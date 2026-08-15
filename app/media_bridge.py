import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from websockets.asyncio.client import connect

from app.config import OPENAI_API_KEY
from app.prompt_builder import build_patient_prompt
from app.realtime_client import REALTIME_URL, build_session_update
from app.scenario_loader import get_scenario


TRANSCRIPT_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "transcripts"
)


def add_transcript_entry(
    entries: list[dict[str, str]],
    speaker: str,
    text: str,
) -> None:
    """Add a completed utterance to the transcript."""

    cleaned_text = text.strip()

    if not cleaned_text:
        return

    entries.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "speaker": speaker,
            "text": cleaned_text,
        }
    )


def save_transcript(
    scenario_id: str,
    call_sid: str | None,
    entries: list[dict[str, str]],
) -> None:
    """Save human-readable and structured transcripts."""

    TRANSCRIPT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    safe_call_sid = call_sid or "unknown-call"
    file_stem = f"{scenario_id}-{safe_call_sid}"

    json_path = TRANSCRIPT_DIRECTORY / f"{file_stem}.json"
    text_path = TRANSCRIPT_DIRECTORY / f"{file_stem}.txt"

    structured_transcript: dict[str, Any] = {
        "scenario_id": scenario_id,
        "call_sid": call_sid,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "turns": entries,
    }

    json_path.write_text(
        json.dumps(structured_transcript, indent=2),
        encoding="utf-8",
    )

    text_lines = [
        f"Scenario: {scenario_id}",
        f"Call SID: {safe_call_sid}",
        "",
    ]

    for entry in entries:
        text_lines.append(
            f"[{entry['timestamp']}] "
            f"{entry['speaker']}: {entry['text']}"
        )

    text_path.write_text(
        "\n".join(text_lines) + "\n",
        encoding="utf-8",
    )

    print(f"Transcript saved to {text_path}")


async def handle_media_stream(
    twilio_socket: WebSocket,
) -> None:
    """Relay audio between Twilio and OpenAI Realtime."""

    await twilio_socket.accept()

    stream_sid: str | None = None
    call_sid: str | None = None
    scenario_id = "call-01"
    transcript_entries: list[dict[str, str]] = []

    try:
        # Wait for Twilio's start event before opening the AI session.
        while True:
            message = await twilio_socket.receive_json()
            event_type = message.get("event")

            if event_type == "connected":
                print("Twilio media connection established")

            elif event_type == "start":
                start_data = message.get("start", {})
                stream_sid = start_data.get("streamSid")
                call_sid = start_data.get("callSid")

                parameters = start_data.get(
                    "customParameters",
                    {},
                )
                scenario_id = parameters.get(
                    "scenario_id",
                    "call-01",
                )
                break

        scenario = get_scenario(scenario_id)
        patient_prompt = build_patient_prompt(scenario)

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Safety-Identifier": f"pgai-{scenario_id}",
        }

        async with connect(
            REALTIME_URL,
            additional_headers=headers,
            max_size=None,
        ) as openai_socket:
            await openai_socket.send(
                json.dumps(
                    build_session_update(patient_prompt)
                )
            )

            print(f"OpenAI session started for {scenario_id}")

            async def twilio_to_openai() -> None:
                """Forward the practice agent audio to OpenAI."""

                while True:
                    message = await twilio_socket.receive_json()
                    event_type = message.get("event")

                    if event_type == "media":
                        payload = message["media"]["payload"]

                        await openai_socket.send(
                            json.dumps(
                                {
                                    "type": (
                                        "input_audio_buffer.append"
                                    ),
                                    "audio": payload,
                                }
                            )
                        )

                    elif event_type == "stop":
                        print(
                            "Twilio stream stopped: "
                            f"{stream_sid}"
                        )
                        return

            async def openai_to_twilio() -> None:
                """Forward patient audio and capture transcripts."""

                async for raw_message in openai_socket:
                    event = json.loads(raw_message)
                    event_type = event.get("type")

                    if event_type == "response.output_audio.delta":
                        await twilio_socket.send_json(
                            {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": event["delta"],
                                },
                            }
                        )

                    elif event_type == (
                        "conversation.item."
                        "input_audio_transcription.completed"
                    ):
                        transcript = event.get("transcript", "")

                        add_transcript_entry(
                            transcript_entries,
                            "PRACTICE_AGENT",
                            transcript,
                        )

                        print(
                            "Practice agent: "
                            f"{transcript}"
                        )

                    elif event_type == (
                        "response.output_audio_transcript.done"
                    ):
                        transcript = event.get("transcript", "")

                        add_transcript_entry(
                            transcript_entries,
                            "PATIENT_BOT",
                            transcript,
                        )

                        print(
                            "Patient bot: "
                            f"{transcript}"
                        )

                    elif event_type == (
                        "input_audio_buffer.speech_started"
                    ):
                        # Stop buffered patient audio when the
                        # practice agent starts speaking.
                        await twilio_socket.send_json(
                            {
                                "event": "clear",
                                "streamSid": stream_sid,
                            }
                        )

                    elif event_type == "error":
                        print(
                            "OpenAI Realtime error: "
                            f"{event}"
                        )

            tasks = {
                asyncio.create_task(twilio_to_openai()),
                asyncio.create_task(openai_to_twilio()),
            }

            completed, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            await asyncio.gather(
                *pending,
                return_exceptions=True,
            )

            for task in completed:
                exception = task.exception()

                if exception:
                    raise exception

    except WebSocketDisconnect:
        print(
            "Twilio WebSocket disconnected: "
            f"{stream_sid}"
        )

    finally:
        save_transcript(
            scenario_id,
            call_sid,
            transcript_entries,
        )
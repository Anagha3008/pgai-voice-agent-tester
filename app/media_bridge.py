import asyncio
import json

from fastapi import WebSocket, WebSocketDisconnect
from websockets.asyncio.client import connect

from app.config import OPENAI_API_KEY
from app.prompt_builder import build_patient_prompt
from app.realtime_client import REALTIME_URL, build_session_update
from app.scenario_loader import get_scenario


async def handle_media_stream(twilio_socket: WebSocket) -> None:
    """Relay audio between Twilio and OpenAI Realtime."""
    await twilio_socket.accept()

    stream_sid: str | None = None
    scenario_id = "call-01"

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

                parameters = start_data.get("customParameters", {})
                scenario_id = parameters.get("scenario_id", "call-01")
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
                json.dumps(build_session_update(patient_prompt))
            )

            print(f"OpenAI session started for {scenario_id}")

            async def twilio_to_openai() -> None:
                """Forward the practice agent's phone audio to OpenAI."""
                while True:
                    message = await twilio_socket.receive_json()
                    event_type = message.get("event")

                    if event_type == "media":
                        payload = message["media"]["payload"]

                        await openai_socket.send(
                            json.dumps(
                                {
                                    "type": "input_audio_buffer.append",
                                    "audio": payload,
                                }
                            )
                        )

                    elif event_type == "stop":
                        print(f"Twilio stream stopped: {stream_sid}")
                        return

            async def openai_to_twilio() -> None:
                """Forward the simulated patient's voice to Twilio."""
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

                    elif event_type == "input_audio_buffer.speech_started":
                        # Stop buffered patient audio when the remote agent speaks.
                        await twilio_socket.send_json(
                            {
                                "event": "clear",
                                "streamSid": stream_sid,
                            }
                        )

                    elif event_type == "error":
                        print(f"OpenAI Realtime error: {event}")

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

            await asyncio.gather(*pending, return_exceptions=True)

            for task in completed:
                exception = task.exception()
                if exception:
                    raise exception

    except WebSocketDisconnect:
        print(f"Twilio WebSocket disconnected: {stream_sid}")
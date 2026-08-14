from typing import Any


REALTIME_MODEL = "gpt-realtime-2.1"
REALTIME_URL = (
    f"wss://api.openai.com/v1/realtime?model={REALTIME_MODEL}"
)


def build_session_update(prompt: str) -> dict[str, Any]:
    """Create the OpenAI Realtime session configuration."""
    return {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "model": REALTIME_MODEL,
            "output_modalities": ["audio"],
            "instructions": prompt,
            "audio": {
                "input": {
                    "format": {
                        "type": "audio/pcmu",
                    },
                    "transcription": {
                        "model": "gpt-live-transcribe",
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 600,
                        "create_response": True,
                        "interrupt_response": True,
                    },
                },
                "output": {
                    "format": {
                        "type": "audio/pcmu",
                    },
                    "voice": "marin",
                },
            },
        },
    }
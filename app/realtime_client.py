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
                        "type": "semantic_vad",
                        "eagerness": "medium",
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
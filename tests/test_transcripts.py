import json

import app.media_bridge as media_bridge


def test_transcript_entry_is_added() -> None:
    entries: list[dict[str, str]] = []

    media_bridge.add_transcript_entry(
        entries,
        "PATIENT_BOT",
        "Hello, I need an appointment.",
    )

    assert len(entries) == 1
    assert entries[0]["speaker"] == "PATIENT_BOT"
    assert entries[0]["text"] == "Hello, I need an appointment."
    assert entries[0]["timestamp"]


def test_transcript_files_are_created(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        media_bridge,
        "TRANSCRIPT_DIRECTORY",
        tmp_path,
    )

    entries = [
        {
            "timestamp": "2026-08-15T12:00:00+00:00",
            "speaker": "PRACTICE_AGENT",
            "text": "How may I help you?",
        },
        {
            "timestamp": "2026-08-15T12:00:01+00:00",
            "speaker": "PATIENT_BOT",
            "text": "I need an appointment.",
        },
    ]

    media_bridge.save_transcript(
        "call-01",
        "CA123",
        entries,
    )

    text_file = tmp_path / "call-01-CA123.txt"
    json_file = tmp_path / "call-01-CA123.json"

    assert text_file.exists()
    assert json_file.exists()

    text_content = text_file.read_text(encoding="utf-8")
    json_content = json.loads(
        json_file.read_text(encoding="utf-8")
    )

    assert "PRACTICE_AGENT: How may I help you?" in text_content
    assert "PATIENT_BOT: I need an appointment." in text_content
    assert json_content["scenario_id"] == "call-01"
    assert len(json_content["turns"]) == 2
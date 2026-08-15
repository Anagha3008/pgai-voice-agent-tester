from pathlib import Path

import pytest

import scripts.download_recordings as downloader


def test_invalid_call_sid_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="must begin with 'CA'",
    ):
        downloader.download_call_recordings(
            call_sid="invalid",
            scenario_id="call-01",
        )


def test_recording_is_downloaded(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class FakeRecording:
        sid = "RE123"
        uri = (
            "/2010-04-01/Accounts/AC123/"
            "Recordings/RE123.json"
        )

    class FakeRecordings:
        def list(self, call_sid: str):
            assert call_sid == "CA123"
            return [FakeRecording()]

    class FakeClient:
        recordings = FakeRecordings()

    class FakeResponse:
        content = b"fake-mp3-data"

        def raise_for_status(self) -> None:
            return None

    def fake_http_get(
        url: str,
        **kwargs,
    ) -> FakeResponse:
        assert url.startswith("https://api.twilio.com/")
        assert url.endswith("RE123.mp3")
        return FakeResponse()

    monkeypatch.setattr(
        downloader,
        "Client",
        lambda *args, **kwargs: FakeClient(),
    )
    monkeypatch.setattr(
        downloader.httpx,
        "get",
        fake_http_get,
    )
    monkeypatch.setattr(
        downloader,
        "RECORDINGS_DIRECTORY",
        tmp_path,
    )

    paths = downloader.download_call_recordings(
        call_sid="CA123",
        scenario_id="call-01",
    )

    assert len(paths) == 1
    assert paths[0].exists()
    assert paths[0].suffix == ".mp3"
    assert paths[0].read_bytes() == b"fake-mp3-data"
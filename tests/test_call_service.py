import pytest

import app.call_service as call_service


def test_build_outbound_call_url(monkeypatch) -> None:
    monkeypatch.setattr(
        call_service,
        "PUBLIC_BASE_URL",
        "https://example.ngrok.app",
    )

    url = call_service.build_outbound_call_url("call-01")

    assert url.endswith("/outbound-call?scenario_id=call-01")


def test_build_outbound_call_url_requires_public_base_url(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        call_service,
        "PUBLIC_BASE_URL",
        "",
    )

    with pytest.raises(
        ValueError,
        match="PUBLIC_BASE_URL is missing",
    ):
        call_service.build_outbound_call_url("call-01")


def test_create_outbound_call_requires_twilio_credentials(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        call_service,
        "PUBLIC_BASE_URL",
        "https://example.ngrok.app",
    )
    monkeypatch.setattr(
        call_service,
        "TWILIO_ACCOUNT_SID",
        "",
    )

    with pytest.raises(
        ValueError,
        match="TWILIO_ACCOUNT_SID is missing",
    ):
        call_service.create_outbound_call("call-01")


def test_wait_for_call_completion_returns_terminal_status(
    monkeypatch,
) -> None:
    statuses = iter(["in-progress", "completed"])

    class FakeCall:
        def __init__(self, status: str) -> None:
            self.status = status

    class FakeCalls:
        def __call__(self, call_sid: str) -> "FakeCalls":
            assert call_sid == "CA123"
            return self

        def fetch(self) -> FakeCall:
            return FakeCall(next(statuses))

    class FakeClient:
        calls = FakeCalls()

    monkeypatch.setattr(
        call_service,
        "get_twilio_client",
        lambda: FakeClient(),
    )
    monkeypatch.setattr(call_service.time, "sleep", lambda _: None)

    status = call_service.wait_for_call_completion("CA123")

    assert status == "completed"

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

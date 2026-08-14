from urllib.parse import urlencode

from twilio.rest import Client

from app.config import (
    PG_TEST_NUMBER,
    PUBLIC_BASE_URL,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    validate_destination_number,
)


def build_outbound_call_url(scenario_id: str) -> str:
    """Build the public TwiML URL used by Twilio."""

    if not PUBLIC_BASE_URL:
        raise ValueError("PUBLIC_BASE_URL is missing from the .env file.")

    base_url = PUBLIC_BASE_URL.rstrip("/")
    query = urlencode({"scenario_id": scenario_id})

    return f"{base_url}/outbound-call?{query}"


def create_outbound_call(scenario_id: str = "call-01") -> str:
    """Call only the approved PGAI assessment number."""

    destination = validate_destination_number(PG_TEST_NUMBER)

    if not TWILIO_ACCOUNT_SID:
        raise ValueError("TWILIO_ACCOUNT_SID is missing.")

    if not TWILIO_AUTH_TOKEN:
        raise ValueError("TWILIO_AUTH_TOKEN is missing.")

    if not TWILIO_PHONE_NUMBER:
        raise ValueError("TWILIO_PHONE_NUMBER is missing.")

    twiml_url = build_outbound_call_url(scenario_id)

    client = Client(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
    )

    call = client.calls.create(
        to=destination,
        from_=TWILIO_PHONE_NUMBER,
        url=twiml_url,
        method="POST",
        record=True,
        recording_channels="dual",
    )

    return call.sid
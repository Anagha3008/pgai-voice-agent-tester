import time
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

ACTIVE_CALL_STATUSES = {"queued", "ringing", "in-progress"}


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


def get_twilio_client() -> Client:
    """Return an authenticated Twilio client."""

    if not TWILIO_ACCOUNT_SID:
        raise ValueError("TWILIO_ACCOUNT_SID is missing.")

    if not TWILIO_AUTH_TOKEN:
        raise ValueError("TWILIO_AUTH_TOKEN is missing.")

    return Client(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
    )


def wait_for_call_completion(
    call_sid: str,
    poll_interval_seconds: int = 5,
    timeout_seconds: int = 300,
) -> str:
    """Poll Twilio until the call reaches a terminal status."""

    client = get_twilio_client()
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        status = client.calls(call_sid).fetch().status

        if status not in ACTIVE_CALL_STATUSES:
            return status

        time.sleep(poll_interval_seconds)

    raise TimeoutError(
        f"Call {call_sid} did not finish within {timeout_seconds} seconds."
    )
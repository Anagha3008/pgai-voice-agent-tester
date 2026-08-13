import os

from dotenv import load_dotenv

load_dotenv()

# The assessment permits calls only to this number.
PG_TEST_NUMBER = "+18054398008"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")


def validate_destination_number(destination: str) -> str:
    """Allow calls only to the Pretty Good AI assessment number."""
    if destination != PG_TEST_NUMBER:
        raise ValueError(
            f"Calls are permitted only to {PG_TEST_NUMBER}. "
            f"Rejected destination: {destination}"
        )

    return destination
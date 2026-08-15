import argparse
from pathlib import Path

import httpx
from twilio.rest import Client

from app.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)


RECORDINGS_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "recordings"
)


def download_call_recordings(
    call_sid: str,
    scenario_id: str,
) -> list[Path]:
    """Download every recording associated with one Twilio call."""

    if not call_sid.startswith("CA"):
        raise ValueError("A Twilio Call SID must begin with 'CA'.")

    client = Client(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
    )

    recordings = client.recordings.list(call_sid=call_sid)

    if not recordings:
        raise ValueError(
            f"No completed recordings found for {call_sid}."
        )

    RECORDINGS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    downloaded_files: list[Path] = []

    for recording in recordings:
        media_path = recording.uri.replace(".json", ".mp3")
        media_url = f"https://api.twilio.com{media_path}"

        response = httpx.get(
            media_url,
            auth=(
                TWILIO_ACCOUNT_SID,
                TWILIO_AUTH_TOKEN,
            ),
            follow_redirects=True,
            timeout=60.0,
        )
        response.raise_for_status()

        output_path = RECORDINGS_DIRECTORY / (
            f"{scenario_id}-{call_sid}-{recording.sid}.mp3"
        )

        output_path.write_bytes(response.content)
        downloaded_files.append(output_path)

        print(f"Saved recording: {output_path}")

    return downloaded_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a Twilio call recording as MP3."
    )
    parser.add_argument(
        "--call-sid",
        required=True,
        help="Twilio Call SID beginning with CA.",
    )
    parser.add_argument(
        "--scenario-id",
        required=True,
        help="Scenario identifier such as call-01.",
    )

    arguments = parser.parse_args()

    download_call_recordings(
        call_sid=arguments.call_sid,
        scenario_id=arguments.scenario_id,
    )


if __name__ == "__main__":
    main()
from pathlib import Path

from app.scenario_loader import load_scenarios


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECORDINGS_DIRECTORY = PROJECT_ROOT / "recordings"
TRANSCRIPTS_DIRECTORY = PROJECT_ROOT / "transcripts"


def find_artifacts(
    directory: Path,
    scenario_id: str,
    extension: str,
) -> list[Path]:
    """Find artifacts whose names begin with a scenario ID."""

    return sorted(
        directory.glob(f"{scenario_id}-*.{extension}")
    )


def validate_submission() -> bool:
    """Check that every scenario has required call artifacts."""

    scenarios = load_scenarios()
    missing_items: list[str] = []

    print(f"Checking {len(scenarios)} scenarios...")

    for scenario in scenarios:
        scenario_id = scenario["id"]

        mp3_files = find_artifacts(
            RECORDINGS_DIRECTORY,
            scenario_id,
            "mp3",
        )
        text_files = find_artifacts(
            TRANSCRIPTS_DIRECTORY,
            scenario_id,
            "txt",
        )
        json_files = find_artifacts(
            TRANSCRIPTS_DIRECTORY,
            scenario_id,
            "json",
        )

        if not mp3_files:
            missing_items.append(
                f"{scenario_id}: MP3 recording"
            )

        if not text_files:
            missing_items.append(
                f"{scenario_id}: TXT transcript"
            )

        if not json_files:
            missing_items.append(
                f"{scenario_id}: JSON transcript"
            )

    if missing_items:
        print("\nSubmission is incomplete:")

        for item in missing_items:
            print(f"- {item}")

        return False

    print(
        "\nSubmission artifacts are complete for all scenarios."
    )
    return True


def main() -> None:
    if not validate_submission():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
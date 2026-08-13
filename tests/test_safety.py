import pytest

from app.config import PG_TEST_NUMBER, validate_destination_number
from app.prompt_builder import build_patient_prompt
from app.scenario_loader import get_scenario, load_scenarios


def test_approved_destination_is_allowed():
    assert validate_destination_number(PG_TEST_NUMBER) == PG_TEST_NUMBER


def test_unapproved_destination_is_blocked():
    with pytest.raises(ValueError):
        validate_destination_number("+13125550100")


def test_scenarios_load_successfully():
    scenarios = load_scenarios()

    assert len(scenarios) >= 1
    assert scenarios[0]["id"] == "call-01"


def test_known_scenario_can_be_found():
    scenario = get_scenario("call-01")

    assert scenario["patient"]["name"] == "Maya Thompson"


def test_unknown_scenario_is_rejected():
    with pytest.raises(ValueError):
        get_scenario("missing-scenario")


def test_prompt_contains_required_information():
    scenario = get_scenario("call-01")
    prompt = build_patient_prompt(scenario)

    assert "Maya Thompson" in prompt
    assert "Schedule an annual physical" in prompt
    assert "Never reveal that you are an AI" in prompt
import json

import pytest

from services.storage_service import (
    add_recently_viewed,
    load_user_state,
    remove_meal_plan_entry,
    save_user_state,
    set_meal_plan_entry,
    toggle_favorite,
)


def test_favorites_persist_and_toggle_off(tmp_path):
    state_path = tmp_path / "user_state.json"

    assert toggle_favorite("masala-dosa", state_path) is True
    assert load_user_state(state_path)["favorites"] == ["masala-dosa"]
    assert toggle_favorite("masala-dosa", state_path) is False
    assert load_user_state(state_path)["favorites"] == []


def test_meal_plan_add_remove_and_recent_history_persist(tmp_path):
    state_path = tmp_path / "user_state.json"

    set_meal_plan_entry("2026-11-27", "Dinner", "dal-tadka", state_path)
    add_recently_viewed("dal-tadka", state_path)
    assert load_user_state(state_path)["meal_plan"]["2026-11-27"]["Dinner"] == "dal-tadka"
    assert load_user_state(state_path)["recently_viewed"] == ["dal-tadka"]

    remove_meal_plan_entry("2026-11-27", "Dinner", state_path)
    assert load_user_state(state_path)["meal_plan"] == {}


def test_meal_planner_rejects_unknown_slots(tmp_path):
    with pytest.raises(ValueError, match="Breakfast, Lunch, or Dinner"):
        set_meal_plan_entry("2026-11-27", "Snack", "fresh-guacamole", tmp_path / "state.json")


def test_saved_state_round_trips_as_valid_json(tmp_path):
    state_path = tmp_path / "nested" / "state.json"
    saved = save_user_state(
        {
            "favorites": ["dal-tadka", "dal-tadka"],
            "meal_plan": {},
            "recently_viewed": [],
        },
        state_path,
    )

    assert state_path.is_file()
    assert json.loads(state_path.read_text(encoding="utf-8")) == saved
    assert saved["favorites"] == ["dal-tadka"]

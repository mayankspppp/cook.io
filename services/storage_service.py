"""Atomic JSON persistence for favorites, meal plans, and recipe history."""

import json
import os
import tempfile
from pathlib import Path
from threading import RLock


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "data" / "user_state.json"
_WRITE_LOCK = RLock()
EMPTY_STATE = {"favorites": [], "meal_plan": {}, "recently_viewed": []}


def load_user_state(path=STATE_PATH):
    """Load saved local state, returning an empty state for a first-time user."""
    if not path.exists():
        return {"favorites": [], "meal_plan": {}, "recently_viewed": []}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Unable to read saved Cook.io data at {path}: {error}") from error
    if not isinstance(state, dict):
        raise ValueError("Saved Cook.io data must be a JSON object.")
    normalized = {
        "favorites": state.get("favorites", []),
        "meal_plan": state.get("meal_plan", {}),
        "recently_viewed": state.get("recently_viewed", []),
    }
    if not all(isinstance(normalized[key], expected) for key, expected in (
        ("favorites", list),
        ("meal_plan", dict),
        ("recently_viewed", list),
    )):
        raise ValueError("Saved favorites, meal plan, or history has an invalid shape.")
    return normalized


def save_user_state(state, path=STATE_PATH):
    """Atomically persist state to a local JSON file."""
    if not isinstance(state, dict):
        raise ValueError("Cook.io state must be a dictionary.")
    normalized = {
        "favorites": list(dict.fromkeys(state.get("favorites", []))),
        "meal_plan": state.get("meal_plan", {}),
        "recently_viewed": list(dict.fromkeys(state.get("recently_viewed", [])))[:12],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    with _WRITE_LOCK:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(path.parent),
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(normalized, temporary_file, indent=2, ensure_ascii=False)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(str(temporary_path), str(path))
        except OSError as error:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink()
            raise RuntimeError(f"Unable to save Cook.io data at {path}: {error}") from error
    return normalized


def toggle_favorite(recipe_id, path=STATE_PATH):
    state = load_user_state(path)
    favorites = set(state["favorites"])
    if recipe_id in favorites:
        favorites.remove(recipe_id)
        is_favorite = False
    else:
        favorites.add(recipe_id)
        is_favorite = True
    state["favorites"] = sorted(favorites)
    save_user_state(state, path)
    return is_favorite


def set_meal_plan_entry(day, meal, recipe_id, path=STATE_PATH):
    if meal not in {"Breakfast", "Lunch", "Dinner"}:
        raise ValueError("Meal slot must be Breakfast, Lunch, or Dinner.")
    state = load_user_state(path)
    state["meal_plan"].setdefault(day, {})[meal] = recipe_id
    save_user_state(state, path)
    return state


def remove_meal_plan_entry(day, meal, path=STATE_PATH):
    state = load_user_state(path)
    state["meal_plan"].get(day, {}).pop(meal, None)
    if day in state["meal_plan"] and not state["meal_plan"][day]:
        del state["meal_plan"][day]
    save_user_state(state, path)
    return state


def add_recently_viewed(recipe_id, path=STATE_PATH):
    state = load_user_state(path)
    state["recently_viewed"] = [recipe_id] + [
        item for item in state["recently_viewed"] if item != recipe_id
    ]
    save_user_state(state, path)
    return state

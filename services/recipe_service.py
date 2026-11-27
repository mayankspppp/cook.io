"""Local recipe catalogue loading, search, filtering, and serving calculations."""

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "data" / "recipes.json"
REQUIRED_FIELDS = {
    "id",
    "name",
    "description",
    "image",
    "cuisine",
    "category",
    "dietary_type",
    "prep_time",
    "cook_time",
    "total_time",
    "difficulty",
    "servings",
    "ingredients",
    "instructions",
    "nutrition_per_serving_estimate",
    "tags",
    "popularity",
}


def load_recipes(path: Path = CATALOGUE_PATH) -> List[dict]:
    """Load and validate the on-disk JSON catalogue."""
    try:
        recipes = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise RuntimeError(f"Unable to read recipe catalogue at {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Recipe catalogue contains invalid JSON: {error}") from error

    if not isinstance(recipes, list):
        raise ValueError("Recipe catalogue must be a JSON list.")

    identifiers = set()
    for recipe in recipes:
        if not isinstance(recipe, dict):
            raise ValueError("Every recipe must be a JSON object.")
        missing_fields = REQUIRED_FIELDS.difference(recipe)
        if missing_fields:
            raise ValueError(
                f"Recipe is missing required fields: {', '.join(sorted(missing_fields))}"
            )
        if recipe["id"] in identifiers:
            raise ValueError(f"Duplicate recipe ID: {recipe['id']}")
        identifiers.add(recipe["id"])
        if recipe["servings"] <= 0 or recipe["total_time"] != recipe["prep_time"] + recipe["cook_time"]:
            raise ValueError(f"Recipe has invalid time or servings data: {recipe['id']}")
        if not recipe["ingredients"] or not recipe["instructions"]:
            raise ValueError(f"Recipe needs ingredients and steps: {recipe['id']}")
    return recipes


def filter_recipes(
    recipes: Iterable[dict],
    search: str = "",
    cuisine: str = "All",
    category: str = "All",
    dietary_type: str = "All",
    max_minutes: Optional[int] = None,
    difficulty: str = "All",
    sort_by: str = "Popularity",
) -> List[dict]:
    """Apply all active search and filter conditions together."""
    terms = [term for term in search.casefold().split() if term]
    results = []
    for recipe in recipes:
        searchable_text = " ".join(
            [
                recipe["name"],
                recipe["description"],
                recipe["cuisine"],
                recipe["category"],
                recipe["dietary_type"],
                " ".join(recipe["tags"]),
                " ".join(item["name"] for item in recipe["ingredients"]),
            ]
        ).casefold()
        if terms and not all(term in searchable_text for term in terms):
            continue
        if cuisine != "All" and recipe["cuisine"] != cuisine:
            continue
        if category != "All" and recipe["category"] != category:
            continue
        if dietary_type != "All" and recipe["dietary_type"] != dietary_type:
            continue
        if max_minutes is not None and recipe["total_time"] > max_minutes:
            continue
        if difficulty != "All" and recipe["difficulty"] != difficulty:
            continue
        results.append(recipe)

    sort_keys = {
        "Popularity": lambda recipe: (-recipe["popularity"], recipe["name"].casefold()),
        "Quickest": lambda recipe: (recipe["total_time"], recipe["name"].casefold()),
        "A–Z": lambda recipe: recipe["name"].casefold(),
    }
    return sorted(results, key=sort_keys.get(sort_by, sort_keys["Popularity"]))


def scale_ingredient_amount(amount: float, base_servings: int, desired_servings: int) -> float:
    """Scale a numeric ingredient quantity to a different serving count."""
    if base_servings <= 0 or desired_servings <= 0:
        raise ValueError("Serving counts must be greater than zero.")
    return amount * desired_servings / base_servings


def format_quantity(amount: float) -> str:
    """Format quantities with common kitchen fractions when possible."""
    from fractions import Fraction

    value = Fraction(amount).limit_denominator(8)
    if abs(float(value) - amount) > 0.03:
        return f"{amount:.2f}".rstrip("0").rstrip(".")
    whole, numerator = divmod(value.numerator, value.denominator)
    if numerator == 0:
        return str(whole)
    fraction = f"{numerator}/{value.denominator}"
    return f"{whole} {fraction}" if whole else fraction


def format_ingredient(ingredient: dict, base_servings: int, desired_servings: int) -> str:
    amount = scale_ingredient_amount(
        ingredient["amount"], base_servings, desired_servings
    )
    unit = f" {ingredient['unit']}" if ingredient["unit"] else ""
    return f"{format_quantity(amount)}{unit} {ingredient['name']}"

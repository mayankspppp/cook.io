import json
from pathlib import Path

from PIL import Image

from scripts.generate_recipes import build_recipes
from services.recipe_service import (
    filter_recipes,
    format_ingredient,
    load_recipes,
    scale_ingredient_amount,
)


ROOT = Path(__file__).resolve().parents[1]


def test_catalogue_has_complete_unique_recipes_and_local_photos():
    recipes = load_recipes()

    assert len(recipes) >= 50
    assert len({recipe["id"] for recipe in recipes}) == len(recipes)
    for recipe in recipes:
        image_path = ROOT / recipe["image"]
        assert image_path.is_file()
        with Image.open(image_path) as image:
            image.verify()
        assert len(recipe["ingredients"]) >= 3
        assert len(recipe["instructions"]) >= 3


def test_generator_creates_valid_json_recipe_records():
    recipes = build_recipes()
    decoded = json.loads(json.dumps(recipes))

    assert len(decoded) >= 50
    assert len({recipe["id"] for recipe in decoded}) == len(decoded)
    assert all(recipe["nutrition_per_serving_estimate"]["calories"] > 0 for recipe in decoded)


def test_search_matches_recipe_names_and_ingredient_names():
    recipes = load_recipes()

    names = filter_recipes(recipes, search="miso ramen")
    ingredients = filter_recipes(recipes, search="chickpeas")

    assert [recipe["id"] for recipe in names] == ["miso-ramen"]
    assert ingredients
    assert all(
        "chickpea" in " ".join(item["name"] for item in recipe["ingredients"]).casefold()
        for recipe in ingredients
    )


def test_search_and_all_active_filters_are_intersected_and_sorted():
    recipes = load_recipes()
    results = filter_recipes(
        recipes,
        search="tomato",
        cuisine="Indian",
        category="Dinner",
        dietary_type="Vegetarian",
        max_minutes=60,
        difficulty="Moderate",
        sort_by="Quickest",
    )

    assert results
    assert all(
        recipe["cuisine"] == "Indian"
        and recipe["category"] == "Dinner"
        and recipe["dietary_type"] == "Vegetarian"
        and recipe["total_time"] <= 60
        and recipe["difficulty"] == "Moderate"
        and "tomato" in " ".join(
            [recipe["name"], *(item["name"] for item in recipe["ingredients"])]
        ).casefold()
        for recipe in results
    )
    assert [recipe["total_time"] for recipe in results] == sorted(
        recipe["total_time"] for recipe in results
    )


def test_filters_return_an_empty_list_when_the_combination_has_no_match():
    results = filter_recipes(
        load_recipes(),
        cuisine="Japanese",
        category="Dessert",
        dietary_type="Vegan",
    )

    assert results == []


def test_serving_calculator_scales_and_formats_fractions():
    assert scale_ingredient_amount(2, 4, 3) == 1.5
    assert format_ingredient(
        {"amount": 2, "unit": "cups", "name": "chickpeas"},
        base_servings=4,
        desired_servings=3,
    ) == "1 1/2 cups chickpeas"


def test_serving_calculator_rejects_non_positive_servings():
    try:
        scale_ingredient_amount(1, 0, 2)
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError("Invalid serving count was accepted.")

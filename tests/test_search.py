from services.recipe_service import filter_recipes, load_recipes


def test_multiple_filter_combinations_preserve_only_matching_recipes():
    recipes = load_recipes()
    results = filter_recipes(
        recipes,
        cuisine="Indian",
        category="Dinner",
        dietary_type="Vegan",
        max_minutes=60,
    )

    assert results
    assert all(
        recipe["cuisine"] == "Indian"
        and recipe["category"] == "Dinner"
        and recipe["dietary_type"] == "Vegan"
        and recipe["total_time"] <= 60
        for recipe in results
    )


def test_popularity_sort_uses_curated_popularity_scores():
    results = filter_recipes(load_recipes(), sort_by="Popularity")

    assert [recipe["popularity"] for recipe in results] == sorted(
        (recipe["popularity"] for recipe in results), reverse=True
    )

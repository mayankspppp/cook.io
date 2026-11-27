"""Reusable Streamlit recipe-card rendering."""

from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
FALLBACK_IMAGE = ROOT / "assets" / "img" / "recipe.jpg"


def render_recipe_card(recipe, is_favorite, on_open, on_toggle_favorite, key_prefix):
    image_path = ROOT / recipe["image"]
    if not image_path.is_file():
        image_path = FALLBACK_IMAGE

    with st.container(border=True, key=f"recipe-card-{key_prefix}-{recipe['id']}"):
        st.image(str(image_path), width="stretch")
        st.caption(f"{recipe['cuisine']}  ·  {recipe['category']}")
        st.markdown(f"#### {recipe['name']}")
        st.markdown(
            f"`{recipe['total_time']} min`  ·  `{recipe['difficulty']}`  ·  "
            f"`{recipe['dietary_type']}`"
        )
        calories = recipe["nutrition_per_serving_estimate"]["calories"]
        st.caption(f"About {calories} kcal per serving")
        if st.button(
            "♥ Saved" if is_favorite else "♡ Save",
            key=f"favorite-{key_prefix}-{recipe['id']}",
            width="stretch",
            help="Remove this recipe from favorites" if is_favorite else "Save this recipe",
        ):
            on_toggle_favorite(recipe["id"])
        if st.button(
            "View recipe",
            key=f"open-{key_prefix}-{recipe['id']}",
            width="stretch",
            type="primary",
        ):
            on_open(recipe["id"])


def render_recipe_grid(
    recipes, favorite_ids, on_open, on_toggle_favorite, key_prefix, columns=3
):
    if not recipes:
        st.info("No recipes found. Try changing your search or filters.")
        return
    grid_columns = st.columns(min(columns, len(recipes)), gap="medium")
    for index, recipe in enumerate(recipes):
        with grid_columns[index % len(grid_columns)]:
            render_recipe_card(
                recipe,
                recipe["id"] in favorite_ids,
                on_open,
                on_toggle_favorite,
                key_prefix,
            )

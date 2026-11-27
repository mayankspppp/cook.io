"""Cook.io: a local-first recipe discovery app built with Streamlit."""

import base64
import random
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

import pandas as pd
import plotly.express as px
import streamlit as st

from components.recipe_card import render_recipe_grid
from services.recipe_service import filter_recipes, format_ingredient, load_recipes
from services.storage_service import (
    add_recently_viewed,
    load_user_state,
    remove_meal_plan_entry,
    save_user_state,
    set_meal_plan_entry,
    toggle_favorite,
)


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SECTIONS = [
    "Home",
    "Explore Recipes",
    "Categories",
    "Favorites",
    "Meal Planner",
    "About Cook.io",
]

st.set_page_config(
    page_title="Cook.io · Find something delicious",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def get_recipes():
    return load_recipes()


def _show_error(error):
    st.error(f"Cook.io could not finish that action: {error}")
    st.stop()


try:
    recipes = get_recipes()
    user_state = load_user_state()
except (RuntimeError, ValueError) as error:
    st.error(str(error))
    st.stop()


def _load_styles():
    stylesheet = ASSETS / "styles.css"
    if stylesheet.is_file():
        st.markdown(f"<style>{stylesheet.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    dark_mode = st.session_state.get("dark_mode", False)
    if dark_mode:
        st.markdown(
            """
            <style>
            .stApp { background: #171a17; color: #f2f0e9; }
            [data-testid="stSidebar"] { background: #20251f; }
            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] h1,
            [data-testid="stMarkdownContainer"] h2,
            [data-testid="stMarkdownContainer"] h3,
            label, small { color: #eeeae1; }
            [data-testid="stCaptionContainer"] { color: #b7c2b9; }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
            [data-testid="stSidebar"] [data-testid="stRadio"] p { color: #e3e7e1; }
            [class*="st-key-recipe-card-"] { background: #222722; border-color: #3a443b; }
            [data-testid="stTextInput"] input,
            [data-testid="stSelectbox"] [role="combobox"],
            [data-testid="stDateInput"] input { background: #252a25; color: #f2f0e9; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def _open_recipe(recipe_id):
    st.query_params["recipe"] = recipe_id
    st.rerun()


def _go_to_page(page):
    st.session_state["navigation"] = page


def _search_from_home():
    st.session_state["explore_search"] = st.session_state.get("home_search", "")
    _go_to_page("Explore Recipes")


def _go_to_cuisine(cuisine):
    st.session_state["explore_cuisine"] = cuisine
    _go_to_page("Explore Recipes")


def _go_to_category(category):
    st.session_state["explore_category"] = category
    _go_to_page("Explore Recipes")


def _close_recipe():
    st.query_params.clear()
    st.rerun()


def _toggle_favorite(recipe_id):
    try:
        toggle_favorite(recipe_id)
        st.rerun()
    except (RuntimeError, ValueError) as error:
        _show_error(error)


def _recipe_by_id(recipe_id):
    return next((item for item in recipes if item["id"] == recipe_id), None)


def _recipe_card_grid(items, favorite_ids, key_prefix, columns=3):
    render_recipe_grid(
        items,
        favorite_ids,
        on_open=_open_recipe,
        on_toggle_favorite=_toggle_favorite,
        key_prefix=key_prefix,
        columns=columns,
    )


def _page_header(eyebrow, title, description):
    st.caption(eyebrow.upper())
    st.title(title)
    st.write(description)


def _render_home(favorite_ids):
    hero_path = ASSETS / "img" / "detail-banner.jpg"
    if hero_path.is_file():
        hero_data = base64.b64encode(hero_path.read_bytes()).decode("ascii")
        st.markdown(
            f"""
            <section class="cook-hero" style="background-image:
                linear-gradient(90deg, rgba(22, 30, 25, .90), rgba(22, 30, 25, .30)),
                url('data:image/jpeg;base64,{hero_data}')">
              <span class="hero-kicker">GOOD FOOD, MORE OFTEN</span>
              <h1>Find your next<br>favorite.</h1>
              <p>Thoughtful recipes for everyday cooking, gathered in one place.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("What sounds good today?")
    st.text_input(
        "Search recipes or ingredients",
        placeholder="Try chickpeas, tomato, or lemon chicken",
        label_visibility="collapsed",
        key="home_search",
    )
    search_button_column, random_column = st.columns(2)
    with search_button_column:
        st.button(
            "Find recipes",
            type="primary",
            width="stretch",
            on_click=_search_from_home,
        )
    with random_column:
        if st.button("Surprise me", width="stretch"):
            _open_recipe(random.choice(recipes)["id"])

    st.markdown(
        f"""
        <div class="stat-strip">
          <div><strong>{len(recipes)}+</strong><span>home-tested ideas</span></div>
          <div><strong>{len({item["cuisine"] for item in recipes})}</strong><span>global cuisines</span></div>
          <div><strong>01</strong><span>good meal, any day</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Popular right now")
    _recipe_card_grid(
        sorted(recipes, key=lambda item: item["popularity"], reverse=True)[:3],
        favorite_ids,
        key_prefix="home-popular",
    )

    cuisine_names = sorted({item["cuisine"] for item in recipes})
    st.subheader("A taste of somewhere new")
    cuisine_columns = st.columns(min(5, len(cuisine_names)))
    for index, cuisine in enumerate(cuisine_names[:5]):
        with cuisine_columns[index]:
            st.button(
                f"Explore {cuisine}",
                key=f"home-cuisine-{cuisine}",
                width="stretch",
                on_click=_go_to_cuisine,
                args=(cuisine,),
            )

    st.subheader("Recently added")
    _recipe_card_grid(recipes[-3:], favorite_ids, key_prefix="home-recently-added")

    recently_viewed = [
        item for recipe_id in user_state["recently_viewed"]
        if (item := _recipe_by_id(recipe_id)) is not None
    ]
    if recently_viewed:
        st.subheader("Picked up where you left off")
        _recipe_card_grid(recently_viewed[:3], favorite_ids, key_prefix="home-history")


def _render_explore(favorite_ids):
    _page_header(
        "The Cook.io collection",
        "Explore recipes",
        "Search by dish, cuisine, or ingredient, then layer filters to find your fit.",
    )
    cuisines = ["All"] + sorted({item["cuisine"] for item in recipes})
    categories = ["All"] + sorted({item["category"] for item in recipes})
    diets = ["All"] + sorted({item["dietary_type"] for item in recipes})
    difficulties = ["All", "Easy", "Moderate", "Advanced"]
    if st.session_state.get("explore_cuisine") not in cuisines:
        st.session_state["explore_cuisine"] = "All"

    filter_column, results_column = st.columns([1, 2.8], gap="large")
    with filter_column:
        st.markdown("### Refine your search")
        if st.button("Clear filters", width="stretch"):
            for key, value in (
                ("explore_search", ""),
                ("explore_cuisine", "All"),
                ("explore_category", "All"),
                ("explore_diet", "All"),
                ("explore_difficulty", "All"),
                ("explore_max_minutes", None),
                ("explore_sort", "Popularity"),
                ("explore_page_size", 12),
            ):
                st.session_state[key] = value
            st.rerun()
        st.text_input("Recipe or ingredient", key="explore_search")
        st.selectbox("Cuisine", cuisines, key="explore_cuisine")
        st.selectbox("Category", categories, key="explore_category")
        st.selectbox("Dietary preference", diets, key="explore_diet")
        st.selectbox("Difficulty", difficulties, key="explore_difficulty")
        st.selectbox(
            "Maximum total time",
            [None, 15, 30, 45, 60, 90, 120],
            format_func=lambda value: "Any time" if value is None else f"Up to {value} min",
            key="explore_max_minutes",
        )
        st.selectbox(
            "Sort results",
            ["Popularity", "Quickest", "A–Z"],
            key="explore_sort",
        )
        if st.button("Reset saved app data", width="stretch"):
            st.session_state["confirm_reset"] = True
        if st.session_state.get("confirm_reset"):
            st.warning("This removes saved favorites, meal plans, and recent history.")
            if st.button("Confirm reset", type="primary", key="confirm-reset-data"):
                try:
                    save_user_state({"favorites": [], "meal_plan": {}, "recently_viewed": []})
                    st.session_state["confirm_reset"] = False
                    st.rerun()
                except (RuntimeError, ValueError) as error:
                    _show_error(error)

    try:
        results = filter_recipes(
            recipes,
            search=st.session_state.get("explore_search", ""),
            cuisine=st.session_state.get("explore_cuisine", "All"),
            category=st.session_state.get("explore_category", "All"),
            dietary_type=st.session_state.get("explore_diet", "All"),
            max_minutes=st.session_state.get("explore_max_minutes"),
            difficulty=st.session_state.get("explore_difficulty", "All"),
            sort_by=st.session_state.get("explore_sort", "Popularity"),
        )
    except (KeyError, TypeError, ValueError) as error:
        st.error(f"Could not filter the recipe collection: {error}")
        return

    with results_column:
        count_label = "recipe" if len(results) == 1 else "recipes"
        st.markdown(f"### {len(results)} {count_label} to explore")
        page_size = st.session_state.setdefault("explore_page_size", 12)
        _recipe_card_grid(results[:page_size], favorite_ids, key_prefix="explore-results")
        if len(results) > page_size and st.button("Show more recipes", width="stretch"):
            st.session_state["explore_page_size"] = page_size + 12
            st.rerun()


def _render_categories(favorite_ids):
    _page_header(
        "Find your flavor",
        "Browse by cuisine",
        "From comforting classics to fresh, quick meals, choose a starting point.",
    )
    cuisines = sorted({item["cuisine"] for item in recipes})
    columns = st.columns(4)
    for index, cuisine in enumerate(cuisines):
        matching = [item for item in recipes if item["cuisine"] == cuisine]
        with columns[index % len(columns)]:
            image_path = ROOT / matching[0]["image"]
            if not image_path.is_file():
                image_path = ASSETS / "img" / "recipe.jpg"
            st.image(str(image_path), width="stretch")
            st.markdown(f"#### {cuisine}")
            st.caption(f"{len(matching)} recipes in this collection")
            st.button(
                f"Browse {cuisine}",
                key=f"category-{cuisine}",
                width="stretch",
                on_click=_go_to_cuisine,
                args=(cuisine,),
            )

    st.subheader("Browse by meal")
    meal_columns = st.columns(4)
    for index, category in enumerate(sorted({item["category"] for item in recipes})):
        with meal_columns[index % len(meal_columns)]:
            st.button(
                f"{category} · {sum(item['category'] == category for item in recipes)}",
                key=f"category-meal-{category}",
                width="stretch",
                on_click=_go_to_category,
                args=(category,),
            )

    st.subheader("Popular picks")
    _recipe_card_grid(
        sorted(recipes, key=lambda item: item["popularity"], reverse=True)[:3],
        favorite_ids,
        key_prefix="categories-popular",
    )


def _render_favorites(favorite_ids):
    _page_header(
        "Your personal recipe box",
        "Favorites",
        "Keep the dishes you want to make again close at hand.",
    )
    favorites = [item for item in recipes if item["id"] in favorite_ids]
    if favorites:
        _recipe_card_grid(favorites, favorite_ids, key_prefix="favorites")
    else:
        st.info("Your recipe box is empty. Save a recipe to see it here.")
        st.button(
            "Explore the collection",
            type="primary",
            on_click=_go_to_page,
            args=("Explore Recipes",),
        )


def _render_meal_planner(favorite_ids):
    _page_header(
        "Make the week feel easier",
        "Meal planner",
        "Save a breakfast, lunch, and dinner for each day. Your plan stays on this device.",
    )
    selected_day = st.date_input("Plan for", value=date.today(), key="planner_date")
    day_key = selected_day.isoformat()
    day_plan = user_state["meal_plan"].get(day_key, {})
    slot_columns = st.columns(3)

    for column, meal in zip(slot_columns, ("Breakfast", "Lunch", "Dinner")):
        with column:
            st.markdown(f"### {meal}")
            current_id = day_plan.get(meal)
            current_recipe = _recipe_by_id(current_id) if current_id else None
            if current_recipe:
                st.image(str(ROOT / current_recipe["image"]), width="stretch")
                st.write(current_recipe["name"])
                if st.button("Remove from plan", key=f"remove-plan-{day_key}-{meal}"):
                    try:
                        remove_meal_plan_entry(day_key, meal)
                        st.rerun()
                    except (RuntimeError, ValueError) as error:
                        _show_error(error)

            choices = {"Choose a recipe": ""}
            choices.update(
                {
                    item["name"]: item["id"]
                    for item in recipes
                    if item["category"] == meal
                }
            )
            st.selectbox(
                f"Choose {meal.lower()}",
                list(choices),
                key=f"planner-choice-{day_key}-{meal}",
            )
            if st.button("Add to plan", key=f"add-plan-{day_key}-{meal}", type="primary"):
                choice = st.session_state[f"planner-choice-{day_key}-{meal}"]
                recipe_id = choices[choice]
                if not recipe_id:
                    st.warning("Choose a recipe first.")
                else:
                    try:
                        set_meal_plan_entry(day_key, meal, recipe_id)
                        st.rerun()
                    except (RuntimeError, ValueError) as error:
                        _show_error(error)

    if not any(day_plan.values()):
        st.info("Choose a dish for each meal, then add it to your plan.")


def _render_about():
    _page_header(
        "A little more about us",
        "Cooking should feel good.",
        "Cook.io is a calm, practical place to discover what to cook next.",
    )
    st.markdown(
        """
        Cook.io brings a hand-curated collection of Indian and international
        favorites together with useful planning tools. Recipes are stored
        locally in an editable JSON catalogue; no account, paid API, or API key
        is needed.

        **Built for real kitchens**
        - Search dish names, cuisines, tags, and ingredients.
        - Narrow the collection with filters that work together.
        - Scale ingredient quantities when you change servings.
        - Keep favorites, recent recipes, and meal plans on this device.

        **Nutrition note**
        Nutrition values are rounded estimates per serving, not laboratory
        measurements. Ingredients, brands, portions, and preparation methods
        can change the final values. Use product labels or a qualified
        professional for dietary or medical decisions.

        **Photography**
        The original Cook.io hero, logo, and recipe assets are retained.
        Additional food photographs are bundled locally from Unsplash so the
        catalogue does not depend on image APIs at runtime.
        """
    )


def _render_detail(recipe, favorite_ids):
    if recipe["id"] not in user_state["recently_viewed"]:
        try:
            add_recently_viewed(recipe["id"])
        except (RuntimeError, ValueError) as error:
            st.warning(f"Could not update recent history: {error}")

    if st.button("← Back to Cook.io"):
        _close_recipe()

    image_path = ROOT / recipe["image"]
    if not image_path.is_file():
        image_path = ASSETS / "img" / "recipe.jpg"
    image_column, detail_column = st.columns([1.1, 1], gap="large")
    with image_column:
        st.image(str(image_path), width="stretch")
    with detail_column:
        st.caption(f"{recipe['cuisine']}  ·  {recipe['category']}")
        st.title(recipe["name"])
        st.write(recipe["description"])
        st.markdown(
            f"**{recipe['dietary_type']}**  ·  {recipe['difficulty']}  ·  "
            f"{recipe['prep_time']} min prep  ·  {recipe['cook_time']} min cook"
        )
        st.metric("Total time", f"{recipe['total_time']} min")
        if st.button(
            "♥ Remove from favorites" if recipe["id"] in favorite_ids else "♡ Save to favorites",
            type="primary",
            key=f"detail-favorite-{recipe['id']}",
        ):
            _toggle_favorite(recipe["id"])
        st.caption("Share this recipe by copying the page URL; its recipe ID is in the address.")
        context = getattr(st, "context", None)
        current_url = getattr(context, "url", "")
        if current_url:
            parsed_url = urlsplit(current_url)
            share_url = urlunsplit(
                (parsed_url.scheme, parsed_url.netloc, parsed_url.path, f"recipe={quote(recipe['id'])}", "")
            )
            st.code(share_url, language=None)
        else:
            st.code(f"?recipe={quote(recipe['id'])}", language=None)

    st.divider()
    ingredients_column, steps_column = st.columns([1, 1.25], gap="large")
    with ingredients_column:
        st.subheader("Ingredients")
        servings = st.number_input(
            "Servings",
            min_value=1,
            max_value=24,
            value=recipe["servings"],
            step=1,
            key=f"servings-{recipe['id']}",
        )
        for ingredient in recipe["ingredients"]:
            st.markdown(
                f"- {format_ingredient(ingredient, recipe['servings'], servings)}"
            )
    with steps_column:
        st.subheader("Method")
        for index, instruction in enumerate(recipe["instructions"], start=1):
            st.markdown(f"**{index}.** {instruction}")

    nutrition = recipe["nutrition_per_serving_estimate"]
    st.divider()
    st.subheader("Estimated nutrition · per serving")
    metric_columns = st.columns(4)
    metrics = [
        ("Energy", f"{nutrition['calories']} kcal"),
        ("Protein", f"{nutrition['protein_g']} g"),
        ("Carbohydrates", f"{nutrition['carbohydrates_g']} g"),
        ("Fat", f"{nutrition['fat_g']} g"),
    ]
    for column, (label, value) in zip(metric_columns, metrics):
        column.metric(label, value)
    macro_frame = pd.DataFrame(
        {
            "Macronutrient": ["Protein", "Carbohydrates", "Fat"],
            "Grams per serving": [
                nutrition["protein_g"],
                nutrition["carbohydrates_g"],
                nutrition["fat_g"],
            ],
        }
    )
    chart = px.pie(
        macro_frame,
        names="Macronutrient",
        values="Grams per serving",
        hole=0.56,
        color="Macronutrient",
        color_discrete_map={
            "Protein": "#317a59",
            "Carbohydrates": "#e9a43a",
            "Fat": "#df7653",
        },
    )
    chart.update_layout(
        showlegend=True,
        margin=dict(t=10, b=10, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#536158",
        legend=dict(orientation="h", y=-0.08),
    )
    st.plotly_chart(
        chart,
        config={"displayModeBar": False, "responsive": True},
    )
    st.caption("Nutrition values are approximate estimates; see About Cook.io.")

    related = [
        item for item in recipes
        if item["id"] != recipe["id"] and item["cuisine"] == recipe["cuisine"]
    ][:3]
    if not related:
        related = [
            item for item in recipes
            if item["id"] != recipe["id"] and item["category"] == recipe["category"]
        ][:3]
    if related:
        st.subheader(f"More {recipe['cuisine']} favorites")
        _recipe_card_grid(related, favorite_ids, key_prefix="detail-related")


def main():
    _load_styles()

    with st.sidebar:
        logo_name = "logo-dark.svg" if st.session_state.get("dark_mode") else "logo-light.svg"
        brand_image = ASSETS / "img" / logo_name
        if brand_image.is_file():
            svg_data = base64.b64encode(brand_image.read_bytes()).decode("ascii")
            st.markdown(
                f'<img src="data:image/svg+xml;base64,{svg_data}" alt="Cook.io" width="160">',
                unsafe_allow_html=True,
            )
        else:
            st.markdown("## Cook.io")
        st.caption("A little inspiration for your next meal.")
        st.radio("Discover", SECTIONS, key="navigation", label_visibility="collapsed")
        st.toggle("Evening mode", key="dark_mode")
        st.divider()
        st.caption("A recipe collection that stays on your device.")

    _load_styles()
    active_page = st.session_state["navigation"]
    favorite_ids = set(user_state["favorites"])

    recipe_id = st.query_params.get("recipe")
    if recipe_id:
        recipe = _recipe_by_id(recipe_id)
        if recipe is None:
            st.error("That recipe is not in the Cook.io collection.")
            if st.button("Return home"):
                _close_recipe()
            return
        _render_detail(recipe, favorite_ids)
        return

    if active_page == "Home":
        _render_home(favorite_ids)
    elif active_page == "Explore Recipes":
        _render_explore(favorite_ids)
    elif active_page == "Categories":
        _render_categories(favorite_ids)
    elif active_page == "Favorites":
        _render_favorites(favorite_ids)
    elif active_page == "Meal Planner":
        _render_meal_planner(favorite_ids)
    elif active_page == "About Cook.io":
        _render_about()

    st.markdown(
        '<div class="page-footer">Made for everyday cooking · Cook.io</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

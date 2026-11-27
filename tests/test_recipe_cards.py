from streamlit.testing.v1 import AppTest

from components.recipe_card import render_recipe_grid
from services.recipe_service import load_recipes


def test_same_recipe_can_appear_in_multiple_sections():
    def render_sections():
        from components.recipe_card import render_recipe_grid
        from services.recipe_service import load_recipes

        recipe = load_recipes()[0]
        for key_prefix in ("popular", "recent"):
            render_recipe_grid(
                [recipe],
                set(),
                on_open=lambda recipe_id: None,
                on_toggle_favorite=lambda recipe_id: None,
                key_prefix=key_prefix,
            )

    app = AppTest.from_function(render_sections).run()

    assert not app.exception

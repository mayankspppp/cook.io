"""Build the bundled Cook.io recipe catalogue from its curated seed records."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPECIAL_INSTRUCTIONS = {
    "masala-dosa": [
        "Boil the potatoes until tender, then roughly mash them. Cook the onion and mustard seeds in a little oil, add the potatoes and seasonings, and keep the filling warm.",
        "Heat a flat griddle and spread a ladle of dosa batter into a thin circle. Drizzle lightly with oil and cook until the bottom is crisp.",
        "Spoon the potato filling down the centre, fold the dosa over it, and serve hot with chutney or sambar.",
    ],
    "idli-sambar": [
        "Pour the idli batter into greased moulds. Steam until the idlis are set and a skewer comes out clean.",
        "Cook the lentils until soft. Simmer them with the vegetables, sambar powder, and water until the vegetables are tender; finish with a simple mustard-seed tempering.",
        "Serve the warm idlis with the sambar, adjusting its consistency with hot water if needed.",
    ],
    "margherita-pizza": [
        "Heat the oven and a heavy tray or pizza stone to its highest setting. Stretch the dough into a thin round.",
        "Spread a thin layer of tomato sauce over the dough, add mozzarella, and bake until the crust is puffed and browned.",
        "Scatter over fresh basil, drizzle with olive oil, and slice while hot.",
    ],
    "fresh-guacamole": [
        "Halve and pit the avocados, then scoop the flesh into a bowl. Finely chop the onion, cilantro, and tomato.",
        "Mash the avocado with lime juice and a pinch of salt, leaving some texture. Fold through the chopped vegetables.",
        "Taste and adjust the lime and seasoning. Serve straight away with warm tortillas or vegetable sticks.",
    ],
    "sushi-bowl": [
        "Rinse the sushi rice until the water runs clear, then cook it according to the package directions. Season lightly and let it cool until warm.",
        "Slice the avocado and cucumber and cut the carrot into fine matchsticks. Tear the nori into small pieces.",
        "Divide the rice between bowls, arrange the vegetables on top, and finish with nori and a little soy sauce or sesame dressing.",
    ],
    "shakshuka": [
        "Soften the onion and bell pepper in olive oil in a wide skillet. Stir in the cumin and cook briefly until fragrant.",
        "Add the tomatoes and simmer until thickened. Make small wells, add the eggs, cover, and cook until the whites are set.",
        "Finish with cilantro and serve directly from the pan with bread.",
    ],
    "blueberry-pancakes": [
        "Whisk the flour with the other dry ingredients. In another bowl whisk the milk and egg, then stir the two mixtures together just until combined.",
        "Fold in the blueberries. Cook small ladles of batter in a lightly buttered skillet over medium heat, turning when bubbles appear.",
        "Serve warm with maple syrup and extra blueberries if you like.",
    ],
}


def _recipe(
    recipe_id,
    name,
    cuisine,
    category,
    dietary_type,
    method,
    prep_time,
    cook_time,
    servings,
    nutrition,
    image,
    ingredients,
    tags,
):
    total_time = prep_time + cook_time
    difficulty = "Easy" if total_time <= 30 else "Moderate" if total_time <= 60 else "Advanced"
    return {
        "id": recipe_id,
        "name": name,
        "description": (
            f"A home-cook-friendly {cuisine.lower()} {category.lower()} with "
            f"balanced, satisfying flavors. Ready in about {total_time} minutes."
        ),
        "image": f"assets/images/{image}",
        "cuisine": cuisine,
        "category": category,
        "dietary_type": dietary_type,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "total_time": total_time,
        "difficulty": difficulty,
        "servings": servings,
        "ingredients": [
            {"amount": amount, "unit": unit, "name": ingredient}
            for amount, unit, ingredient in ingredients
        ],
        "instructions": SPECIAL_INSTRUCTIONS.get(recipe_id, _instructions(method)),
        "nutrition_per_serving_estimate": {
            "calories": nutrition[0],
            "protein_g": nutrition[1],
            "carbohydrates_g": nutrition[2],
            "fat_g": nutrition[3],
        },
        "tags": list(dict.fromkeys([cuisine.lower(), category.lower(), dietary_type.lower()] + tags)),
        "popularity": 0,
    }


def _instructions(method):
    methods = {
        "stovetop": [
            "Prepare and measure the ingredients; rinse grains or legumes and chop the vegetables.",
            "Warm oil in a heavy pan over medium heat. Cook the aromatics and spices first, add the main ingredients with a splash of water, and cook until tender and fragrant.",
            "Taste and adjust the seasoning. Finish with fresh herbs or lemon, then serve warm.",
        ],
        "simmer": [
            "Rinse, drain, and prepare the ingredients. Measure the spices and keep the garnish separate.",
            "Soften the aromatics in oil, stir in the spices and main ingredients, then add stock or water. Simmer gently until everything is cooked through and the sauce is flavorful.",
            "Taste, adjust salt and acidity, and finish with the listed herbs or garnish before serving.",
        ],
        "stir_fry": [
            "Prepare all ingredients before heating the pan; stir together the sauce ingredients in a small bowl.",
            "Heat a wok or wide skillet until hot. Add oil, cook the aromatics briefly, then stir-fry the remaining ingredients in batches until just tender and fully cooked.",
            "Return everything to the pan, toss with the sauce until glossy, and serve immediately.",
        ],
        "oven": [
            "Heat the oven to 200°C (400°F). Prepare the ingredients and lightly oil a suitable baking dish or tray.",
            "Arrange the ingredients in the dish, season evenly, and bake until tender, golden, and cooked through. Check near the end of the stated cooking time.",
            "Rest briefly, taste for seasoning, add the fresh garnish, and serve.",
        ],
        "grill": [
            "Prepare the ingredients and mix the oil, seasonings, and any marinade together.",
            "Heat a grill or ridged pan to medium-high. Cook the ingredients in a single layer, turning as needed, until browned and fully cooked.",
            "Rest briefly, finish with the fresh garnish or sauce, and serve warm.",
        ],
        "assemble": [
            "Rinse and chop the produce. Cook any grains or other ingredients according to their package directions and let them drain well.",
            "Prepare the dressing or sauce, then layer the cooked ingredients and fresh toppings in serving bowls or plates.",
            "Season to taste, spoon over the sauce, and serve while the warm ingredients are still hot.",
        ],
        "steam": [
            "Prepare the ingredients and line a steamer basket if needed. Bring a few centimetres of water to a steady simmer.",
            "Arrange the ingredients in the steamer without crowding. Cover and steam until tender and cooked through, checking the stated cooking time.",
            "Carefully remove from the steamer, season or garnish as listed, and serve warm.",
        ],
        "blend": [
            "Prepare the ingredients, reserving a little of the liquid and garnish for finishing.",
            "Blend the ingredients with the seasonings until smooth, adding the reserved liquid a little at a time to reach the consistency you like.",
            "Taste and adjust the seasoning. Finish with the garnish and serve, or chill briefly if preferred.",
        ],
        "pancake": [
            "Whisk the dry ingredients together. In a separate bowl, whisk the wet ingredients, then combine just until no dry streaks remain.",
            "Heat a lightly oiled skillet over medium heat. Cook small portions until bubbles appear, flip once, and cook the other side until golden.",
            "Serve warm with the listed toppings, adding them to taste.",
        ],
        "sweet_bake": [
            "Heat the oven to 180°C (350°F). Prepare the baking tin and measure the ingredients before mixing.",
            "Combine the ingredients just until evenly mixed, transfer to the prepared tin, and bake until set and lightly golden.",
            "Cool as directed before slicing. Finish with the listed fruit or garnish and serve.",
        ],
        "chill": [
            "Prepare the ingredients and arrange them in the serving dish or individual glasses.",
            "Mix or layer the ingredients as described, cover, and chill until set and well combined.",
            "Add the fresh garnish just before serving and keep any leftovers refrigerated.",
        ],
    }
    return methods[method]


RECIPES = [
    ("masala-dosa", "Masala Dosa", "Indian", "Breakfast", "Vegetarian", "stovetop", 25, 25, 4, (310, 8, 52, 8), "spiced-curry.jpg", [(1.5, "cups", "dosa batter"), (2, "pieces", "potatoes"), (0.5, "cup", "onion"), (1, "tsp", "mustard seeds"), (1, "tbsp", "oil")], ["south indian", "crispy"]),
    ("vegetable-poha", "Vegetable Poha", "Indian", "Breakfast", "Vegan", "stovetop", 15, 15, 3, (260, 6, 43, 7), "breakfast-board.jpg", [(2, "cups", "thick poha"), (0.5, "cup", "peas"), (0.5, "cup", "onion"), (1, "tbsp", "peanuts"), (1, "tbsp", "lemon juice")], ["quick", "gluten-free"]),
    ("chana-masala", "Chana Masala", "Indian", "Dinner", "Vegan", "simmer", 15, 35, 4, (330, 14, 49, 9), "spiced-curry.jpg", [(2, "cups", "cooked chickpeas"), (1, "cup", "tomatoes"), (0.5, "cup", "onion"), (1, "tbsp", "ginger garlic paste"), (1, "tsp", "garam masala")], ["high-fiber", "weeknight"]),
    ("paneer-tikka", "Paneer Tikka", "Indian", "Snack", "Vegetarian", "grill", 20, 15, 4, (290, 18, 12, 19), "grilled-plate.jpg", [(400, "g", "paneer"), (0.75, "cup", "plain yogurt"), (1, "piece", "bell pepper"), (1, "tsp", "tikka masala"), (1, "tbsp", "lemon juice")], ["protein-rich", "party"]),
    ("dal-tadka", "Dal Tadka", "Indian", "Dinner", "Vegan", "simmer", 10, 35, 4, (280, 16, 40, 6), "spiced-curry.jpg", [(1, "cup", "yellow lentils"), (1, "piece", "tomato"), (0.5, "cup", "onion"), (1, "tsp", "cumin seeds"), (1, "tbsp", "oil")], ["comfort food", "high-fiber"]),
    ("chicken-tikka-masala", "Chicken Tikka Masala", "Indian", "Dinner", "Non-vegetarian", "simmer", 25, 35, 4, (460, 36, 20, 25), "spiced-curry.jpg", [(500, "g", "chicken breast"), (0.75, "cup", "plain yogurt"), (1, "cup", "tomatoes"), (0.5, "cup", "cream"), (1, "tbsp", "garam masala")], ["popular", "protein-rich"]),
    ("palak-paneer", "Palak Paneer", "Indian", "Dinner", "Vegetarian", "stovetop", 15, 25, 4, (350, 19, 20, 22), "spiced-curry.jpg", [(400, "g", "paneer"), (4, "cups", "spinach"), (0.5, "cup", "onion"), (1, "piece", "tomato"), (0.25, "cup", "cream")], ["spinach", "comfort food"]),
    ("vegetable-biryani", "Vegetable Biryani", "Indian", "Dinner", "Vegan", "stovetop", 25, 35, 5, (390, 9, 68, 9), "harvest-bowl.jpg", [(2, "cups", "basmati rice"), (2, "cups", "mixed vegetables"), (0.75, "cup", "onion"), (1, "tbsp", "biryani masala"), (0.25, "cup", "cashews")], ["one-pot", "celebration"]),
    ("aloo-gobi", "Aloo Gobi", "Indian", "Lunch", "Vegan", "stovetop", 15, 30, 4, (250, 7, 37, 8), "spiced-curry.jpg", [(2, "pieces", "potatoes"), (1, "head", "cauliflower"), (1, "piece", "tomato"), (1, "tsp", "turmeric"), (1, "tbsp", "oil")], ["gluten-free", "weeknight"]),
    ("rajma-masala", "Rajma Masala", "Indian", "Dinner", "Vegan", "simmer", 15, 40, 4, (360, 17, 58, 7), "spiced-curry.jpg", [(2, "cups", "cooked kidney beans"), (1, "cup", "tomatoes"), (0.5, "cup", "onion"), (1, "tsp", "cumin"), (1, "tbsp", "oil")], ["high-fiber", "meal prep"]),
    ("idli-sambar", "Idli with Sambar", "Indian", "Breakfast", "Vegan", "steam", 20, 25, 4, (300, 11, 55, 4), "breakfast-board.jpg", [(2, "cups", "idli batter"), (1, "cup", "toor dal"), (1, "cup", "mixed vegetables"), (1, "tbsp", "sambar powder"), (1, "tsp", "mustard seeds")], ["south indian", "steamed"]),
    ("lemon-rice", "South Indian Lemon Rice", "Indian", "Lunch", "Vegan", "stovetop", 10, 15, 4, (290, 6, 51, 8), "harvest-bowl.jpg", [(2, "cups", "cooked rice"), (2, "tbsp", "lemon juice"), (2, "tbsp", "peanuts"), (1, "tsp", "mustard seeds"), (0.25, "tsp", "turmeric")], ["quick", "gluten-free"]),
    ("tandoori-salmon", "Tandoori Salmon", "Indian", "Dinner", "Pescatarian", "grill", 20, 15, 4, (410, 38, 12, 23), "grilled-plate.jpg", [(4, "pieces", "salmon fillets"), (0.5, "cup", "plain yogurt"), (1, "tbsp", "tandoori masala"), (1, "tbsp", "lemon juice"), (1, "tbsp", "oil")], ["omega-3", "protein-rich"]),
    ("tomato-basil-pasta", "Tomato Basil Pasta", "Italian", "Dinner", "Vegetarian", "stovetop", 10, 20, 4, (420, 14, 68, 11), "pasta-bowl.jpg", [(300, "g", "penne pasta"), (2, "cups", "cherry tomatoes"), (2, "tbsp", "olive oil"), (0.5, "cup", "fresh basil"), (0.25, "cup", "parmesan")], ["weeknight", "comfort food"]),
    ("mushroom-risotto", "Creamy Mushroom Risotto", "Italian", "Dinner", "Vegetarian", "stovetop", 15, 35, 4, (440, 13, 61, 16), "pasta-bowl.jpg", [(1.5, "cups", "arborio rice"), (250, "g", "mushrooms"), (4, "cups", "vegetable stock"), (0.5, "cup", "parmesan"), (1, "tbsp", "butter")], ["comfort food", "one-pot"]),
    ("margherita-pizza", "Margherita Pizza", "Italian", "Dinner", "Vegetarian", "oven", 20, 15, 4, (380, 17, 48, 13), "wood-fired-pizza.jpg", [(1, "piece", "pizza dough"), (0.75, "cup", "tomato sauce"), (200, "g", "mozzarella"), (0.5, "cup", "fresh basil"), (1, "tbsp", "olive oil")], ["family favorite", "baked"]),
    ("minestrone-soup", "Rustic Minestrone Soup", "Italian", "Lunch", "Vegan", "simmer", 15, 35, 5, (240, 11, 42, 4), "hearty-soup.jpg", [(1, "cup", "white beans"), (1, "cup", "small pasta"), (1, "piece", "carrot"), (1, "piece", "zucchini"), (4, "cups", "vegetable stock")], ["high-fiber", "one-pot"]),
    ("caprese-salad", "Caprese Salad", "Italian", "Lunch", "Vegetarian", "assemble", 15, 0, 2, (310, 18, 12, 22), "fresh-salad.jpg", [(3, "pieces", "ripe tomatoes"), (200, "g", "fresh mozzarella"), (0.5, "cup", "fresh basil"), (1, "tbsp", "olive oil"), (1, "tsp", "balsamic glaze")], ["no-cook", "summer"]),
    ("black-bean-tacos", "Smoky Black Bean Tacos", "Mexican", "Dinner", "Vegan", "stovetop", 15, 15, 4, (340, 14, 55, 8), "harvest-bowl.jpg", [(2, "cups", "black beans"), (8, "pieces", "corn tortillas"), (1, "piece", "avocado"), (1, "cup", "salsa"), (1, "tsp", "smoked paprika")], ["plant-based", "quick"]),
    ("chicken-fajita-bowl", "Chicken Fajita Bowl", "Mexican", "Lunch", "Non-vegetarian", "stovetop", 20, 20, 4, (490, 38, 56, 13), "harvest-bowl.jpg", [(450, "g", "chicken breast"), (2, "cups", "cooked rice"), (2, "pieces", "bell peppers"), (1, "piece", "red onion"), (1, "tbsp", "fajita seasoning")], ["meal prep", "protein-rich"]),
    ("fresh-guacamole", "Fresh Guacamole", "Mexican", "Snack", "Vegan", "blend", 15, 0, 4, (180, 3, 11, 15), "fresh-salad.jpg", [(3, "pieces", "ripe avocados"), (1, "piece", "lime"), (0.25, "cup", "red onion"), (0.25, "cup", "cilantro"), (1, "piece", "tomato")], ["no-cook", "party"]),
    ("vegetable-enchiladas", "Roasted Vegetable Enchiladas", "Mexican", "Dinner", "Vegetarian", "oven", 25, 30, 4, (430, 20, 54, 15), "wood-fired-pizza.jpg", [(8, "pieces", "corn tortillas"), (2, "cups", "roasted vegetables"), (1.5, "cups", "enchilada sauce"), (1, "cup", "black beans"), (1, "cup", "cheddar cheese")], ["baked", "family favorite"]),
    ("salsa-verde-eggs", "Salsa Verde Breakfast Eggs", "Mexican", "Breakfast", "Vegetarian", "stovetop", 10, 15, 2, (320, 19, 25, 16), "breakfast-board.jpg", [(4, "pieces", "eggs"), (0.75, "cup", "salsa verde"), (2, "pieces", "corn tortillas"), (0.25, "cup", "cotija cheese"), (0.25, "cup", "cilantro")], ["high-protein", "brunch"]),
    ("miso-ramen", "Weeknight Miso Ramen", "Japanese", "Dinner", "Vegetarian", "simmer", 15, 20, 2, (430, 19, 61, 13), "hearty-soup.jpg", [(2, "portions", "ramen noodles"), (4, "cups", "vegetable stock"), (2, "tbsp", "white miso"), (150, "g", "shiitake mushrooms"), (2, "pieces", "eggs")], ["comfort food", "quick"]),
    ("teriyaki-salmon", "Teriyaki Salmon Rice Bowl", "Japanese", "Dinner", "Pescatarian", "stovetop", 15, 15, 2, (510, 37, 56, 16), "grilled-plate.jpg", [(2, "pieces", "salmon fillets"), (1, "cup", "cooked rice"), (2, "tbsp", "soy sauce"), (1, "tbsp", "honey"), (1, "cup", "steamed broccoli")], ["omega-3", "protein-rich"]),
    ("sushi-bowl", "Garden Sushi Bowl", "Japanese", "Lunch", "Vegan", "assemble", 20, 20, 2, (390, 9, 70, 8), "harvest-bowl.jpg", [(1, "cup", "sushi rice"), (1, "piece", "avocado"), (0.5, "piece", "cucumber"), (1, "piece", "carrot"), (2, "sheets", "nori")], ["plant-based", "meal prep"]),
    ("chicken-yakitori", "Chicken Yakitori Skewers", "Japanese", "Dinner", "Non-vegetarian", "grill", 20, 15, 4, (330, 35, 20, 10), "grilled-plate.jpg", [(500, "g", "chicken thighs"), (3, "tbsp", "soy sauce"), (1, "tbsp", "mirin"), (1, "tbsp", "honey"), (2, "pieces", "scallions")], ["grilled", "protein-rich"]),
    ("greek-salad", "Classic Greek Salad", "Mediterranean", "Lunch", "Vegetarian", "assemble", 15, 0, 4, (280, 9, 18, 20), "fresh-salad.jpg", [(2, "pieces", "cucumbers"), (3, "pieces", "tomatoes"), (0.5, "piece", "red onion"), (150, "g", "feta"), (0.5, "cup", "kalamata olives")], ["no-cook", "gluten-free"]),
    ("hummus-bowl", "Lemon Hummus Grain Bowl", "Mediterranean", "Lunch", "Vegan", "assemble", 20, 20, 2, (460, 17, 67, 14), "harvest-bowl.jpg", [(1, "cup", "cooked quinoa"), (1, "cup", "hummus"), (1, "piece", "cucumber"), (1, "cup", "cherry tomatoes"), (1, "tbsp", "lemon juice")], ["meal prep", "plant-based"]),
    ("shakshuka", "One-Pan Shakshuka", "Mediterranean", "Breakfast", "Vegetarian", "stovetop", 10, 25, 3, (290, 16, 25, 14), "spiced-curry.jpg", [(4, "pieces", "eggs"), (1.5, "cups", "crushed tomatoes"), (1, "piece", "red bell pepper"), (0.5, "cup", "onion"), (1, "tsp", "cumin")], ["one-pan", "brunch"]),
    ("falafel-pita", "Herby Falafel Pita", "Middle Eastern", "Lunch", "Vegan", "oven", 25, 25, 4, (410, 16, 58, 13), "harvest-bowl.jpg", [(2, "cups", "cooked chickpeas"), (4, "pieces", "whole-wheat pita"), (0.5, "cup", "parsley"), (0.5, "cup", "plain yogurt"), (1, "tsp", "ground cumin")], ["plant-based", "high-fiber"]),
    ("lemon-herb-chicken", "Lemon Herb Roast Chicken", "Mediterranean", "Dinner", "Non-vegetarian", "oven", 15, 45, 4, (440, 42, 18, 22), "grilled-plate.jpg", [(600, "g", "chicken thighs"), (2, "pieces", "lemons"), (2, "tbsp", "olive oil"), (1, "tbsp", "fresh rosemary"), (500, "g", "baby potatoes")], ["roasted", "protein-rich"]),
    ("green-curry", "Thai Green Vegetable Curry", "Thai", "Dinner", "Vegan", "simmer", 15, 25, 4, (370, 9, 41, 20), "spiced-curry.jpg", [(2, "tbsp", "green curry paste"), (400, "ml", "coconut milk"), (2, "cups", "mixed vegetables"), (1, "cup", "cooked rice"), (1, "tbsp", "lime juice")], ["plant-based", "one-pot"]),
    ("pad-thai", "Balanced Chicken Pad Thai", "Thai", "Dinner", "Non-vegetarian", "stir_fry", 25, 15, 3, (470, 28, 62, 12), "pasta-bowl.jpg", [(200, "g", "rice noodles"), (300, "g", "chicken breast"), (2, "pieces", "eggs"), (2, "tbsp", "tamarind paste"), (0.25, "cup", "peanuts")], ["popular", "stir-fry"]),
    ("tom-yum-soup", "Bright Tom Yum Soup", "Thai", "Lunch", "Pescatarian", "simmer", 15, 20, 4, (210, 22, 18, 5), "hearty-soup.jpg", [(300, "g", "shrimp"), (4, "cups", "vegetable stock"), (150, "g", "mushrooms"), (2, "tbsp", "lime juice"), (1, "tbsp", "tom yum paste")], ["light", "gluten-free"]),
    ("ratatouille", "Provençal Ratatouille", "French", "Dinner", "Vegan", "oven", 25, 45, 4, (240, 7, 32, 10), "harvest-bowl.jpg", [(1, "piece", "eggplant"), (1, "piece", "zucchini"), (2, "pieces", "tomatoes"), (1, "piece", "bell pepper"), (2, "tbsp", "olive oil")], ["plant-based", "seasonal"]),
    ("blueberry-crepes", "Simple Blueberry Crêpes", "French", "Breakfast", "Vegetarian", "pancake", 15, 20, 4, (260, 9, 38, 8), "breakfast-board.jpg", [(1, "cup", "all-purpose flour"), (2, "pieces", "eggs"), (1.25, "cups", "milk"), (1, "cup", "blueberries"), (1, "tbsp", "butter")], ["brunch", "sweet"]),
    ("french-onion-soup", "Slow-Cooked French Onion Soup", "French", "Lunch", "Vegetarian", "simmer", 15, 50, 4, (330, 14, 38, 13), "hearty-soup.jpg", [(4, "pieces", "yellow onions"), (4, "cups", "vegetable stock"), (4, "slices", "baguette"), (100, "g", "gruyere"), (2, "tbsp", "butter")], ["comfort food", "slow-simmered"]),
    ("classic-turkey-burger", "Classic Turkey Burger", "American", "Dinner", "Non-vegetarian", "grill", 15, 15, 4, (420, 34, 39, 15), "garden-burger.jpg", [(500, "g", "ground turkey"), (4, "pieces", "burger buns"), (1, "piece", "egg"), (1, "tsp", "garlic powder"), (1, "cup", "lettuce")], ["grilled", "protein-rich"]),
    ("blueberry-pancakes", "Fluffy Blueberry Pancakes", "American", "Breakfast", "Vegetarian", "pancake", 10, 15, 4, (290, 10, 49, 7), "breakfast-board.jpg", [(1.5, "cups", "all-purpose flour"), (1, "cup", "milk"), (1, "piece", "egg"), (1, "cup", "blueberries"), (1, "tbsp", "maple syrup")], ["brunch", "family favorite"]),
    ("bbq-pulled-chicken", "Easy BBQ Pulled Chicken", "American", "Dinner", "Non-vegetarian", "simmer", 15, 35, 4, (390, 38, 36, 11), "grilled-plate.jpg", [(600, "g", "chicken breast"), (1, "cup", "tomato barbecue sauce"), (4, "pieces", "whole-grain rolls"), (0.5, "piece", "red onion"), (1, "tbsp", "apple cider vinegar")], ["meal prep", "weeknight"]),
    ("cobb-salad", "Garden Cobb Salad", "American", "Lunch", "Non-vegetarian", "assemble", 20, 15, 2, (470, 34, 20, 29), "fresh-salad.jpg", [(2, "cups", "romaine lettuce"), (2, "pieces", "eggs"), (150, "g", "chicken breast"), (0.5, "piece", "avocado"), (0.25, "cup", "blue cheese")], ["high-protein", "gluten-free"]),
    ("vegetable-fried-rice", "Everyday Vegetable Fried Rice", "Chinese", "Dinner", "Vegan", "stir_fry", 15, 12, 4, (360, 9, 60, 9), "harvest-bowl.jpg", [(3, "cups", "cooked rice"), (1, "cup", "peas and carrots"), (2, "pieces", "scallions"), (2, "tbsp", "soy sauce"), (1, "tbsp", "sesame oil")], ["quick", "one-pan"]),
    ("ginger-garlic-dumplings", "Ginger Garlic Vegetable Dumplings", "Chinese", "Snack", "Vegan", "steam", 35, 12, 4, (280, 10, 46, 6), "harvest-bowl.jpg", [(24, "pieces", "dumpling wrappers"), (2, "cups", "shredded cabbage"), (1, "piece", "carrot"), (1, "tbsp", "fresh ginger"), (2, "tbsp", "soy sauce")], ["steamed", "plant-based"]),
    ("mapo-tofu", "Gentle Mapo Tofu", "Chinese", "Dinner", "Vegetarian", "stovetop", 15, 20, 3, (340, 20, 22, 20), "spiced-curry.jpg", [(400, "g", "firm tofu"), (1, "tbsp", "chili bean paste"), (1, "cup", "vegetable stock"), (1, "tbsp", "soy sauce"), (1, "tsp", "cornstarch")], ["high-protein", "weeknight"]),
    ("vegetable-bibimbap", "Colorful Vegetable Bibimbap", "Korean", "Dinner", "Vegetarian", "assemble", 25, 20, 2, (450, 16, 70, 12), "harvest-bowl.jpg", [(1.5, "cups", "cooked rice"), (1, "cup", "spinach"), (1, "piece", "carrot"), (1, "piece", "zucchini"), (2, "pieces", "eggs")], ["balanced", "meal prep"]),
    ("beef-bulgogi-bowl", "Weeknight Beef Bulgogi Bowl", "Korean", "Dinner", "Non-vegetarian", "stir_fry", 20, 12, 3, (480, 34, 55, 14), "grilled-plate.jpg", [(400, "g", "lean beef"), (2, "cups", "cooked rice"), (2, "tbsp", "soy sauce"), (1, "piece", "pear"), (1, "tbsp", "sesame oil")], ["protein-rich", "quick"]),
    ("red-lentil-soup", "Middle Eastern Red Lentil Soup", "Middle Eastern", "Lunch", "Vegan", "simmer", 10, 30, 4, (270, 16, 43, 5), "hearty-soup.jpg", [(1.5, "cups", "red lentils"), (1, "piece", "carrot"), (1, "piece", "onion"), (1, "tsp", "ground cumin"), (5, "cups", "vegetable stock")], ["high-fiber", "one-pot"]),
    ("tabbouleh-salad", "Fresh Parsley Tabbouleh", "Middle Eastern", "Lunch", "Vegan", "assemble", 25, 15, 4, (230, 7, 41, 7), "fresh-salad.jpg", [(1, "cup", "bulgur wheat"), (2, "cups", "parsley"), (1, "cup", "tomatoes"), (0.5, "cup", "cucumber"), (2, "tbsp", "lemon juice")], ["fresh", "plant-based"]),
    ("chocolate-date-bites", "No-Bake Chocolate Date Bites", "International", "Dessert", "Vegan", "blend", 15, 0, 12, (150, 4, 21, 7), "breakfast-board.jpg", [(1, "cup", "soft dates"), (0.75, "cup", "rolled oats"), (2, "tbsp", "cocoa powder"), (2, "tbsp", "almond butter"), (1, "tbsp", "chia seeds")], ["no-bake", "snack"]),
    ("mango-yogurt-parfait", "Mango Yogurt Parfait", "International", "Breakfast", "Vegetarian", "assemble", 10, 0, 2, (280, 15, 42, 6), "breakfast-board.jpg", [(1.5, "cups", "plain Greek yogurt"), (1, "piece", "ripe mango"), (0.5, "cup", "granola"), (1, "tbsp", "honey"), (1, "tbsp", "pumpkin seeds")], ["no-cook", "quick"]),
]


def build_recipes():
    recipes = [_recipe(*record) for record in RECIPES]
    identifiers = [recipe["id"] for recipe in recipes]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Recipe IDs must be unique.")
    if len(recipes) < 50:
        raise ValueError("The catalogue must contain at least 50 recipes.")
    for index, recipe in enumerate(recipes):
        recipe["popularity"] = 1000 - index * 10
    return recipes


if __name__ == "__main__":
    destination = ROOT / "data" / "recipes.json"
    destination.write_text(
        json.dumps(build_recipes(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(RECIPES)} recipes to {destination}")

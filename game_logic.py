import random

def handle_baking_process(game):
    # Debug print to see what ingredients are being checked
    print(f"Checking recipe with ingredients: {game.current_ingredients}")
    
    # Check if the current ingredients match any recipe
    for recipe, ingredients in game.recipes.items():
        # Debug print for recipe comparison
        print(f"Comparing with recipe {recipe}: {ingredients}")
        
        # Sort both lists to ensure consistent comparison
        current_sorted = sorted(game.current_ingredients)
        recipe_sorted = sorted(ingredients)
        
        if current_sorted == recipe_sorted:
            base_reward = 10
            if "Quality Ingredients" in game.active_upgrades:
                base_reward += 5  # Extra reward for quality ingredients
            result = f"Successfully baked {recipe}!"
            game.current_ingredients = []  # Clear current ingredients after baking
            game.has_baked = True
            print(f"Recipe matched! {recipe}")  # Debug print
            return result, base_reward

    # If no recipe matches, it's a failed attempt
    print("No recipe matched with current ingredients")  # Debug print
    penalty = 5
    result = "Baking failed."
    game.current_ingredients = []  # Clear current ingredients after baking
    return result, -penalty  # Only return the penalty, don't modify bakecoin here

def generate_customer_order():
    recipes = ["Cake", "Cookies", "Brownies", "Pancakes", "Muffins"]
    return f"Customer wants: {random.choice(recipes)}"

def trigger_kitchen_disaster():
    disasters = ["Oven malfunction", "Ingredient spill", "Power outage"]
    return random.choice(disasters)

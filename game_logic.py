import random
from config import DIFFICULTY_SETTINGS

def handle_baking_process(game):
    """Process baking attempt and return result message and reward/penalty"""
    # Don't process baking if animation is in progress
    if game.animation_manager.is_animating:
        return None, 0  # Return early if animating
    
    if not game.current_ingredients:
        return None, 0

    # Debug print current ingredients
    print(f"Current ingredients: {sorted(game.current_ingredients)}")

    # Check if the current ingredients match any recipe
    for recipe, required_ingredients in game.recipes.items():
        # Sort both lists to ensure consistent comparison
        current_sorted = sorted(game.current_ingredients)
        recipe_sorted = sorted(required_ingredients)
        
        # Debug print recipe comparison
        print(f"Comparing with {recipe}: {recipe_sorted}")
        
        # Check if all required ingredients are present
        if set(current_sorted) == set(recipe_sorted):
            base_reward = 10
            if "Quality Ingredients" in game.active_upgrades:
                base_reward += 5  # Extra reward for quality ingredients
            result = f"Successfully baked {recipe}!"
            game.current_ingredients.clear()  # Clear current ingredients after baking
            game.animation_manager.reset_bowl()  # Reset the bowl visualization
            game.has_baked = True
            print(f"Recipe matched! {recipe}")  # Debug print
            game.bakecoin += base_reward  # Add the reward to bakecoin
            return result, base_reward

    # If no recipe matches, it's a failed attempt
    print("No recipe matched with current ingredients")  # Debug print
    penalty = 5
    result = f"Baking failed! Lost {penalty} Bakecoin"  # Added penalty amount to message
    game.current_ingredients.clear()  # Clear current ingredients after baking
    game.animation_manager.reset_bowl()  # Reset the bowl visualization
    game.bakecoin -= penalty  # Subtract the penalty from bakecoin
    return result, -penalty

def trigger_kitchen_disaster(game):
    """Trigger a kitchen disaster with upgrade effects"""
    base_chance = DIFFICULTY_SETTINGS[game.difficulty]["disaster_chance"]
    disaster_types = ["Oven malfunction", "Ingredient spill", "Power outage"]
    
    # Apply upgrade effects
    if "Better Oven" in game.active_upgrades:
        base_chance *= 0.5  # 50% less chance of oven malfunction
    if "Sturdy Shelves" in game.active_upgrades:
        base_chance *= 0.5  # 50% less chance of ingredient spills
    if "Backup Generator" in game.active_upgrades:
        base_chance *= 0.5  # 50% less chance of power outages
        
    if random.random() < base_chance:
        disaster = random.choice(disaster_types)
        # Check if upgrade prevents this specific disaster
        if (disaster == "Oven malfunction" and "Better Oven" in game.active_upgrades) or \
           (disaster == "Ingredient spill" and "Sturdy Shelves" in game.active_upgrades) or \
           (disaster == "Power outage" and "Backup Generator" in game.active_upgrades):
            if random.random() < 0.5:  # 50% chance to prevent disaster
                return None
        
        # Handle disaster effects
        if disaster == "Ingredient spill":
            if game.current_ingredients:
                # Remove 1-2 random ingredients
                remove_count = random.randint(1, min(2, len(game.current_ingredients)))
                for _ in range(remove_count):
                    if game.current_ingredients:
                        removed_ingredient = random.choice(game.current_ingredients)
                        game.current_ingredients.remove(removed_ingredient)
                        game.ingredient_counts[removed_ingredient] = max(0, game.ingredient_counts[removed_ingredient] - 1)
                # Update bowl fill level
                game.animation_manager.bowl_fill_level = len(game.current_ingredients) * 0.1
        
        elif disaster == "Power outage":
            if game.current_ingredients and random.random() < 0.3:  # 30% chance to affect ingredients
                # Clear all ingredients in bowl
                for ing in game.current_ingredients:
                    game.ingredient_counts[ing] = max(0, game.ingredient_counts[ing] - 1)
                game.current_ingredients.clear()
                game.animation_manager.bowl_fill_level = 0
        
        elif disaster == "Oven malfunction":
            if game.current_ingredients:
                # Remove half of the ingredients
                remove_count = len(game.current_ingredients) // 2
                for _ in range(remove_count):
                    if game.current_ingredients:
                        ing = game.current_ingredients.pop(random.randint(0, len(game.current_ingredients) - 1))
                        game.ingredient_counts[ing] = max(0, game.ingredient_counts[ing] - 1)
                # Update bowl fill level
                game.animation_manager.bowl_fill_level = len(game.current_ingredients) * 0.1
        
        game.disaster_count += 1
        game.animation_manager.add_popup_message(f"Oh no! {disaster}!", color=(255, 0, 0))
        return disaster
    
    return None

def generate_customer_order(game):
    """Generate a random customer order"""
    if random.random() < DIFFICULTY_SETTINGS[game.difficulty]["customer_order_chance"]:
        recipe = random.choice(list(game.discovered_recipes))
        reward = 15  # Base reward
        if "Quality Ingredients" in game.active_upgrades:
            reward += 5  # Extra reward for quality ingredients
        return f"Customer Order: {recipe} (Reward: {reward} Bakecoin)"
    return None

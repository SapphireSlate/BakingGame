from config import DIFFICULTY_SETTINGS, base_ingredients, WIDTH, HEIGHT
import random
import pygame
import math
from game_logic import trigger_kitchen_disaster, generate_customer_order
from animation import flash_screen_red
from sprites import IngredientSprite

class Game:
    def __init__(self, animation_manager):
        self.bakecoin = 0  # Initialize to 0
        self.difficulty = "Normal"
        self.disaster_count = 0
        self.has_baked = False
        self.current_ingredients = []
        self.discovered_recipes = set(["Cake", "Cookies", "Brownies", "Pancakes", "Muffins"])
        # Initialize all ingredients with exactly 5
        self.ingredient_counts = {ing: 5 for ing in base_ingredients}
        self.active_upgrades = set()
        self.state = "intro"
        self.achievements = {}  # Add this line
        self.baking = False
        self.kitchen_disaster = None
        self.customer_order = None
        self.recipes = {
            "Cake": ["Flour", "Sugar", "Eggs", "Milk", "Butter"],
            "Cookies": ["Flour", "Sugar", "Eggs", "Butter"],
            "Brownies": ["Flour", "Sugar", "Eggs", "Cocoa", "Butter"],
            "Pancakes": ["Flour", "Eggs", "Milk", "Butter"],
            "Muffins": ["Flour", "Sugar", "Eggs", "Milk", "Baking Powder"],
            "Chocolate Cake": ["Flour", "Sugar", "Eggs", "Milk", "Butter", "Cocoa"],
            "Meringue Cookies": ["Eggs", "Sugar", "Vanilla"],
            "Condensed Milk Fudge": ["Condensed Milk", "Chocolate Chips"]
        }
        # ... other game state variables ...
        self.upgrades = {
            "Better Oven": {"cost": 50, "effect": "Reduces Oven malfunction chance", "icon": "🔥"},
            "Sturdy Shelves": {"cost": 75, "effect": "Reduces Ingredient spill chance", "icon": "🥣"},
            "Backup Generator": {"cost": 100, "effect": "Reduces Power outage chance", "icon": "🔌"},
            "Quality Ingredients": {"cost": 125, "effect": "Improves baking success rate", "icon": "⭐"}
        }
        self.animation_manager = animation_manager

        # Add the combinations dictionary but don't show ingredients until discovered
        self.combinations = {
            ("Cocoa", "Sugar"): "Chocolate Chips",
            ("Milk", "Sugar"): "Condensed Milk",
            ("Eggs", "Sugar"): "Meringue",
            ("Powdered Sugar", "Butter"): "Frosting"
        }
        
        # Start with only base ingredients discovered
        self.discovered_ingredients = set(base_ingredients)

        # Add sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.ingredient_sprites = pygame.sprite.Group()
        self.initialize_sprites()

    def apply_difficulty(self):
        return DIFFICULTY_SETTINGS[self.difficulty]

    def start_baking(self):
        if len(self.current_ingredients) > 0 and not self.baking:
            print("Start baking called...")  # Debug print
            self.baking = True
            # This will be handled in the main game loop

    def handle_ingredient_click(self, x, y):
        if self.animation_manager.is_animating:
            return None, None, None

        # Check collision with ingredient sprites
        pos = pygame.mouse.get_pos()
        for sprite in self.ingredient_sprites:
            if sprite.rect.collidepoint(pos):
                ing = sprite.name
                if self.ingredient_counts[ing] > 0:
                    self.current_ingredients.append(ing)
                    self.ingredient_counts[ing] -= 1
                    sprite.update_count(self.ingredient_counts[ing])
                    return ing, sprite.rect.centerx, sprite.rect.centery

        return None, None, None

    def check_for_combinations(self):
        # Only check for combinations if there are exactly 2 ingredients
        if len(self.current_ingredients) == 2:
            ing1, ing2 = self.current_ingredients[0], self.current_ingredients[1]
            combination = tuple(sorted([ing1, ing2]))
            new_ingredient = self.combinations.get(combination)
            
            if new_ingredient and new_ingredient not in self.discovered_ingredients:
                self.discovered_ingredients.add(new_ingredient)
                self.ingredient_counts[new_ingredient] = 5
                print(f"New ingredient discovered: {new_ingredient}")  # Debug print
                return f"New ingredient discovered: {new_ingredient}!"
        return None

    def update(self):
        # Remove the baking process from here since it's handled in handle_keydown
        
        # Check for kitchen disasters
        if not self.kitchen_disaster:
            if random.random() < self.apply_difficulty()["disaster_chance"]:
                self.kitchen_disaster = trigger_kitchen_disaster()
        
        # Generate customer orders
        if not self.customer_order:
            if random.random() < self.apply_difficulty()["customer_order_chance"]:
                self.customer_order = generate_customer_order()

        # Update all sprites
        self.all_sprites.update()

    def handle_baking_process(self):
        # Don't process baking if animation is in progress
        if self.animation_manager.is_animating:
            return None, 0  # Return early if animating
        
        if not self.current_ingredients:
            return None, 0

        # Check if the current ingredients match any recipe
        for recipe, ingredients in self.recipes.items():
            # Sort both lists to ensure consistent comparison
            current_sorted = sorted(self.current_ingredients)
            recipe_sorted = sorted(ingredients)
            
            if current_sorted == recipe_sorted:
                base_reward = 10
                if "Quality Ingredients" in self.active_upgrades:
                    base_reward += 5  # Extra reward for quality ingredients
                result = f"Successfully baked {recipe}!"
                self.current_ingredients.clear()  # Clear current ingredients after baking
                self.animation_manager.reset_bowl()  # Reset the bowl visualization
                self.has_baked = True
                print(f"Recipe matched! {recipe}")  # Debug print
                self.bakecoin += base_reward  # Add the reward to bakecoin
                return result, base_reward

        # If no recipe matches, it's a failed attempt
        print("No recipe matched with current ingredients")  # Debug print
        penalty = 5
        result = f"Baking failed! Lost {penalty} Bakecoin"  # Added penalty amount to message
        self.current_ingredients.clear()  # Clear current ingredients after baking
        self.animation_manager.reset_bowl()  # Reset the bowl visualization
        self.bakecoin -= penalty  # Subtract the penalty from bakecoin
        return result, -penalty

    def load_from_save(self, save_data):
        self.bakecoin = save_data["bakecoin"]
        self.discovered_recipes = set(save_data["discovered_recipes"])
        self.achievements = save_data["achievements"]
        self.difficulty = save_data["difficulty"]
        self.disaster_count = save_data["disaster_count"]
        self.has_baked = save_data["has_baked"]

    # ... other methods to manage game state ...

    def choose_difficulty(self, key):
        print(f"Choosing difficulty with key: {pygame.key.name(key)}")  # Debug print
        if key == pygame.K_e:
            self.difficulty = "Easy"
            self.bakecoin = 150  # Starting amount for Easy
        elif key == pygame.K_n:
            self.difficulty = "Normal"
            self.bakecoin = 75   # Starting amount for Normal
        elif key == pygame.K_h:
            self.difficulty = "Hard"
            self.bakecoin = 50   # Starting amount for Hard
        self.state = "main_game"
        print(f"Difficulty set to: {self.difficulty}, Bakecoin: {self.bakecoin}, State changed to: {self.state}")  # Debug print

    def trigger_kitchen_disaster(self):
        base_chance = self.apply_difficulty()["disaster_chance"]
        disaster_types = ["Oven malfunction", "Ingredient spill", "Power outage"]
        
        for disaster in disaster_types:
            if disaster == "Oven malfunction" and "Better Oven" in self.active_upgrades:
                base_chance *= 0.5
            elif disaster == "Ingredient spill" and "Sturdy Shelves" in self.active_upgrades:
                base_chance *= 0.5
            elif disaster == "Power outage" and "Backup Generator" in self.active_upgrades:
                base_chance *= 0.5
            
            if random.random() < base_chance:
                self.kitchen_disaster = disaster
                self.disaster_count += 1
                self.animation_manager.trigger_disaster_animation(disaster, self)
                return self.kitchen_disaster
        
        return None

    def handle_disaster_animation(self, animation_manager):
        ingredients_affected = False
        if self.kitchen_disaster == "Ingredient spill":
            if self.current_ingredients:
                removed_ingredient = random.choice(self.current_ingredients)
                self.current_ingredients.remove(removed_ingredient)
                # Set bowl fill level proportional to remaining ingredients
                animation_manager.bowl_fill_level = len(self.current_ingredients) * 0.1
                self.ingredient_counts[removed_ingredient] = max(0, self.ingredient_counts[removed_ingredient] - 1)
                ingredients_affected = True

        elif self.kitchen_disaster == "Power outage":
            if random.random() < 0.3:  # 30% chance
                for ing in self.current_ingredients:
                    self.ingredient_counts[ing] = max(0, self.ingredient_counts[ing] - 1)
                self.current_ingredients.clear()
                # Reset bowl fill level when all ingredients are lost
                animation_manager.bowl_fill_level = 0
                ingredients_affected = True

        elif self.kitchen_disaster == "Oven malfunction":
            if self.current_ingredients:
                remove_count = len(self.current_ingredients) // 2
                for _ in range(remove_count):
                    ing = self.current_ingredients.pop(random.randint(0, len(self.current_ingredients) - 1))
                    self.ingredient_counts[ing] = max(0, self.ingredient_counts[ing] - 1)
                # Set bowl fill level proportional to remaining ingredients
                animation_manager.bowl_fill_level = len(self.current_ingredients) * 0.1
                ingredients_affected = True

        self.disaster_count += 1
        return ingredients_affected

    def combine_ingredients(self, ing1, ing2):
        # Try both orderings of the ingredients
        combination = tuple(sorted([ing1, ing2]))
        new_ingredient = self.combinations.get(combination)
        
        if new_ingredient:
            if new_ingredient not in self.ingredient_counts:
                self.ingredient_counts[new_ingredient] = 5  # Initialize with 5 when discovered
            else:
                self.ingredient_counts[new_ingredient] += 1
            self.discovered_ingredients.add(new_ingredient)
            return new_ingredient
        return None

    def replenish_ingredients(self):
        cost = 25  # Cost for replenishing ingredients
        if self.bakecoin >= cost:
            self.bakecoin -= cost
            # Reset all discovered ingredients to current amount + 5
            for ing in self.discovered_ingredients:
                self.ingredient_counts[ing] = self.ingredient_counts.get(ing, 0) + 5
            print(f"Ingredients replenished. Cost: {cost} Bakecoin")
            return True
        else:
            print("Not enough Bakecoin to replenish ingredients!")
            return False

    def reset_bowl(self):
        self.current_ingredients.clear()
        self.animation_manager.reset_bowl()

    def initialize_sprites(self):
        # Create sprites in two columns on the left side
        sprite_width = 100  # Width of each sprite
        sprite_height = 100  # Height of each sprite
        margin_left = 50  # Left margin from screen edge
        margin_top = 150  # Top margin to avoid bakecoin display
        spacing_y = 20  # Vertical spacing between sprites
        
        items_per_column = (len(self.ingredient_counts) + 1) // 2  # Distribute items evenly
        
        for i, (ing, count) in enumerate(self.ingredient_counts.items()):
            column = i // items_per_column  # 0 for first column, 1 for second
            row = i % items_per_column
            
            x = margin_left + column * (sprite_width + 50)  # 50px spacing between columns
            y = margin_top + row * (sprite_height + spacing_y)
            
            sprite = IngredientSprite(ing, x, y, count)
            self.all_sprites.add(sprite)
            self.ingredient_sprites.add(sprite)

    def purchase_upgrade(self, mouse_pos):
        """Purchase an upgrade if the player has enough bakecoins"""
        if self.state != "main_game":
            return False
            
        upgrade_width = WIDTH // len(self.upgrades)
        x = mouse_pos[0]
        y = mouse_pos[1]
        
        # Check if click is in upgrade area
        if y >= HEIGHT - 50:
            upgrade_index = x // upgrade_width
            if upgrade_index < len(self.upgrades):
                upgrade_name = list(self.upgrades.keys())[upgrade_index]
                
                # Don't allow purchasing already active upgrades
                if upgrade_name in self.active_upgrades:
                    return False
                    
                upgrade_cost = self.upgrades[upgrade_name]["cost"]
                if self.bakecoin >= upgrade_cost:
                    self.bakecoin -= upgrade_cost
                    self.active_upgrades.add(upgrade_name)
                    print(f"Purchased upgrade: {upgrade_name}")
                    return True
                else:
                    print(f"Not enough Bakecoin for {upgrade_name}")
        return False

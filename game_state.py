from config import DIFFICULTY_SETTINGS, base_ingredients, WIDTH, HEIGHT
import random
import pygame
import math
from game_logic import trigger_kitchen_disaster, generate_customer_order, handle_baking_process
from animation import flash_screen_red
from sprites import IngredientSprite

class Game:
    def __init__(self, animation_manager):
        # Initialize game state
        self.state = "intro"  # Start in intro state
        self.bakecoin = 75  # Start with 75 bakecoin
        self.difficulty = "Normal"
        self.disaster_count = 0
        self.has_baked = False
        self.current_ingredients = []
        self.discovered_recipes = set(["Cake", "Cookies", "Brownies", "Pancakes", "Muffins"])
        
        # Initialize all ingredients with exactly 5
        self.ingredient_counts = {ing: 5 for ing in base_ingredients}
        self.active_upgrades = set()
        self.achievements = {}
        self.baking = False
        self.kitchen_disaster = None
        self.customer_order = None
        
        # Initialize recipes
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
        
        # Initialize combinations
        self.combinations = {
            ("Cocoa", "Sugar"): "Chocolate Chips",
            ("Milk", "Sugar"): "Condensed Milk",
            ("Eggs", "Sugar"): "Meringue",
            ("Powdered Sugar", "Butter"): "Frosting"
        }
        
        # Start with only base ingredients discovered
        self.discovered_ingredients = set(base_ingredients)
        
        # Initialize upgrades with costs and effects
        self.upgrades = {
            "Better Oven": {"cost": 50, "effect": "Reduces Oven malfunction chance", "icon": "🔥"},
            "Sturdy Shelves": {"cost": 75, "effect": "Reduces Ingredient spill chance", "icon": "🥣"},
            "Backup Generator": {"cost": 100, "effect": "Reduces Power outage chance", "icon": "🔌"},
            "Quality Ingredients": {"cost": 125, "effect": "Improves baking success rate", "icon": "⭐"}
        }
        
        # Store animation manager
        self.animation_manager = animation_manager
        
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.ingredient_sprites = pygame.sprite.Group()
        
        # Initialize UI after sprite groups
        from ui import ModernUI
        self.ui = ModernUI()
        
        # Initialize sprites
        self.initialize_sprites()
        
    def initialize_sprites(self):
        """Initialize ingredient sprites with proper positioning"""
        # Clear existing sprites
        self.all_sprites.empty()
        self.ingredient_sprites.empty()
        
        # Calculate grid layout
        margin_left = 30
        margin_top = 80
        sprite_width = 220
        sprite_height = 120
        spacing_y = 110
        items_per_row = 2
        
        # Create sprites for each ingredient
        for i, ingredient in enumerate(sorted(self.ingredient_counts.keys())):
            row = i // items_per_row
            col = i % items_per_row
            
            x = margin_left + col * (sprite_width - 60)  # Reduced spacing between columns by subtracting 60
            y = margin_top + row * spacing_y
            
            sprite = IngredientSprite(ingredient, x, y, self.ingredient_counts[ingredient])
            self.ingredient_sprites.add(sprite)
            self.all_sprites.add(sprite)
    
    def update(self):
        """Update game state"""
        if self.state != "main_game":
            return
            
        # Update all sprites
        self.all_sprites.update()
        
        # Check for kitchen disasters
        if not self.kitchen_disaster:
            settings = DIFFICULTY_SETTINGS[self.difficulty]
            if random.random() < settings["disaster_chance"]:
                self.kitchen_disaster = trigger_kitchen_disaster(self)
                
        # Check for customer orders
        if not self.customer_order:
            settings = DIFFICULTY_SETTINGS[self.difficulty]
            if random.random() < settings["customer_order_chance"]:
                self.customer_order = generate_customer_order(self)
                
        # Clear disasters with a 10% chance each update
        if self.kitchen_disaster and random.random() < 0.1:
            self.kitchen_disaster = None
            
    def handle_ingredient_click(self, x, y):
        """Handle ingredient click and return animation info"""
        for sprite in self.ingredient_sprites:
            if sprite.rect.collidepoint(x, y) and sprite.count > 0:
                # Add ingredient to current ingredients
                self.current_ingredients.append(sprite.name)
                # Decrease count
                sprite.count -= 1
                sprite.update_count(sprite.count)
                # Return animation info
                return sprite.name, sprite.rect.centerx, sprite.rect.centery
        return None, None, None
        
    def replenish_ingredients(self):
        """Replenish all ingredients for 25 bakecoin"""
        if self.bakecoin >= 25:
            self.bakecoin -= 25
            for ingredient in self.ingredient_counts:
                self.ingredient_counts[ingredient] = 5
                # Update sprite counts
                for sprite in self.ingredient_sprites:
                    if sprite.name == ingredient:
                        sprite.update_count(5)
            return True
        return False
        
    def purchase_upgrade(self, mouse_pos):
        """Purchase an upgrade if clicked and can afford"""
        # Calculate button dimensions exactly as in UI
        upgrade_height = 50
        spacing = 10
        total_width = WIDTH - 40  # Match UI's total width
        button_width = (total_width - (spacing * (len(self.upgrades) - 1))) // len(self.upgrades)
        
        y = HEIGHT - upgrade_height - spacing
        
        # Calculate total buttons width and center position exactly as in UI
        total_buttons_width = (button_width * len(self.upgrades)) + (spacing * (len(self.upgrades) - 1))
        start_x = (WIDTH - total_buttons_width) // 2  # Center the buttons horizontally
        
        # Debug print for mouse position
        print(f"Mouse click at: {mouse_pos}")
        
        for i, (name, upgrade) in enumerate(self.upgrades.items()):
            x = start_x + i * (button_width + spacing)
            button_rect = pygame.Rect(x, y, button_width, upgrade_height)
            
            # Debug print for each button's area
            print(f"Button '{name}' rect: {button_rect}, Cost: {upgrade['cost']}, Active: {name in self.active_upgrades}")
            
            if button_rect.collidepoint(mouse_pos):
                print(f"Clicked on {name} upgrade")
                if name not in self.active_upgrades and self.bakecoin >= upgrade['cost']:
                    print(f"Purchasing {name} for {upgrade['cost']} bakecoin")
                    self.bakecoin -= upgrade['cost']
                    self.active_upgrades.add(name)
                    return True
                else:
                    print(f"Cannot purchase: Active={name in self.active_upgrades}, Bakecoin={self.bakecoin}")
        return False
        
    def handle_baking_process(self):
        """Process baking attempt and return result message and reward/penalty"""
        return handle_baking_process(self)

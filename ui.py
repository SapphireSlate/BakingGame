import pygame
from config import WIDTH, HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY
import math
import random

def draw_intro_screen(screen):
    """Draw the intro screen with title and start prompt"""
    # Fill screen with dark background
    screen.fill((20, 25, 35))
    
    # Create title text
    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("Bakecoin", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    
    # Create semi-transparent background for title
    title_bg = pygame.Surface((title_rect.width + 40, title_rect.height + 20), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (40, 45, 60, 180), title_bg.get_rect(), border_radius=10)
    
    # Draw title background and text
    screen.blit(title_bg, (title_rect.x - 20, title_rect.y - 10))
    screen.blit(title_text, title_rect)
    
    # Create start prompt text
    prompt_font = pygame.font.Font(None, 36)
    prompt_text = prompt_font.render("Press ENTER to Start", True, (200, 200, 200))
    prompt_rect = prompt_text.get_rect(center=(WIDTH//2, HEIGHT * 3//4))
    
    # Create semi-transparent background for prompt
    prompt_bg = pygame.Surface((prompt_rect.width + 40, prompt_rect.height + 20), pygame.SRCALPHA)
    pygame.draw.rect(prompt_bg, (40, 45, 60, 180), prompt_bg.get_rect(), border_radius=10)
    
    # Draw prompt background and text
    screen.blit(prompt_bg, (prompt_rect.x - 20, prompt_rect.y - 10))
    screen.blit(prompt_text, prompt_rect)
    
    # Draw version number
    version_font = pygame.font.Font(None, 24)
    version_text = version_font.render("v1.0", True, (128, 128, 128))
    version_rect = version_text.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
    screen.blit(version_text, version_rect)
    
    # Draw decorative elements
    draw_decorative_elements(screen)

def draw_decorative_elements(screen):
    """Draw decorative elements on the intro screen"""
    # Draw floating particles
    for _ in range(20):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(2, 4)
        alpha = random.randint(50, 150)
        particle_color = (255, 255, 255, alpha)
        
        particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, particle_color, (size//2, size//2), size//2)
        screen.blit(particle_surface, (x, y))
    
    # Draw subtle grid lines
    for x in range(0, WIDTH, 40):
        alpha = 30
        pygame.draw.line(screen, (255, 255, 255, alpha), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        alpha = 30
        pygame.draw.line(screen, (255, 255, 255, alpha), (0, y), (WIDTH, y))

def handle_dialogue(screen, game):
    """Handle dialogue screens including difficulty selection"""
    if game.state == "choose_difficulty":
        # Fill screen with dark background
        screen.fill((20, 25, 35))
        
        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Choose Difficulty", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title_text, title_rect)
        
        # Draw difficulty options
        options_font = pygame.font.Font(None, 36)
        difficulties = [
            ("Easy", "Start with 100 Bakecoin", "Less frequent disasters", "E"),
            ("Normal", "Start with 75 Bakecoin", "Regular gameplay", "N"),
            ("Hard", "Start with 50 Bakecoin", "More frequent disasters", "H")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        difficulty_rects = []  # Store rectangles for mouse interaction
        
        for i, (diff, coins, desc, key) in enumerate(difficulties):
            y_pos = HEIGHT//2 + i * 80
            
            # Create option background
            option_rect = pygame.Rect(WIDTH//2 - 200, y_pos - 10, 400, 60)
            is_hovered = option_rect.collidepoint(mouse_pos)
            
            # Store rectangle for click detection
            difficulty_rects.append((option_rect, diff))
            
            # Draw background with hover effect
            bg_color = (60, 65, 80, 230) if is_hovered else (40, 45, 60, 180)
            option_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
            pygame.draw.rect(option_bg, bg_color, option_bg.get_rect(), border_radius=10)
            screen.blit(option_bg, option_rect)
            
            # Draw difficulty name with key hint
            diff_text = options_font.render(f"{diff} ({key})", True, (255, 255, 255))
            diff_rect = diff_text.get_rect(midleft=(WIDTH//2 - 180, y_pos + 20))
            screen.blit(diff_text, diff_rect)
            
            # Draw description
            desc_font = pygame.font.Font(None, 24)
            desc_text = desc_font.render(desc, True, (200, 200, 200))
            desc_rect = desc_text.get_rect(midleft=(WIDTH//2 - 180, y_pos + 40))
            screen.blit(desc_text, desc_rect)
            
            # Draw coins info
            coins_text = desc_font.render(coins, True, (255, 215, 0))  # Gold color
            coins_rect = coins_text.get_rect(midright=(WIDTH//2 + 180, y_pos + 20))
            screen.blit(coins_text, coins_rect)
        
        # Handle mouse clicks
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, difficulty in difficulty_rects:
                    if rect.collidepoint(event.pos):
                        game.difficulty = difficulty
                        game.state = "main_game"
                        print(f"Starting game with difficulty: {difficulty}")
                        if difficulty == "Easy":
                            game.bakecoin = 100
                        elif difficulty == "Normal":
                            game.bakecoin = 75
                        else:  # Hard
                            game.bakecoin = 50

def draw_recipe_book_screen(screen, game):
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 24)
    y = 50
    for recipe in game.discovered_recipes:
        text = font.render(recipe, True, (0, 0, 0))
        screen.blit(text, (50, y))
        y += 30
    
    back_text = font.render("Press B to go back", True, (0, 0, 0))
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

class VolumeControl:
    def __init__(self, x, y, width=200):
        self.x = x
        self.y = y
        self.width = width
        self.height = 150
        self.visible = False
        self.sliders = {
            'master': {'value': 0.8, 'y_offset': 20, 'label': 'Master Volume'},
            'mixing': {'value': 0.4, 'y_offset': 50, 'label': 'Mixing Sounds'},
            'baking': {'value': 0.3, 'y_offset': 80, 'label': 'Baking Sounds'},
            'effects': {'value': 0.5, 'y_offset': 110, 'label': 'Effects'},
            'ambient': {'value': 0.1, 'y_offset': 140, 'label': 'Ambient'}
        }
        self.active_slider = None
        self.font = pygame.font.Font(None, 24)
        
    def toggle(self):
        self.visible = not self.visible
    
    def handle_mouse_down(self, pos):
        if not self.visible:
            return False
            
        mouse_x, mouse_y = pos
        if not (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):
            self.visible = False
            return False
        
        # Check if clicked on a slider
        for channel, slider in self.sliders.items():
            slider_y = self.y + slider['y_offset']
            if slider_y - 5 <= mouse_y <= slider_y + 5:
                self.active_slider = channel
                # Update value based on x position
                value = (mouse_x - self.x) / self.width
                self.sliders[channel]['value'] = max(0.0, min(1.0, value))
                return True
        return True
    
    def handle_mouse_up(self):
        self.active_slider = None
    
    def handle_mouse_motion(self, pos):
        if not self.visible or not self.active_slider:
            return
            
        mouse_x, _ = pos
        # Update active slider value
        value = (mouse_x - self.x) / self.width
        self.sliders[self.active_slider]['value'] = max(0.0, min(1.0, value))
    
    def get_volume(self, channel):
        return self.sliders[channel]['value']
    
    def draw(self, screen):
        if not self.visible:
            return
            
        # Draw background panel
        panel = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*DARK_GRAY, 230), 
                        (0, 0, self.width + 20, self.height + 20), 
                        border_radius=10)
        screen.blit(panel, (self.x - 10, self.y - 10))
        
        # Draw title
        title = self.font.render("Volume Settings", True, WHITE)
        screen.blit(title, (self.x + self.width//2 - title.get_width()//2, self.y - 5))
        
        # Draw each slider
        for channel, slider in self.sliders.items():
            # Draw label
            label = self.font.render(slider['label'], True, WHITE)
            screen.blit(label, (self.x, self.y + slider['y_offset'] - 15))
            
            # Draw slider track
            pygame.draw.line(screen, GRAY,
                           (self.x, self.y + slider['y_offset']),
                           (self.x + self.width, self.y + slider['y_offset']),
                           2)
            
            # Draw slider handle
            handle_x = self.x + self.width * slider['value']
            pygame.draw.circle(screen, WHITE,
                             (int(handle_x), self.y + slider['y_offset']),
                             6)
            
            # Draw percentage
            percent = f"{int(slider['value'] * 100)}%"
            percent_text = self.font.render(percent, True, WHITE)
            screen.blit(percent_text, 
                       (self.x + self.width + 5, 
                        self.y + slider['y_offset'] - 8))

# Add volume control to existing Button class
class Button:
    def __init__(self, x, y, width, height, text, action=None, color=GRAY, hover_color=DARK_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.action:
                self.action()
                return True
        return False

class ModernUI:
    def __init__(self):
        # Initialize fonts
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # Modern color scheme
        self.colors = {
            'background': (20, 25, 35, 255),
            'panel': (40, 45, 60, 200),
            'panel_light': (60, 65, 80, 200),
            'glass': (255, 255, 255, 30),
            'glass_dark': (20, 25, 35, 180),
            'text': (255, 255, 255, 255),
            'text_dark': (20, 25, 35, 255),
            'accent': (100, 200, 255, 255),
            'success': (100, 255, 100, 255),
            'warning': (255, 200, 100, 255),
            'error': (255, 100, 100, 255)
        }
        
        # Panel positions and dimensions
        self.recipe_panel_rect = pygame.Rect(WIDTH - 280, 20, 260, HEIGHT - 40)
        self.inventory_panel_rect = pygame.Rect(20, 20, 260, HEIGHT - 40)
        
        # Initialize floating particles
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'position': (
                    random.uniform(-100, 100),
                    random.uniform(-100, 100),
                    random.uniform(0, 50)
                ),
                'color': (255, 255, 255, 255),
                'size': random.uniform(2, 4),
                'alpha': random.randint(50, 150),
                'speed': random.uniform(0.5, 1.5)
            })
        
        # Initialize game state
        self.state = "intro"

    def update_particles(self, dt):
        """Update particle positions and properties"""
        for particle in self.particles:
            # Update z position with floating motion
            particle['position'] = (
                particle['position'][0],
                particle['position'][1],
                particle['position'][2] + math.sin(pygame.time.get_ticks() / 1000) * particle['speed']
            )
            
            # Reset particles that float too high
            if particle['position'][2] > 100:
                particle['position'] = (
                    random.uniform(-100, 100),
                    random.uniform(-100, 100),
                    0
                )
    
    def draw_game_ui(self, screen, game):
        """Draw the main game UI with 3D effects"""
        # Clear screen with a dark gradient background
        self.draw_background(screen)
        
        # Draw side panels with glass effect
        recipe_panel = pygame.Surface((self.recipe_panel_rect.width, self.recipe_panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(recipe_panel, self.colors['glass_dark'], recipe_panel.get_rect(), border_radius=10)
        screen.blit(recipe_panel, self.recipe_panel_rect)
        
        inventory_panel = pygame.Surface((self.inventory_panel_rect.width, self.inventory_panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(inventory_panel, self.colors['glass_dark'], inventory_panel.get_rect(), border_radius=10)
        screen.blit(inventory_panel, self.inventory_panel_rect)
        
        # Draw recipe list with modern styling
        self.draw_recipe_panel(screen, game)
        
        # Draw top bar with game info
        self.draw_top_bar(screen, game)
        
        # Draw bottom buttons first
        self.draw_replenish_button(screen, game)
        self.draw_upgrades(screen, game)
        
        # Draw ingredient grid last to ensure it's on top
        self.draw_ingredient_grid(screen, game)

    def draw_background(self, screen):
        """Draw a modern gradient background"""
        bg_start = self.colors.get('background', (20, 25, 35, 255))
        bg_end = self.colors.get('background_light', (30, 35, 45, 255))
        
        for i in range(HEIGHT):
            progress = i / HEIGHT
            color = [
                int(bg_start[0] + (bg_end[0] - bg_start[0]) * progress),
                int(bg_start[1] + (bg_end[1] - bg_start[1]) * progress),
                int(bg_start[2] + (bg_end[2] - bg_start[2]) * progress),
                255  # Keep full opacity for background
            ]
            pygame.draw.line(screen, color, (0, i), (WIDTH, i))
    
    def draw_ingredient_grid(self, screen, game):
        """Draw ingredients in a modern floating grid layout"""
        grid_start_x = self.inventory_panel_rect.x + 20
        grid_start_y = self.inventory_panel_rect.y + 60
        
        items_per_row = 2
        spacing_x = 160  # Reduced from 180 to 160 for even tighter horizontal spacing
        spacing_y = 110
        
        # Draw "Ingredients" title with less padding
        title = self.font_medium.render("Ingredients", True, self.colors['text'])
        screen.blit(title, (grid_start_x, self.inventory_panel_rect.y + 20))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, sprite in enumerate(game.ingredient_sprites):
            row = i // items_per_row
            col = i % items_per_row
            
            x = grid_start_x + col * spacing_x
            y = grid_start_y + row * spacing_y
            
            # Update sprite's position
            sprite.rect.center = (x + 110, y + 60)
            
            # Draw ingredient circle with hover effect
            radius = 25
            if sprite.is_hovered:  # Using sprite's own hover detection
                radius = 30
                # Draw hover glow
                glow_radius = radius + 5
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*self.colors['accent'][:3], 100), 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (x + 110 - glow_radius, y + 60 - glow_radius))
            
            # Draw ingredient
            color = sprite.color
            if len(color) == 3:
                color = (*color, 255)
            pygame.draw.circle(screen, color, (x + 110, y + 60), radius)
            pygame.draw.circle(screen, self.colors['text'], (x + 110, y + 60), radius, 2)
            
            # Draw ingredient name and count with improved visibility
            name_surface = self.font_small.render(sprite.name, True, self.colors['text'])
            count_surface = self.font_small.render(f"x{sprite.count}", True, self.colors['text'])
            
            # Add background for better text visibility
            text_bg = pygame.Surface((name_surface.get_width() + 10, name_surface.get_height() + 4), pygame.SRCALPHA)
            pygame.draw.rect(text_bg, self.colors['glass_dark'], text_bg.get_rect(), border_radius=4)
            
            name_pos = (x + 110 - name_surface.get_width()//2, y + 90)
            count_pos = (x + 110 - count_surface.get_width()//2, y + 110)
            
            # Draw text backgrounds
            screen.blit(text_bg, (name_pos[0] - 5, name_pos[1] - 2))
            screen.blit(name_surface, name_pos)
            screen.blit(count_surface, count_pos)
    
    def get_mixed_color(self, ingredients):
        """Get a mixed color based on current ingredients"""
        if not ingredients:
            return self.colors['panel']
        
        # Define base colors for ingredients (all with alpha)
        ingredient_colors = {
            'Flour': (240, 240, 240, 255),  # White
            'Sugar': (255, 250, 250, 255),  # Off-white
            'Eggs': (255, 223, 168, 255),   # Light yellow
            'Milk': (255, 255, 255, 255),   # White
            'Butter': (255, 225, 120, 255), # Yellow
            'Cocoa': (101, 67, 33, 255),    # Brown
            'Vanilla': (255, 229, 180, 255), # Cream
            'Baking Powder': (255, 255, 255, 255), # White
            'Chocolate Chips': (80, 50, 20, 255),  # Dark brown
            'Condensed Milk': (255, 248, 220, 255), # Cream
            'Meringue': (255, 255, 255, 255),      # White
            'Powdered Sugar': (255, 255, 255, 255), # White
            'Frosting': (255, 255, 255, 255)       # White
        }
        
        # Mix colors
        r, g, b, a = 0, 0, 0, 0
        for ingredient in ingredients:
            color = ingredient_colors.get(ingredient, (200, 200, 200, 255))
            r += color[0]
            g += color[1]
            b += color[2]
            a += color[3]
        
        count = len(ingredients)
        return (r//count, g//count, b//count, a//count)
    
    def draw_recipe_panel(self, screen, game):
        """Draw recipe panel with modern styling"""
        panel_x = self.recipe_panel_rect.x + 20
        panel_y = self.recipe_panel_rect.y + 100  # Increased from 80 to 100 to match ingredient spacing
        
        # Draw "Recipes" title
        title = self.font_medium.render("Recipes", True, self.colors['text'])
        screen.blit(title, (panel_x, self.recipe_panel_rect.y + 30))  # Keep title position the same
        
        # Draw recipe list
        for i, recipe in enumerate(game.discovered_recipes):
            y_offset = i * 80
            
            # Create recipe card
            card_rect = pygame.Rect(panel_x, panel_y + y_offset, 220, 70)
            card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(card_surface, self.colors['glass'], card_surface.get_rect(), border_radius=10)
            
            # Draw recipe name
            recipe_text = self.font_small.render(recipe, True, self.colors['text'])
            text_pos = (10, 10)
            card_surface.blit(recipe_text, text_pos)
            
            # Draw recipe ingredients
            if recipe in game.recipes:
                ingredients = ", ".join(game.recipes[recipe][:3])
                if len(game.recipes[recipe]) > 3:
                    ingredients += "..."
                ing_text = self.font_small.render(ingredients, True, self.colors['text'])
                ing_pos = (10, 35)
                card_surface.blit(ing_text, ing_pos)
            
            screen.blit(card_surface, card_rect)
    
    def draw_top_bar(self, screen, game):
        """Draw top bar with game information"""
        # Create glass panel for top bar
        top_bar = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        pygame.draw.rect(top_bar, self.colors['glass_dark'], top_bar.get_rect())
        
        # Draw bakecoin count
        coin_text = self.font_medium.render(f"🪙 {game.bakecoin}", True, self.colors['accent'])
        coin_pos = (WIDTH//2 - coin_text.get_width()//2, 10)
        top_bar.blit(coin_text, coin_pos)
        
        screen.blit(top_bar, (0, 0))
    
    def draw_button(self, screen, rect, text, color=None, hover=False, active=False):
        """Draw a modern button with glass effect"""
        if color is None:
            color = self.colors['secondary']
            
        # Create button surface
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Handle both RGB and RGBA color tuples
        if len(color) == 3:
            # If RGB, add alpha of 200
            button_color = (*color, 200 if not hover else 240)
        else:
            # If RGBA, adjust alpha based on hover
            button_color = (*color[:3], color[3] + 40 if hover else color[3])
            
        pygame.draw.rect(button_surface, button_color, button_surface.get_rect(), border_radius=10)
        
        # Draw text
        text_surface = self.font_medium.render(text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=(rect.width//2, rect.height//2))
        button_surface.blit(text_surface, text_rect)
        
        # Add hover effect
        if hover:
            pygame.draw.rect(button_surface, (*self.colors['accent'], 30),
                           button_surface.get_rect(), border_radius=10)
        
        screen.blit(button_surface, rect)

    def draw_replenish_button(self, screen, game):
        """Draw the replenish ingredients button"""
        button_x = 20
        button_y = HEIGHT - 100
        button_width = 200
        button_height = 40
        
        # Create button surface with glass effect
        button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        
        # Check if player has enough bakecoin
        can_afford = game.bakecoin >= 25
        
        # Draw button background
        if can_afford:
            color = self.colors['panel'] if not pygame.Rect(button_x, button_y, button_width, button_height).collidepoint(pygame.mouse.get_pos()) else self.colors['panel_light']
        else:
            color = (*self.colors['panel'][:3], 100)  # Semi-transparent when can't afford
            
        pygame.draw.rect(button_surface, color, button_surface.get_rect(), border_radius=5)
        
        # Draw button text
        text = self.font_small.render("Replenish (25🪙)", True, self.colors['text'] if can_afford else (*self.colors['text'][:3], 100))
        text_rect = text.get_rect(center=(button_width//2, button_height//2))
        button_surface.blit(text, text_rect)
        
        # Draw button on screen
        screen.blit(button_surface, (button_x, button_y))

    def draw_upgrades(self, screen, game):
        """Draw upgrade options using modern UI"""
        upgrade_height = 50
        spacing = 10
        total_width = WIDTH - 40  # Account for screen edges with more padding
        button_width = (total_width - (spacing * (len(game.upgrades) - 1))) // len(game.upgrades)
        
        y = HEIGHT - upgrade_height - spacing
        
        # Calculate total buttons width
        total_buttons_width = (button_width * len(game.upgrades)) + (spacing * (len(game.upgrades) - 1))
        start_x = (WIDTH - total_buttons_width) // 2  # Center the buttons horizontally
        
        for i, (name, upgrade) in enumerate(game.upgrades.items()):
            x = start_x + i * (button_width + spacing)
            
            # Create upgrade button rect
            button_rect = pygame.Rect(x, y, button_width, upgrade_height)
            
            # Determine button state
            is_active = name in game.active_upgrades
            is_affordable = game.bakecoin >= upgrade['cost']
            is_hovered = button_rect.collidepoint(pygame.mouse.get_pos())
            
            # Create button surface
            button_surface = pygame.Surface((button_width, upgrade_height), pygame.SRCALPHA)
            
            # Draw button background
            if is_active:
                color = self.colors['success']
            elif is_affordable:
                color = self.colors['panel_light'] if is_hovered else self.colors['panel']
            else:
                color = (*self.colors['panel'][:3], 100)  # Semi-transparent when can't afford
                
            pygame.draw.rect(button_surface, color, button_surface.get_rect(), border_radius=5)
            
            # Draw upgrade info
            text = f"{upgrade['icon']} {name} ({upgrade['cost']}🪙)"
            text_surface = self.font_small.render(text, True, 
                self.colors['text'] if (is_active or is_affordable) else (*self.colors['text'][:3], 100))
            
            # Scale text if too wide for button
            if text_surface.get_width() > button_width - 20:
                scale = (button_width - 20) / text_surface.get_width()
                new_width = int(text_surface.get_width() * scale)
                new_height = int(text_surface.get_height() * scale)
                text_surface = pygame.transform.smoothscale(text_surface, (new_width, new_height))
            
            text_rect = text_surface.get_rect(center=(button_width//2, upgrade_height//2))
            button_surface.blit(text_surface, text_rect)
            
            # Draw button on screen
            screen.blit(button_surface, button_rect)

import pygame
from config import WIDTH, HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY
import math
import random

def draw_intro_screen(screen):
    screen.fill(BLACK)
    
    # Create semi-transparent background for title
    title_font = pygame.font.Font(None, 64)
    title_text = title_font.render("Bakecoin", True, WHITE, None)
    
    # Create background surface for title
    title_bg = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 20), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (20, 20, 40, 180), title_bg.get_rect())
    
    # Position and draw title
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = HEIGHT // 2
    screen.blit(title_bg, (title_x - 20, title_y - 10))
    screen.blit(title_text, (title_x, title_y))
    
    # Create semi-transparent background for start text
    start_font = pygame.font.Font(None, 32)
    start_text = start_font.render("Press ENTER to start", True, WHITE, None)
    
    # Create background surface for start text
    start_bg = pygame.Surface((start_text.get_width() + 40, start_text.get_height() + 20), pygame.SRCALPHA)
    pygame.draw.rect(start_bg, (20, 20, 40, 180), start_bg.get_rect())
    
    # Position and draw start text
    start_x = WIDTH // 2 - start_text.get_width() // 2
    start_y = HEIGHT * 3 // 4
    screen.blit(start_bg, (start_x - 20, start_y - 10))
    screen.blit(start_text, (start_x, start_y))

def handle_dialogue(screen, game):
    """Draw dialogue UI based on game state"""
    # Draw background gradient
    if hasattr(game, 'ui'):
        game.ui.draw_background(screen)
    else:
        screen.fill((0, 0, 0))  # Use RGB tuple for black
    
    # Create glass panel for dialogue
    if hasattr(game, 'ui'):
        panel_width = 600
        panel_height = 200
        panel_x = WIDTH//2 - panel_width//2
        panel_y = HEIGHT//2 - panel_height//2
        
        # Create semi-transparent panel surface
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        glass_color = (20, 25, 35, 180)  # Fixed RGBA color
        pygame.draw.rect(panel_surface, glass_color, panel_surface.get_rect(), border_radius=10)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Get appropriate text based on game state
        if game.state == "intro":
            title = "Welcome to Bakecoin!"
            text = "Press ENTER to start"
        elif game.state == "choose_difficulty":
            title = "Choose Your Difficulty"
            text = "Press E (Easy), N (Normal), or H (Hard)"
        else:
            title = "Let's Start Baking!"
            text = "Click ingredients to add them to the bowl. Press ENTER to bake."
        
        # Use RGB tuples for text color
        text_color = (255, 255, 255)  # Fixed RGB color
        
        # Draw title
        title_surface = game.ui.font_large.render(title, True, text_color)
        title_rect = title_surface.get_rect(center=(WIDTH//2, panel_y + 50))
        screen.blit(title_surface, title_rect)
        
        # Draw instruction text
        text_surface = game.ui.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(WIDTH//2, panel_y + 120))
        screen.blit(text_surface, text_rect)
    else:
        # Fallback to basic rendering if UI not initialized
        font = pygame.font.Font(None, 32)
        if game.state == "intro":
            text = "Welcome to Bakecoin! Press ENTER to start."
        elif game.state == "choose_difficulty":
            text = "Choose your difficulty: Easy (E), Normal (N), or Hard (H)."
        else:
            text = "Click ingredients to add them to the bowl. Press ENTER to bake."
        
        text_surface = font.render(text, True, (255, 255, 255))  # Use RGB tuple for white
        screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, HEIGHT//2))
    
    pygame.display.flip()
    print(f"Drawing dialogue for state: {game.state}")  # Debug print

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
        self.font_title = pygame.font.Font(None, 64)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # UI Colors - All colors defined as RGBA tuples
        self.colors = {
            'primary': (60, 80, 135, 255),
            'secondary': (40, 50, 80, 200),
            'accent': (255, 180, 50, 255),
            'text': (255, 255, 255, 255),
            'text_dark': (20, 20, 30, 255),
            'panel': (30, 35, 50, 200),
            'panel_light': (50, 60, 80, 200),
            'success': (100, 200, 100, 200),
            'error': (200, 80, 80, 200),
            'warning': (200, 150, 50, 200),
            'glass': (255, 255, 255, 40),
            'glass_dark': (20, 25, 35, 180),
            'background': (20, 25, 35, 255),
            'background_light': (30, 35, 45, 255),
            'highlight': (70, 90, 150, 200),
            'shadow': (15, 20, 30, 200)
        }
        
        # UI Animation states
        self.animations = {
            'menu_offset': 0,
            'panel_alpha': 0,
            'hover_scale': 1.0,
            'rotation': 0
        }
        
        try:
            # Initialize 3D renderer
            from render_3d import IsometricRenderer
            self.renderer = IsometricRenderer()
        except ImportError as e:
            print(f"Warning: Could not import IsometricRenderer: {e}")
            self.renderer = None
        
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
                'color': (255, 255, 255, 255),  # Added alpha channel
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
        
        # Draw mixing bowl in center
        bowl_x = WIDTH // 2
        bowl_y = HEIGHT // 2
        bowl_width = 200  # Increased width
        bowl_height = 120  # Increased height
        
        # Draw bowl shadow
        shadow_surface = pygame.Surface((bowl_width + 20, bowl_height + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect())
        screen.blit(shadow_surface, (bowl_x - (bowl_width + 20)//2, bowl_y - bowl_height//2 + 20))
        
        # Draw bowl base (more oval shaped)
        bowl_rect = pygame.Rect(bowl_x - bowl_width//2, bowl_y - bowl_height//2, bowl_width, bowl_height)
        pygame.draw.ellipse(screen, (*self.colors['panel'][:3], 255), bowl_rect)
        
        # Draw bowl rim (angled ellipse)
        rim_height = 25
        rim_rect = pygame.Rect(bowl_x - bowl_width//2, bowl_y - bowl_height//2 - rim_height//2, bowl_width, rim_height)
        pygame.draw.ellipse(screen, (*self.colors['panel_light'][:3], 255), rim_rect)
        
        # Draw bowl contents if any ingredients
        if game.current_ingredients:
            content_color = self.get_mixed_color(game.current_ingredients)
            content_rect = pygame.Rect(bowl_x - bowl_width//2 + 15, 
                                     bowl_y - bowl_height//2 + 15, 
                                     bowl_width - 30, 
                                     bowl_height - 30)
            pygame.draw.ellipse(screen, content_color, content_rect)
            
            # Add shine effect to contents
            shine_surface = pygame.Surface((bowl_width - 30, bowl_height - 30), pygame.SRCALPHA)
            shine_rect = shine_surface.get_rect()
            pygame.draw.ellipse(shine_surface, (255, 255, 255, 30), shine_rect)
            screen.blit(shine_surface, content_rect)
        
        # Draw ingredient grid
        self.draw_ingredient_grid(screen, game)
        
        # Draw recipe list with modern styling
        self.draw_recipe_panel(screen, game)
        
        # Draw top bar with game info
        self.draw_top_bar(screen, game)
    
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
        spacing_x = 120
        spacing_y = 100  # Reduced vertical spacing
        
        # Draw "Ingredients" title
        title = self.font_medium.render("Ingredients", True, self.colors['text'])
        screen.blit(title, (grid_start_x, grid_start_y - 40))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, sprite in enumerate(game.ingredient_sprites):
            row = i // items_per_row
            col = i % items_per_row
            
            x = grid_start_x + col * spacing_x
            y = grid_start_y + row * spacing_y
            
            # Update sprite's hover state based on mouse position
            sprite.rect.center = (x, y)  # Update sprite's rect position
            sprite.is_hovered = sprite.rect.collidepoint(mouse_pos)
            
            # Draw ingredient circle with hover effect
            radius = 25  # Slightly smaller base radius
            if sprite.is_hovered:
                radius = 30  # Larger radius on hover
                # Draw hover glow
                glow_radius = radius + 5
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*self.colors['accent'][:3], 100), 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (x - glow_radius, y - glow_radius))
            
            # Draw ingredient
            color = sprite.color
            if len(color) == 3:
                color = (*color, 255)  # Add alpha if not present
            pygame.draw.circle(screen, color, (x, y), radius)
            pygame.draw.circle(screen, self.colors['text'], (x, y), radius, 2)
            
            # Draw ingredient name and count with improved visibility
            name_surface = self.font_small.render(sprite.name, True, self.colors['text'])
            count_surface = self.font_small.render(f"x{sprite.count}", True, self.colors['text'])
            
            # Add background for better text visibility
            text_bg = pygame.Surface((name_surface.get_width() + 10, name_surface.get_height() + 4), pygame.SRCALPHA)
            pygame.draw.rect(text_bg, self.colors['glass_dark'], text_bg.get_rect(), border_radius=4)
            
            name_pos = (x - name_surface.get_width()//2, y + radius + 5)
            count_pos = (x - count_surface.get_width()//2, y + radius + 25)
            
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
        panel_y = self.recipe_panel_rect.y + 60
        
        # Draw "Recipes" title
        title = self.font_medium.render("Recipes", True, self.colors['text'])
        screen.blit(title, (panel_x, panel_y - 40))
        
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

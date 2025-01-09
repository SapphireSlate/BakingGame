import pygame
import math
from config import WIDTH, HEIGHT, GRAY, DARK_GRAY, WHITE, BLACK

INGREDIENT_COLORS = {
    "Flour": (245, 240, 235),      # Soft cream white
    "Sugar": (250, 245, 220),      # Warm sandy white
    "Eggs": (255, 200, 50),        # Vibrant egg yolk yellow
    "Milk": (240, 250, 255),       # Cool white with blue undertone
    "Butter": (255, 190, 80),      # Rich golden yellow
    "Cocoa": (45, 25, 15),         # Deep dark chocolate
    "Vanilla": (200, 150, 100),    # Rich caramel brown
    "Baking Powder": (255, 250, 250), # Bright white
    "Powdered Sugar": (255, 255, 250), # Pure white
    "Chocolate Chips": (30, 20, 10),   # Extra dark chocolate
    "Condensed Milk": (255, 225, 180), # Golden cream
    "Meringue": (255, 250, 245),      # Pure white with pink undertone
    "Frosting": (220, 255, 250)       # Cool mint white
}

def ensure_rgb(color):
    """Ensure color is in RGB format (3 components)"""
    if len(color) > 3:
        return color[:3]
    return color

class IngredientSprite(pygame.sprite.Sprite):
    def __init__(self, name, x, y, count):
        super().__init__()
        self.name = name
        self.color = ensure_rgb(INGREDIENT_COLORS.get(name, (200, 200, 200)))
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.count = count
        
        # 3D effect parameters
        self.depth = 20  # Depth of 3D effect
        self.angle = 0  # Current rotation angle
        self.target_angle = 0  # Target rotation angle
        self.rotation_speed = 0.1  # Speed of rotation
        self.perspective = 800  # Perspective distance
        
        # Animation parameters
        self.hover_height = 0
        self.target_hover_height = 0
        self.hover_speed = 0.2
        self.bounce_offset = 0
        self.bounce_speed = 0.05
        self.scale = 1.0
        self.target_scale = 1.0
        
        # Interaction states
        self.is_hovered = False
        self.is_clicked = False
        self.is_selected = False
    
    def draw_modern(self, screen, ui):
        """Draw ingredient with modern 3D effects"""
        # Calculate size based on scale
        size = int(80 * self.scale)
        
        # Create surface for ingredient
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Calculate 3D transformations
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        
        # Draw 3D cylinder for ingredient
        for i in range(self.depth):
            # Calculate ellipse dimensions based on perspective
            squeeze = 1 - (i / self.depth) * 0.3
            width = size * squeeze
            height = size * squeeze * cos_a
            
            # Calculate position with perspective
            x = size + sin_a * i * 0.5
            y = size - i + self.hover_height
            
            # Calculate color with depth shading
            shade = 1 - (i / self.depth) * 0.4
            color = tuple(int(c * shade) for c in self.color)
            
            # Draw ellipse
            pygame.draw.ellipse(surface, (*color, 220), 
                              (x - width/2, y - height/2, width, height))
        
        # Draw top circle
        pygame.draw.ellipse(surface, (*self.color, 255),
                          (size - size/2, 
                           size - self.depth - size/2 + self.hover_height,
                           size, size * cos_a))
        
        # Add highlight
        highlight = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(highlight, (255, 255, 255, 40),
                          (0, 0, size, size * cos_a))
        surface.blit(highlight, (size - size/2,
                               size - self.depth - size/2 + self.hover_height))
        
        # Draw ingredient name
        if self.is_hovered or self.is_selected:
            name_surface = ui.font_small.render(self.name, True, ui.colors['text'])
            name_rect = name_surface.get_rect(center=(size, size * 2 - 20))
            surface.blit(name_surface, name_rect)
        
        # Draw count
        if self.count > 0:
            count_surface = ui.font_small.render(f"x{self.count}", True, ui.colors['text'])
            count_rect = count_surface.get_rect(center=(size * 2 - 20, 20))
            surface.blit(count_surface, count_rect)
        
        # Update the sprite's image
        self.image = surface
        
        # Draw to screen
        screen.blit(self.image, self.rect)
    
    def update(self):
        # Update 3D rotation
        if self.angle != self.target_angle:
            diff = self.target_angle - self.angle
            self.angle += diff * self.rotation_speed
        
        # Update hover animation
        if self.hover_height != self.target_hover_height:
            diff = self.target_hover_height - self.hover_height
            self.hover_height += diff * self.hover_speed
        
        # Update scale animation
        if self.scale != self.target_scale:
            diff = self.target_scale - self.scale
            self.scale += diff * 0.2
        
        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update hover effects
        if self.is_hovered and not was_hovered:
            self.target_hover_height = 10
            self.target_scale = 1.1
            self.target_angle = math.pi * 0.1
        elif not self.is_hovered and was_hovered:
            self.target_hover_height = 0
            self.target_scale = 1.0
            self.target_angle = 0
    
    def handle_click(self):
        """Handle mouse click on the sprite"""
        if self.count > 0:
            self.is_clicked = True
            self.target_scale = 0.9
            pygame.time.set_timer(pygame.USEREVENT, 100)
            return True
        return False
    
    def reset_click(self):
        """Reset click state"""
        self.is_clicked = False
        self.target_scale = 1.0 if not self.is_hovered else 1.1
import pygame
import math
from config import WIDTH, HEIGHT, GRAY, DARK_GRAY, WHITE, BLACK

INGREDIENT_COLORS = {
    "Flour": (245, 240, 235, 255),      # Soft cream white
    "Sugar": (250, 245, 220, 255),      # Warm sandy white
    "Eggs": (255, 200, 50, 255),        # Vibrant egg yolk yellow
    "Milk": (240, 250, 255, 255),       # Cool white with blue undertone
    "Butter": (255, 190, 80, 255),      # Rich golden yellow
    "Cocoa": (45, 25, 15, 255),         # Deep dark chocolate
    "Vanilla": (200, 150, 100, 255),    # Rich caramel brown
    "Baking Powder": (255, 250, 250, 255), # Bright white
    "Powdered Sugar": (255, 255, 250, 255), # Pure white
    "Chocolate Chips": (30, 20, 10, 255),   # Extra dark chocolate
    "Condensed Milk": (255, 225, 180, 255), # Golden cream
    "Meringue": (255, 250, 245, 255),      # Pure white with pink undertone
    "Frosting": (220, 255, 250, 255)       # Cool mint white
}

def ensure_rgb(color):
    """Convert color to RGB or RGBA format as needed"""
    if len(color) == 4:  # RGBA
        return color
    elif len(color) == 3:  # RGB
        return (*color, 255)  # Add full opacity
    else:
        raise ValueError(f"Invalid color format: {color}")

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
        
        # Movement parameters
        self.is_moving = False
        self.target_x = x
        self.target_y = y
        self.speed = 5
        self.bounce_time = 0
        
        # Size parameters
        self.normal_radius = 35
        self.hover_radius = int(self.normal_radius * 1.1)
        self.click_radius = int(self.normal_radius * 0.9)
        self.current_radius = self.normal_radius
        
        # Initialize 3D position
        self.pos_3d = [x - WIDTH/2, y - HEIGHT/2, 0]
        self.target_pos_3d = self.pos_3d.copy()
    
    def update(self):
        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update 3D position
        if self.is_moving:
            # Move towards target
            for i in range(3):
                diff = self.target_pos_3d[i] - self.pos_3d[i]
                if abs(diff) > self.speed:
                    self.pos_3d[i] += self.speed * (1 if diff > 0 else -1)
                else:
                    self.pos_3d[i] = self.target_pos_3d[i]
            
            # Check if we've reached the target
            if all(abs(self.pos_3d[i] - self.target_pos_3d[i]) < self.speed for i in range(3)):
                self.is_moving = False
        
        # Update hover height
        if self.is_hovered:
            self.target_hover_height = 20
        else:
            self.target_hover_height = 0
        
        self.hover_height += (self.target_hover_height - self.hover_height) * self.hover_speed
        
        # Update scale
        if self.is_clicked:
            self.target_scale = 0.9
        elif self.is_hovered:
            self.target_scale = 1.1
        else:
            self.target_scale = 1.0
        
        self.scale += (self.target_scale - self.scale) * 0.2
        
        # Update rotation
        if self.is_hovered:
            self.target_angle += self.rotation_speed
        else:
            self.target_angle = 0
        
        angle_diff = (self.target_angle - self.angle + 180) % 360 - 180
        self.angle += angle_diff * 0.1
        
        # Update current radius
        if self.is_clicked:
            target_radius = self.click_radius
        elif self.is_hovered:
            target_radius = self.hover_radius
        else:
            target_radius = self.normal_radius
        
        self.current_radius += (target_radius - self.current_radius) * 0.3
        
        # Update rect position based on 3D position
        screen_x = WIDTH/2 + self.pos_3d[0]
        screen_y = HEIGHT/2 + self.pos_3d[1] - self.pos_3d[2]
        self.rect.center = (screen_x, screen_y)
    
    def move_to(self, x, y, z=0):
        """Set target position for smooth movement"""
        self.target_pos_3d = [x - WIDTH/2, y - HEIGHT/2, z]
        self.is_moving = True
    
    def handle_click(self):
        """Handle mouse click on the sprite"""
        if self.count > 0:
            self.is_clicked = True
            # Reset click state after a short delay
            pygame.time.set_timer(pygame.USEREVENT, 100)  # 100ms delay
            return True
        return False
    
    def reset_click(self):
        """Reset click state"""
        self.is_clicked = False
    
    def update_count(self, count):
        """Update the ingredient count"""
        self.count = count
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
        self.count = count
        self.font = pygame.font.Font(None, 24)
        
        # Use global INGREDIENT_COLORS and ensure proper RGBA format
        self.color = ensure_rgb(INGREDIENT_COLORS.get(name, (200, 200, 200, 255)))
        self.is_hovered = False
        self.is_clicked = False
        
        # Create sprite image with increased width
        self.image = pygame.Surface((220, 120), pygame.SRCALPHA)  # Increased width from 200 to 220
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.update_appearance()
        
    def get_wrapped_text(self, text, max_width):
        """Get text that fits within max_width by wrapping or scaling"""
        # Try rendering at normal size first
        rendered = self.font.render(text, True, (0, 0, 0))
        if rendered.get_width() <= max_width:
            return [text]
            
        # If too wide, try splitting into two lines
        words = text.split()
        if len(words) > 1:
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            
            # Check if both lines fit
            rendered1 = self.font.render(line1, True, (0, 0, 0))
            rendered2 = self.font.render(line2, True, (0, 0, 0))
            
            if max(rendered1.get_width(), rendered2.get_width()) <= max_width:
                return [line1, line2]
        
        # If still too wide or single word, scale down the font
        original_size = 24
        current_size = original_size
        while current_size > 12:  # Don't go smaller than size 12
            self.font = pygame.font.Font(None, current_size)
            rendered = self.font.render(text, True, (0, 0, 0))
            if rendered.get_width() <= max_width:
                return [text]
            current_size -= 1
        
        # If we get here, use the smallest size
        self.font = pygame.font.Font(None, 12)
        return [text]
        
    def update_appearance(self):
        """Update the sprite's appearance based on state"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw the ingredient circle with size based on state
        radius = 30
        if self.is_clicked:
            radius = 28  # Slightly smaller when clicked
        elif self.is_hovered:
            radius = 32  # Slightly larger when hovered
            
        pygame.draw.circle(self.image, self.color,
                         (110, 45), radius)  # Centered horizontally at 110 (half of 220)
        
        # Get wrapped or scaled text that fits within 200px (leaving 10px padding on each side)
        max_width = 200  # Increased from 180 to 200
        lines = self.get_wrapped_text(self.name, max_width)
        
        if len(lines) == 1:
            # Single line (either short text or scaled)
            text = self.font.render(lines[0], True, (0, 0, 0))
            text_rect = text.get_rect(centerx=110, centery=95)  # Adjusted y position and centerx
            self.image.blit(text, text_rect)
        else:
            # Two lines of text
            text1 = self.font.render(lines[0], True, (0, 0, 0))
            text2 = self.font.render(lines[1], True, (0, 0, 0))
            
            text1_rect = text1.get_rect(centerx=110, centery=90)  # Adjusted y positions and centerx
            text2_rect = text2.get_rect(centerx=110, centery=105)
            
            self.image.blit(text1, text1_rect)
            self.image.blit(text2, text2_rect)
        
        # Draw count in top-right corner with better padding
        count_text = self.font.render(str(self.count), True, (0, 0, 0))
        count_rect = count_text.get_rect(topright=(210, 5))  # Adjusted for new width
        self.image.blit(count_text, count_rect)
        
        # Reset font to default size for next render
        self.font = pygame.font.Font(None, 24)
    
    def update(self):
        """Update sprite state"""
        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        
        # Calculate distance from mouse to center of ingredient circle
        center_x = self.rect.centerx
        center_y = self.rect.centery - 15  # Adjust for the actual circle position
        dx = mouse_pos[0] - center_x
        dy = mouse_pos[1] - center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Only hover if mouse is within the ingredient circle (radius + small margin)
        self.is_hovered = distance <= 35  # Using 35 as radius + margin
        
        # Update appearance if state changed
        if was_hovered != self.is_hovered or self.is_clicked:
            self.update_appearance()
            
    def handle_click(self):
        """Handle mouse click on the sprite"""
        if self.is_hovered and self.count > 0:  # Only handle click if hovered and has ingredients
            self.is_clicked = True
            self.update_appearance()
            # Reset click state after a short delay
            pygame.time.set_timer(pygame.USEREVENT, 100)  # 100ms delay
            return True
        return False
    
    def reset_click(self):
        """Reset click state"""
        self.is_clicked = False
        self.update_appearance()
        
    def update_count(self, new_count):
        """Update the displayed count"""
        self.count = new_count
        self.update_appearance()
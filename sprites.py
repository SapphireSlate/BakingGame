import pygame
import math
from config import WIDTH, HEIGHT, GRAY, DARK_GRAY, WHITE, BLACK

INGREDIENT_COLORS = {
    "Flour": (255, 245, 240),      # Pure white with slight warmth
    "Sugar": (147, 255, 108),      # Bright lime green
    "Eggs": (255, 220, 50),        # Bright yellow
    "Milk": (200, 235, 255),       # Sky blue
    "Butter": (255, 170, 50),      # Orange
    "Cocoa": (90, 50, 30),         # Dark chocolate brown
    "Vanilla": (255, 130, 210),    # Pink
    "Baking Powder": (130, 0, 255), # Deep purple
    "Powdered Sugar": (255, 255, 245), # Bright white
    "Chocolate Chips": (65, 35, 20),   # Rich dark brown
    "Condensed Milk": (255, 180, 100), # Light orange
    "Meringue": (240, 100, 255),      # Bright purple
    "Frosting": (50, 200, 255)        # Azure blue
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
        # Ensure color is in RGB format when storing
        self.color = ensure_rgb(INGREDIENT_COLORS.get(name, (200, 200, 200)))
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Ensure full transparency
        self.rect = self.image.get_rect(center=(x, y))
        self.count = count
        
        # Add missing movement attributes
        self.is_moving = False
        self.target_x = x
        self.target_y = y
        self.speed = 5
        self.bounce_time = 0
        self.bounce_speed = 0.05
        self.bounce_offset = 0
        
        self.draw_character()

    def draw_character(self):
        self.image.fill((0, 0, 0, 0))  # Clear with full transparency
        
        # Draw only the circle and its border
        center = (50, 50)
        radius = 35
        
        # Create RGBA colors from RGB base colors
        circle_color = (*ensure_rgb(self.color), 230)  # Add alpha channel
        border_color = (*ensure_rgb(WHITE), 255)  # Solid white border
        text_color = ensure_rgb(BLACK)  # Text color in RGB
        
        # Draw circle and border
        pygame.draw.circle(self.image, circle_color, center, radius)
        pygame.draw.circle(self.image, border_color, center, radius, 2)
        
        # Draw name inside circle
        font = pygame.font.Font(None, 20)
        words = self.name.split()
        if len(words) > 1:
            # Split long names into two lines
            name_line1 = " ".join(words[:len(words)//2])
            name_line2 = " ".join(words[len(words)//2:])
            
            text1 = font.render(name_line1, True, text_color)
            text2 = font.render(name_line2, True, text_color)
            
            text_rect1 = text1.get_rect(center=(50, 42))
            text_rect2 = text2.get_rect(center=(50, 58))
            
            self.image.blit(text1, text_rect1)
            self.image.blit(text2, text_rect2)
        else:
            text = font.render(self.name, True, text_color)
            text_rect = text.get_rect(center=(50, 45))
            self.image.blit(text, text_rect)
        
        # Draw count at bottom
        count_text = f"x{self.count}"
        count_surf = font.render(count_text, True, text_color)
        count_rect = count_surf.get_rect(center=(50, 65))
        self.image.blit(count_surf, count_rect)

    def update(self):
        if self.is_moving:
            dx = self.target_x - self.rect.centerx
            dy = self.target_y - self.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > self.speed:
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
                self.rect.x += move_x
                self.rect.y += move_y
            else:
                self.rect.centerx = self.target_x
                self.rect.centery = self.target_y
                self.is_moving = False
        else:
            # Gentle bounce when not moving
            self.bounce_time += self.bounce_speed
            new_offset = math.sin(self.bounce_time) * 1.5
            delta = new_offset - self.bounce_offset
            self.rect.y += delta
            self.bounce_offset = new_offset

    def update_count(self, count):
        self.count = count
        self.draw_character()
import pygame
import math
import numpy as np
from config import WIDTH, HEIGHT

class IsometricRenderer:
    def __init__(self):
        self.bowl_color = (200, 200, 220)
        self.bowl_highlight = (230, 230, 250)
        self.bowl_shadow = (170, 170, 190)
    
    def draw_mixing_bowl(self, screen, fill_level=0):
        """Draw a 3D mixing bowl with proper shading"""
        center_x = WIDTH // 2
        center_y = HEIGHT // 2 - 40  # Slightly above center
        
        # Bowl dimensions
        width = 200
        height = 140
        rim_thickness = 15
        
        # Create surfaces for the bowl parts
        bowl_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        
        # Draw bowl exterior (main body)
        points = [
            (10, rim_thickness),  # Top left
            (width + 10, rim_thickness),  # Top right
            (width - 20, height + 10),  # Bottom right
            (30, height + 10)  # Bottom left
        ]
        pygame.draw.polygon(bowl_surface, self.bowl_color, points)
        
        # Draw bowl interior
        interior_points = [
            (20, rim_thickness + 5),  # Top left
            (width, rim_thickness + 5),  # Top right
            (width - 30, height),  # Bottom right
            (40, height)  # Bottom left
        ]
        pygame.draw.polygon(bowl_surface, self.bowl_highlight, interior_points)
        
        # Draw rim highlight
        pygame.draw.ellipse(bowl_surface, self.bowl_highlight,
                          (10, 0, width, rim_thickness * 2))
        
        # Draw rim
        pygame.draw.ellipse(bowl_surface, self.bowl_color,
                          (10, 5, width, rim_thickness * 2), 3)
        
        # Add shading
        for i in range(3):
            alpha = 100 - i * 30
            shadow_color = (*self.bowl_shadow, alpha)
            pygame.draw.line(bowl_surface, shadow_color,
                           (30 + i*5, height + 5),
                           (width - 20 - i*5, height + 5), 2)
        
        # Draw bowl on screen
        screen.blit(bowl_surface, (center_x - width//2 - 10, center_y - height//2 - 10))
        
        # Draw fill level indicator
        if fill_level > 0:
            fill_height = int(height * 0.7 * fill_level)  # Max fill is 70% of bowl height
            fill_y = center_y + height//2 - fill_height
            fill_rect = pygame.Rect(center_x - width//2 + 40,
                                  fill_y,
                                  width - 70,
                                  fill_height)
            pygame.draw.rect(screen, (200, 200, 200, 100), fill_rect) 
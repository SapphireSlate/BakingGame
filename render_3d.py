import pygame
import math
import numpy as np
from config import WIDTH, HEIGHT

class IsometricRenderer:
    def __init__(self):
        self.angle = math.pi / 6  # 30 degrees for isometric view
        self.scale = 1.0
        self.camera_x = WIDTH // 2
        self.camera_y = HEIGHT // 2
        self.z_offset = 0
        
        # Isometric transformation matrix
        cos30 = math.cos(self.angle)
        sin30 = math.sin(self.angle)
        self.iso_matrix = np.array([
            [cos30, -cos30, 0],
            [sin30, sin30, -1],
            [0, 0, 1]
        ])
        
        # Lighting parameters
        self.light_direction = np.array([0.5, -0.5, -1.0])
        self.light_color = np.array([1.0, 0.95, 0.8])
        self.ambient_light = 0.3
        
    def project_point(self, x, y, z):
        """Convert 3D coordinates to 2D screen coordinates"""
        point = np.array([x, y, z])
        transformed = np.dot(self.iso_matrix, point)
        screen_x = self.camera_x + transformed[0] * self.scale
        screen_y = self.camera_y + transformed[1] * self.scale - z * self.z_offset
        return screen_x, screen_y
        
    def draw_floating_ingredient(self, screen, pos, color, size, hover_height=0):
        """Draw an ingredient with 3D floating effect"""
        x, y, z = pos
        
        # Add gentle floating animation
        z += math.sin(pygame.time.get_ticks() / 500) * 5 + hover_height
        
        # Project center point
        center_x, center_y = self.project_point(x, y, z)
        
        # Create gradient surface for 3D effect
        gradient_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Calculate lighting
        normal = np.array([0, 0, 1])
        light_intensity = max(0.2, np.dot(normal, -self.light_direction))
        
        # Apply lighting to color
        lit_color = [min(255, int(c * (self.ambient_light + light_intensity))) for c in color]
        
        # Draw main circle with lighting
        pygame.draw.circle(gradient_surface, (*lit_color, 255), (size, size), size)
        
        # Add highlight
        highlight_pos = (size + size * 0.3, size - size * 0.3)
        highlight_size = size * 0.4
        pygame.draw.circle(gradient_surface, (255, 255, 255, 100), highlight_pos, highlight_size)
        
        # Add shadow
        shadow_surface = pygame.Surface((size * 2, size * 0.5), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, 100)
        pygame.draw.ellipse(shadow_surface, shadow_color, shadow_surface.get_rect())
        screen.blit(shadow_surface, (center_x - size, center_y + size * 0.8))
        
        # Draw the ingredient
        screen.blit(gradient_surface, (center_x - size, center_y - size))
        
    def draw_mixing_bowl(self, screen, contents_height=0.0):
        """Draw a 3D mixing bowl with contents"""
        bowl_radius = 80
        bowl_height = 60
        rim_thickness = 10
        
        # Draw bowl shadow
        shadow_surface = pygame.Surface((bowl_radius * 3, bowl_radius), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, 60)
        pygame.draw.ellipse(shadow_surface, shadow_color, shadow_surface.get_rect())
        screen.blit(shadow_surface, (self.camera_x - bowl_radius * 1.5, self.camera_y + bowl_height))
        
        # Draw bowl contents if any
        if contents_height > 0:
            contents_points = []
            for angle in range(0, 360, 10):
                rad = math.radians(angle)
                x = math.cos(rad) * bowl_radius * 0.8
                y = math.sin(rad) * bowl_radius * 0.8
                z = -bowl_height * (1 - contents_height)
                screen_x, screen_y = self.project_point(x, y, z)
                contents_points.append((screen_x, screen_y))
            
            if contents_points:
                pygame.draw.polygon(screen, (200, 180, 160), contents_points)
        
        # Draw bowl rim
        rim_points = []
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = math.cos(rad) * bowl_radius
            y = math.sin(rad) * bowl_radius
            z = 0
            screen_x, screen_y = self.project_point(x, y, z)
            rim_points.append((screen_x, screen_y))
        
        if rim_points:
            pygame.draw.polygon(screen, (180, 180, 180), rim_points)
            pygame.draw.lines(screen, (120, 120, 120), True, rim_points, 3)
        
        # Draw bowl interior
        interior_points = []
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = math.cos(rad) * bowl_radius * 0.9
            y = math.sin(rad) * bowl_radius * 0.9
            z = -bowl_height
            screen_x, screen_y = self.project_point(x, y, z)
            interior_points.append((screen_x, screen_y))
        
        if interior_points:
            pygame.draw.polygon(screen, (150, 150, 150), interior_points)
            pygame.draw.lines(screen, (100, 100, 100), True, interior_points, 2)

    def draw_particle_effects(self, screen, particles):
        """Draw 3D particle effects"""
        for particle in particles:
            x, y, z = particle['position']
            size = particle['size']
            color = particle['color']
            alpha = particle['alpha']
            
            screen_x, screen_y = self.project_point(x, y, z)
            
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*color, alpha), (size, size), size)
            
            screen.blit(particle_surface, (screen_x - size, screen_y - size))

    def create_glass_panel(self, width, height, color=(255, 255, 255), alpha=128):
        """Create a modern glass-like panel with rounded corners and subtle gradient"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create base panel with transparency
        base_color = (*color, alpha)
        pygame.draw.rect(surface, base_color, (0, 0, width, height), border_radius=15)
        
        # Add subtle gradient overlay
        gradient = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(height):
            alpha = int(20 * (1 - i/height))
            pygame.draw.line(gradient, (255, 255, 255, alpha), (0, i), (width, i))
        
        # Add highlight at the top
        highlight_rect = pygame.Rect(5, 5, width-10, height//4)
        pygame.draw.rect(gradient, (255, 255, 255, 30), highlight_rect, border_radius=10)
        
        surface.blit(gradient, (0, 0))
        return surface 
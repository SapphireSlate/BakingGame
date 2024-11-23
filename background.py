import pygame
import math
import random
from config import WIDTH, HEIGHT

class Background:
    def __init__(self):
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.grid_size = 40
        self.perspective_points = []
        self.generate_perspective_grid()
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) 
                     for _ in range(100)]
        self.time = 0
        
    def generate_perspective_grid(self):
        # Create vanishing point
        vanishing_x = WIDTH // 2
        vanishing_y = HEIGHT // 2
        
        # Generate grid points with perspective
        for x in range(0, WIDTH + self.grid_size, self.grid_size):
            for y in range(0, HEIGHT + self.grid_size, self.grid_size):
                # Calculate perspective displacement
                dx = x - vanishing_x
                dy = y - vanishing_y
                distance = math.sqrt(dx*dx + dy*dy)
                perspective = 0.5 + distance / (WIDTH + HEIGHT)
                
                x_pos = vanishing_x + dx * perspective
                y_pos = vanishing_y + dy * perspective
                
                self.perspective_points.append((x_pos, y_pos))

    def update(self):
        self.time += 0.01
        # Update star positions for twinkling effect
        for i in range(len(self.stars)):
            if random.random() < 0.01:  # 1% chance to move each star
                self.stars[i] = (random.randint(0, WIDTH), random.randint(0, HEIGHT))

    def draw(self, screen):
        # Fill background with dark color
        self.surface.fill((10, 12, 20))
        
        # Draw subtle gradient
        gradient_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            alpha = int(25 * (1 - y/HEIGHT))  # Fade from bottom to top
            pygame.draw.line(gradient_surface, (30, 35, 50, alpha), (0, y), (WIDTH, y))
        self.surface.blit(gradient_surface, (0, 0))
        
        # Draw twinkling stars
        for star in self.stars:
            brightness = int(128 + 127 * math.sin(self.time + hash(star) % 360))
            pygame.draw.circle(self.surface, (brightness, brightness, brightness), star, 1)
        
        # Draw perspective grid with transparency
        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(len(self.perspective_points)):
            for j in range(i + 1, len(self.perspective_points)):
                if abs(i - j) < 10:  # Limit connections for performance
                    start = self.perspective_points[i]
                    end = self.perspective_points[j]
                    # Calculate distance-based alpha
                    distance = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
                    if distance < 100:  # Only draw nearby connections
                        alpha = int(50 * (1 - distance/100))
                        pygame.draw.line(grid_surface, (50, 55, 70, alpha), start, end, 1)
        
        self.surface.blit(grid_surface, (0, 0))
        
        # Add fog effect with proper alpha blending
        fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            alpha = int(5 + 20 * (y/HEIGHT))  # More fog at bottom
            pygame.draw.line(fog_surface, (20, 25, 35, alpha), (0, y), (WIDTH, y))
        
        self.surface.blit(fog_surface, (0, 0))
        
        # Finally, blit the complete background to the screen
        screen.blit(self.surface, (0, 0)) 
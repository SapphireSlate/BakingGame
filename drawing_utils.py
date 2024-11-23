import pygame
import math
from config import WIDTH, HEIGHT, GREEN, GRAY, DARK_GRAY, BLACK, WHITE

def draw_pentagon(surface, color, x, y, size):
    points = []
    for i in range(5):
        angle = math.pi * 2 * i / 5 - math.pi / 2
        points.append((x + size * math.cos(angle), y + size * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)

def draw_hexagon(surface, color, x, y, size):
    points = []
    for i in range(6):
        angle = math.pi * 2 * i / 6
        points.append((x + size * math.cos(angle), y + size * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)

def draw_ingredients(surface, game):
    # Draw all ingredient sprites
    game.ingredient_sprites.draw(surface)
    
    # Update ingredient counts
    for sprite in game.ingredient_sprites:
        sprite.update_count(game.ingredient_counts[sprite.name])

def draw_recipe(surface, name, x, y):
    # Create a semi-transparent background for the recipe text
    font = pygame.font.Font(None, 24)
    text = font.render(name, True, WHITE[:3])  # Use RGB format
    
    # Create a background surface with transparency and rounded corners
    bg_surface = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (20, 20, 40, 180), bg_surface.get_rect(), border_radius=8)
    
    # Draw the background and text
    surface.blit(bg_surface, (x - text.get_width()//2 - 10, y - text.get_height()//2 - 5))
    surface.blit(text, (x - text.get_width()//2, y - text.get_height()//2))

def draw_game(screen, game, animation_manager, dt=0):
    # Draw bowl contents first (moved to the right side)
    if game.current_ingredients:
        # Calculate dimensions for the box
        padding = 10
        line_height = 25  # Start with larger line height
        font_size = 30
        max_box_height = HEIGHT - 100  # Stop above upgrade menu
        
        # Calculate space needed for recipes
        recipes_height = len(game.discovered_recipes) * 80 + 20
        
        # Calculate available height for ingredients box
        available_height = HEIGHT - recipes_height - 120
        max_box_height = min(max_box_height, available_height)
        
        # Calculate initial dimensions
        font = pygame.font.Font(None, font_size)
        
        # Get the maximum width needed for the text
        max_width = 0
        for ing in set(game.current_ingredients):
            count = game.current_ingredients.count(ing)
            text = font.render(f"{ing} x{count}", True, WHITE[:3])
            max_width = max(max_width, text.get_width())
        
        # Set box dimensions with constraints
        box_width = min(300, max_width + (padding * 2))
        
        # Calculate total content height needed
        num_ingredients = len(set(game.current_ingredients))
        content_height = (num_ingredients * line_height) + (padding * 3) + 30
        
        # Adjust font size to fit all ingredients in available space
        while content_height > max_box_height and font_size > 24:  # Increased minimum font size
            font_size -= 2
            font = pygame.font.Font(None, font_size)
            line_height = max(20, line_height - 2)  # Keep line height proportional but not too small
            content_height = (num_ingredients * line_height) + (padding * 3) + 30
        
        box_height = min(max_box_height, content_height)
        
        # Position on right side, below recipes, but above upgrades
        box_x = WIDTH - box_width - 40
        box_y = 50 + recipes_height
        
        # Create and draw the background box with transparency
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (20, 20, 40, 200), (0, 0, box_width, box_height), border_radius=12)
        screen.blit(box_surface, (box_x, box_y))
        
        # Draw "Bowl Contents:" header
        header_text = font.render("Bowl Contents:", True, WHITE[:3])
        header_bg = pygame.Surface((header_text.get_width() + 20, header_text.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(header_bg, (40, 40, 60, 180), header_bg.get_rect(), border_radius=8)
        
        header_x = box_x + (box_width - header_text.get_width()) // 2
        screen.blit(header_bg, (header_x - 10, box_y + padding - 5))
        screen.blit(header_text, (header_x, box_y + padding))
        
        # Draw all ingredients list (scaled to fit)
        y_offset = box_y + padding * 2 + 30
        for ing in set(game.current_ingredients):
            count = game.current_ingredients.count(ing)
            text = font.render(f"{ing} x{count}", True, WHITE[:3])
            
            # Create background for each ingredient line
            text_bg = pygame.Surface((text.get_width() + 20, text.get_height() + 6), pygame.SRCALPHA)
            pygame.draw.rect(text_bg, (30, 30, 50, 150), text_bg.get_rect(), border_radius=6)
            
            text_x = box_x + (box_width - text.get_width()) // 2
            screen.blit(text_bg, (text_x - 10, y_offset - 3))
            screen.blit(text, (text_x, y_offset))
            y_offset += line_height
    
    # Draw ingredients
    draw_ingredients(screen, game)
    
    # Draw recipes on right side
    for i, recipe in enumerate(game.discovered_recipes):
        draw_recipe(screen, recipe, WIDTH - 100, 50 + i * 80)
    
    # Draw remaining UI elements
    draw_upgrades(screen, game)
    animation_manager.update_animations(screen, game, dt)

def draw_upgrades(screen, game):
    upgrade_width = WIDTH // len(game.upgrades)
    for i, (name, info) in enumerate(game.upgrades.items()):
        # Draw solid rectangle without rounded corners
        if name in game.active_upgrades:
            pygame.draw.rect(screen, (*GREEN[:3], 255), (i * upgrade_width, HEIGHT - 50, upgrade_width, 50))
            text = pygame.font.Font(None, 20).render(f"{info['icon']} {name} (Active)", True, WHITE[:3])
        else:
            pygame.draw.rect(screen, (*GRAY[:3], 255), (i * upgrade_width, HEIGHT - 50, upgrade_width, 50))
            text = pygame.font.Font(None, 20).render(f"{info['icon']} {name}: {info['cost']} BC", True, WHITE[:3])
        
        # Center text in button
        text_x = i * upgrade_width + (upgrade_width - text.get_width()) // 2
        screen.blit(text, (text_x, HEIGHT - 35))

def update_bakecoin_display(screen, game):
    font = pygame.font.Font(None, 36)
    bakecoin_text = f"Bakecoin: {game.bakecoin}"
    text_surface = font.render(bakecoin_text, True, (255, 255, 255))
    
    # Create background with transparency and rounded corners
    bg_surface = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (20, 20, 40, 180), bg_surface.get_rect(), border_radius=10)
    
    x = WIDTH//2 - text_surface.get_width()//2
    y = 50
    screen.blit(bg_surface, (x - 10, y - 5))
    screen.blit(text_surface, (x, y))

    if game.customer_order:
        order_y = 90
        order_text = f"Order: {game.customer_order}"
        order_surface = font.render(order_text, True, (255, 255, 255))
        
        order_bg = pygame.Surface((order_surface.get_width() + 20, order_surface.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(order_bg, (20, 20, 40, 180), order_bg.get_rect(), border_radius=10)
        
        x = WIDTH//2 - order_surface.get_width()//2
        screen.blit(order_bg, (x - 10, order_y - 5))
        screen.blit(order_surface, (x, order_y))

import pygame
import math
from config import WIDTH, HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY

def draw_pentagon(screen, x, y, size, color):
    """Draw a pentagon shape"""
    points = []
    for i in range(5):
        angle = math.pi * 2 * i / 5 - math.pi / 2
        points.append((
            x + math.cos(angle) * size,
            y + math.sin(angle) * size
        ))
    pygame.draw.polygon(screen, color, points)
    return points

def draw_hexagon(screen, x, y, size, color):
    """Draw a hexagon shape"""
    points = []
    for i in range(6):
        angle = math.pi * 2 * i / 6
        points.append((
            x + math.cos(angle) * size,
            y + math.sin(angle) * size
        ))
    pygame.draw.polygon(screen, color, points)
    return points

def draw_ingredients(screen, game):
    """Draw ingredients using the modern UI system"""
    game.ui.draw_ingredient_grid(screen, game)

def draw_recipe(screen, recipe_name, ingredients, x, y, width, height, selected=False):
    """Draw a recipe card using the modern UI system"""
    if hasattr(screen, 'ui'):
        screen.ui.draw_recipe_card(screen, recipe_name, ingredients, x, y, width, height, selected)

def draw_game(screen, game, animation_manager, dt):
    """Main game drawing function using modern UI"""
    # Draw game UI using the modern system
    game.ui.draw_game_ui(screen, game)
    
    # Update and draw animations
    animation_manager.update_animations(screen, game, dt)

def draw_upgrades(screen, game):
    """Draw upgrade options using modern UI"""
    if not hasattr(game, 'ui'):
        return
        
    upgrade_height = 50
    spacing = 10
    total_width = WIDTH
    upgrade_width = total_width // len(game.upgrades)
    
    y = HEIGHT - upgrade_height - spacing
    
    for i, (name, upgrade) in enumerate(game.upgrades.items()):
        x = i * upgrade_width
        
        # Create upgrade button rect
        button_rect = pygame.Rect(x + spacing//2, y, upgrade_width - spacing, upgrade_height)
        
        # Determine button state
        is_active = name in game.active_upgrades
        is_affordable = game.bakecoin >= upgrade['cost']
        
        # Draw button with appropriate styling
        game.ui.draw_button(
            screen,
            button_rect,
            f"{upgrade['icon']} {name} ({upgrade['cost']}🪙)",
            color=game.ui.colors['success'] if is_active else (
                game.ui.colors['panel'] if is_affordable else game.ui.colors['panel_light']
            ),
            hover=button_rect.collidepoint(pygame.mouse.get_pos()) and not is_active and is_affordable
        )

def update_bakecoin_display(screen, game):
    """Update bakecoin display using modern UI"""
    if hasattr(game, 'ui'):
        game.ui.draw_top_bar(screen, game)

def create_gradient_surface(width, height, start_color, end_color):
    """Create a vertical gradient surface"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        progress = y / height
        color = [
            int(start_color[i] + (end_color[i] - start_color[i]) * progress)
            for i in range(3)
        ]
        pygame.draw.line(surface, color, (0, y), (width, y))
    return surface

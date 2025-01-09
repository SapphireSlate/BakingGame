import pygame
import sys
from game_state import Game
from drawing_utils import draw_pentagon, draw_hexagon, draw_ingredients, draw_recipe, draw_game, draw_upgrades, update_bakecoin_display
from game_logic import handle_baking_process, generate_customer_order, trigger_kitchen_disaster
from ui import draw_intro_screen, handle_dialogue, draw_recipe_book_screen
from config import WIDTH, HEIGHT, WHITE, BLACK
from animation import AnimationManager, flash_screen_red, PopupText
from background import Background
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Hide Pygame welcome message
os.environ['SDL_VIDEODRIVER'] = 'cocoa'  # For MacOS
os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'  # Helps with compositing

if sys.platform == 'darwin':  # Fixed: using sys.platform instead of os.platform
    os.environ['NSSupportsAutomaticGraphicsSwitching'] = 'True'

# Main game loop and high-level logic

def handle_events(game, animation_manager):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                handle_mouse_click(event, game, animation_manager)
                
        elif event.type == pygame.KEYDOWN:
            handle_keydown(event, game)
            
        elif event.type == pygame.USEREVENT:
            # Reset click states for all sprites
            for sprite in game.ingredient_sprites:
                sprite.reset_click()
    
    return True

def handle_keydown(event, game):
    print(f"Key pressed: {pygame.key.name(event.key)}, Game state: {game.state}, Baking: {game.baking}")  # Debug print
    if game.state == "main_game":
        if event.key == pygame.K_RETURN and not game.baking and len(game.current_ingredients) > 0:
            print("Starting baking process...")  # Debug print
            game.baking = True  # Only set the flag here, don't process baking
        elif event.key == pygame.K_r:
            game.replenish_ingredients()
    elif game.state == "intro":
        if event.key == pygame.K_RETURN:
            game.state = "choose_difficulty"
            print("Transitioning to choose_difficulty")  # Debug print
    elif game.state == "choose_difficulty":
        if event.key in [pygame.K_e, pygame.K_n, pygame.K_h]:
            game.choose_difficulty(event.key)
            print(f"Difficulty chosen: {game.difficulty}")  # Debug print

def handle_mouse_click(event, game, animation_manager):
    if game.state == "main_game":
        x, y = event.pos
        
        # Check for replenish button click
        button_x, button_y = 20, HEIGHT - 100
        button_width, button_height = 200, 40
        if (button_x <= x <= button_x + button_width and 
            button_y <= y <= button_y + button_height):
            if game.replenish_ingredients():
                animation_manager.add_popup_message("Ingredients replenished!", color=(0, 255, 0))
            else:
                animation_manager.add_popup_message("Not enough Bakecoin!", color=(255, 0, 0))
            return
        
        # Handle upgrade purchases
        if y >= HEIGHT - 50:
            if game.purchase_upgrade(event.pos):
                animation_manager.add_popup_message("Upgrade purchased!", color=(0, 255, 0))
            return
        
        # Handle ingredient clicks
        clicked_ingredient = False
        for sprite in game.ingredient_sprites:
            if sprite.rect.collidepoint(event.pos):
                if sprite.count > 0:  # Only handle click if we have ingredients left
                    if not animation_manager.is_animating:  # Check if we can add more animations
                        sprite.handle_click()  # Handle visual feedback
                        ing, start_x, start_y = game.handle_ingredient_click(x, y)
                        if ing:
                            animation_manager.add_ingredient_animation(ing, start_x, start_y)
                    else:
                        animation_manager.add_popup_message("Wait for ingredients to settle!", color=(255, 165, 0))
                else:
                    animation_manager.add_popup_message(f"Out of {sprite.name}!", color=(255, 0, 0))
                clicked_ingredient = True
                break
        
        if not clicked_ingredient:
            # Handle clicks on the bowl or other game areas
            bowl_x = WIDTH // 2
            bowl_y = HEIGHT // 2
            bowl_radius = 80  # Approximate bowl click area
            
            # Check if click is within bowl area
            dx = x - bowl_x
            dy = y - bowl_y
            if (dx * dx + dy * dy) <= bowl_radius * bowl_radius:
                if len(game.current_ingredients) > 0:
                    game.baking = True
                    animation_manager.start_baking()
                else:
                    animation_manager.add_popup_message("Add ingredients first!", color=(255, 165, 0))

def main():
    # Initialize Pygame with error handling
    try:
        pygame.init()
        if pygame.init()[1] > 0:  # Check if there were any initialization errors
            print(f"Warning: {pygame.init()[1]} Pygame modules failed to initialize")
            
        if not pygame.display.get_init():
            print("Failed to initialize Pygame display")
            return
            
        pygame.font.init()
        if not pygame.font.get_init():
            print("Failed to initialize Pygame font module")
            return
            
    except Exception as e:
        print(f"Pygame initialization error: {e}")
        return

    # Set up display
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Advanced Baking Game")
    except pygame.error as e:
        print(f"Failed to set up display: {e}")
        pygame.quit()
        return

    # Initialize game objects
    try:
        animation_manager = AnimationManager()
        game = Game(animation_manager)
        background = Background()
        clock = pygame.time.Clock()
        popup_text = None
        disaster_duration = 3  # seconds
        disaster_timer = 0
    except Exception as e:
        print(f"Failed to initialize game objects: {e}")
        pygame.quit()
        return

    # Main game loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        try:
            running = handle_events(game, animation_manager)
            if not running:
                break

            background.update()
            background.draw(screen)

            if game.state == "intro":
                draw_intro_screen(screen)
            elif game.state == "choose_difficulty":
                handle_dialogue(screen, game)
            elif game.state == "main_game":
                game.update()
                
                if game.kitchen_disaster:
                    if disaster_timer == 0:
                        animation_manager.trigger_disaster_animation(game.kitchen_disaster, game)
                        ingredients_affected = game.handle_disaster_animation(animation_manager)
                        if ingredients_affected:
                            flash_screen_red(screen)
                            game.current_ingredients.clear()
                            animation_manager.reset_bowl()
                        disaster_timer = disaster_duration
                    else:
                        disaster_timer -= dt
                        if disaster_timer <= 0:
                            disaster_timer = 0
                            game.kitchen_disaster = None
                            animation_manager.clear_disaster_animations()

                if game.baking:  # Handle baking process only here
                    result, bakecoin_change = game.handle_baking_process()
                    popup_text = PopupText(result, WIDTH // 2, HEIGHT // 2)
                    game.baking = False
                    print(f"Baking complete. Result: {result}, Bakecoin change: {bakecoin_change}")  # Debug print

                draw_game(screen, game, animation_manager, dt)
                update_bakecoin_display(screen, game)

                if popup_text:
                    popup_text.update()
                    popup_text.draw(screen)
                    if popup_text.is_finished():
                        popup_text = None

            pygame.display.flip()

        except Exception as e:
            print(f"Error in game loop: {e}")
            animation_manager.add_error_message(f"Game error: {str(e)}")
            # Don't crash, continue running

    # Cleanup
    try:
        pygame.font.quit()
        pygame.quit()
    except:
        pass

if __name__ == "__main__":
    main()

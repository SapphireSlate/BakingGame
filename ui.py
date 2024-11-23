import pygame
from config import WIDTH, HEIGHT, BLACK, WHITE

def draw_intro_screen(screen):
    screen.fill(BLACK)
    
    # Create semi-transparent background for title
    title_font = pygame.font.Font(None, 64)
    title_text = title_font.render("Bakecoin", True, WHITE, None)
    
    # Create background surface for title
    title_bg = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 20), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (20, 20, 40, 180), title_bg.get_rect())
    
    # Position and draw title
    title_x = WIDTH // 2 - title_text.get_width() // 2
    title_y = HEIGHT // 2
    screen.blit(title_bg, (title_x - 20, title_y - 10))
    screen.blit(title_text, (title_x, title_y))
    
    # Create semi-transparent background for start text
    start_font = pygame.font.Font(None, 32)
    start_text = start_font.render("Press ENTER to start", True, WHITE, None)
    
    # Create background surface for start text
    start_bg = pygame.Surface((start_text.get_width() + 40, start_text.get_height() + 20), pygame.SRCALPHA)
    pygame.draw.rect(start_bg, (20, 20, 40, 180), start_bg.get_rect())
    
    # Position and draw start text
    start_x = WIDTH // 2 - start_text.get_width() // 2
    start_y = HEIGHT * 3 // 4
    screen.blit(start_bg, (start_x - 20, start_y - 10))
    screen.blit(start_text, (start_x, start_y))

def handle_dialogue(screen, game):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 32)
    if game.state == "intro":
        text = "Welcome to Bakecoin! Press ENTER to start."
    elif game.state == "choose_difficulty":
        text = "Choose your difficulty: Easy (E), Normal (N), or Hard (H)."
    elif game.state == "main_game":
        text = "Click ingredients to add them to the bowl. Press ENTER to bake."
    else:
        return

    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    print(f"Handling dialogue for state: {game.state}")  # Debug print

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if game.state == "intro" and event.key == pygame.K_RETURN:
                    game.state = "choose_difficulty"
                    waiting = False
                elif game.state == "choose_difficulty":
                    if event.key in [pygame.K_e, pygame.K_n, pygame.K_h]:
                        game.choose_difficulty(event.key)
                        waiting = False
    
    print(f"Dialogue ended. Game state: {game.state}, Bakecoin: {game.bakecoin}")  # Debug print

def draw_recipe_book_screen(screen, game):
    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 24)
    y = 50
    for recipe in game.discovered_recipes:
        text = font.render(recipe, True, (0, 0, 0))
        screen.blit(text, (50, y))
        y += 30
    
    back_text = font.render("Press B to go back", True, (0, 0, 0))
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

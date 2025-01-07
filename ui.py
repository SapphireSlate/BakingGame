import pygame
from config import WIDTH, HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY

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

class VolumeControl:
    def __init__(self, x, y, width=200):
        self.x = x
        self.y = y
        self.width = width
        self.height = 150
        self.visible = False
        self.sliders = {
            'master': {'value': 0.8, 'y_offset': 20, 'label': 'Master Volume'},
            'mixing': {'value': 0.4, 'y_offset': 50, 'label': 'Mixing Sounds'},
            'baking': {'value': 0.3, 'y_offset': 80, 'label': 'Baking Sounds'},
            'effects': {'value': 0.5, 'y_offset': 110, 'label': 'Effects'},
            'ambient': {'value': 0.1, 'y_offset': 140, 'label': 'Ambient'}
        }
        self.active_slider = None
        self.font = pygame.font.Font(None, 24)
        
    def toggle(self):
        self.visible = not self.visible
    
    def handle_mouse_down(self, pos):
        if not self.visible:
            return False
            
        mouse_x, mouse_y = pos
        if not (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):
            self.visible = False
            return False
        
        # Check if clicked on a slider
        for channel, slider in self.sliders.items():
            slider_y = self.y + slider['y_offset']
            if slider_y - 5 <= mouse_y <= slider_y + 5:
                self.active_slider = channel
                # Update value based on x position
                value = (mouse_x - self.x) / self.width
                self.sliders[channel]['value'] = max(0.0, min(1.0, value))
                return True
        return True
    
    def handle_mouse_up(self):
        self.active_slider = None
    
    def handle_mouse_motion(self, pos):
        if not self.visible or not self.active_slider:
            return
            
        mouse_x, _ = pos
        # Update active slider value
        value = (mouse_x - self.x) / self.width
        self.sliders[self.active_slider]['value'] = max(0.0, min(1.0, value))
    
    def get_volume(self, channel):
        return self.sliders[channel]['value']
    
    def draw(self, screen):
        if not self.visible:
            return
            
        # Draw background panel
        panel = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*DARK_GRAY, 230), 
                        (0, 0, self.width + 20, self.height + 20), 
                        border_radius=10)
        screen.blit(panel, (self.x - 10, self.y - 10))
        
        # Draw title
        title = self.font.render("Volume Settings", True, WHITE)
        screen.blit(title, (self.x + self.width//2 - title.get_width()//2, self.y - 5))
        
        # Draw each slider
        for channel, slider in self.sliders.items():
            # Draw label
            label = self.font.render(slider['label'], True, WHITE)
            screen.blit(label, (self.x, self.y + slider['y_offset'] - 15))
            
            # Draw slider track
            pygame.draw.line(screen, GRAY,
                           (self.x, self.y + slider['y_offset']),
                           (self.x + self.width, self.y + slider['y_offset']),
                           2)
            
            # Draw slider handle
            handle_x = self.x + self.width * slider['value']
            pygame.draw.circle(screen, WHITE,
                             (int(handle_x), self.y + slider['y_offset']),
                             6)
            
            # Draw percentage
            percent = f"{int(slider['value'] * 100)}%"
            percent_text = self.font.render(percent, True, WHITE)
            screen.blit(percent_text, 
                       (self.x + self.width + 5, 
                        self.y + slider['y_offset'] - 8))

# Add volume control to existing Button class
class Button:
    def __init__(self, x, y, width, height, text, action=None, color=GRAY, hover_color=DARK_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.action:
                self.action()
                return True
        return False

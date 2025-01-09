import pygame
import random
import math
import mixbox

# Constants
WIDTH = 800
HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Ingredient colors
INGREDIENT_COLORS = {
    'Flour': (255, 250, 245),        # Warm white
    'Sugar': (255, 252, 240),        # Cream white
    'Eggs': (255, 215, 100),         # Rich egg yolk yellow
    'Milk': (250, 250, 255),         # Cool white with slight blue tint
    'Butter': (255, 225, 150),       # Rich butter yellow
    'Cocoa': (60, 30, 15),           # Deep chocolate brown
    'Vanilla': (255, 235, 200),      # Warm vanilla cream
    'Baking Powder': (245, 245, 245), # Pure white
    'Powdered Sugar': (255, 255, 252), # Bright white
    'Chocolate Chips': (45, 25, 10),  # Dark chocolate
    'Condensed Milk': (255, 245, 220), # Rich cream
    'Meringue': (255, 252, 250),     # Pure white with slight warmth
    'Frosting': (255, 255, 255)      # Pure white base for mixing
}

# Ingredient types for animation behavior
INGREDIENT_TYPES = {
    'Flour': 'dry',
    'Sugar': 'dry',
    'Cocoa': 'dry',
    'Baking Powder': 'dry',
    'Powdered Sugar': 'dry',
    'Chocolate Chips': 'solid',
    'Milk': 'liquid',
    'Eggs': 'liquid',
    'Butter': 'solid',
    'Vanilla': 'liquid',
    'Condensed Milk': 'liquid',
    'Meringue': 'solid',
    'Frosting': 'solid'
}

class PopupText:
    def __init__(self, text, x, y, color=(255, 0, 0), size=24, duration=2.0, rise_speed=1.0):
        self.font = pygame.font.Font(None, size)
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.fade_speed = 255 / (duration * 60)  # 60 FPS
        self.rise_speed = rise_speed
        self.original_y = y

    def update(self):
        """Update the popup text position and alpha"""
        self.alpha = max(0, self.alpha - self.fade_speed)
        self.y = self.y - self.rise_speed
        return self.alpha > 0

    def draw(self, screen):
        """Draw the popup text with current alpha value"""
        if self.alpha <= 0:
            return
            
        text_surface = self.font.render(self.text, True, self.color)
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, int(self.alpha)))
        text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)

    def is_finished(self):
        """Check if the popup text has finished displaying"""
        return self.alpha <= 0

class AnimationManager:
    def __init__(self):
        self.shake_duration = 0
        self.shake_intensity = 0
        self.baking_effect = BakingEffect()
        self.popup_messages = []
        self.animated_ingredients = []
        self.mixing_layers = []
        self.ghibli_effects = GhibliMixingEffect()
        self.is_baking = False
        self.bowl_width = 160
        self.bowl_height = 120
        self._is_animating = False
        self.total_ingredient_volume = 0
        self.max_ingredient_volume = 1000  # Maximum volume the bowl can hold
        self.current_bowl_level = 0  # Current fill level (0 to 1)
        self.max_concurrent_animations = 5  # Maximum number of concurrent animations
        self.disaster_effects = []  # List to store disaster effects
        self.disaster_duration = 3.0  # Duration of disaster effects in seconds

    def reset_bowl(self):
        """Reset the bowl state"""
        self.mixing_layers.clear()
        self.animated_ingredients.clear()
        self.total_ingredient_volume = 0
        self.current_bowl_level = 0
        self.is_baking = False
        self._is_animating = False

    def add_ingredient_volume(self, ingredient_type):
        """Calculate and add ingredient volume"""
        # Different ingredients have different volumes
        volume_map = {
            'dry': 100,    # Flour, sugar, etc.
            'liquid': 150, # Milk, eggs, etc.
            'solid': 80    # Chocolate chips, butter chunks
        }
        
        ingredient_volume = volume_map.get(INGREDIENT_TYPES.get(ingredient_type, 'dry'), 100)
        if self.total_ingredient_volume + ingredient_volume <= self.max_ingredient_volume:
            self.total_ingredient_volume += ingredient_volume
            self.current_bowl_level = min(1.0, self.total_ingredient_volume / self.max_ingredient_volume)
            return True
        return False

    @property
    def is_animating(self):
        """Check if any animations are currently playing"""
        # Only consider as blocking if we have too many active animations
        return len(self.animated_ingredients) >= self.max_concurrent_animations

    def update_animations(self, screen, game, dt):
        """Update all animations"""
        if self.shake_duration > 0:
            self.shake_duration -= 1

        # Update ingredient animations
        ingredients_to_remove = []
        for ingredient in self.animated_ingredients:
            if ingredient.update(self.current_bowl_level):
                ingredients_to_remove.append(ingredient)
                # When ingredient settles, update the mixing layers
                self.update_mixing_layers(ingredient)

        # Remove settled ingredients
        for ingredient in ingredients_to_remove:
            self.animated_ingredients.remove(ingredient)

        # Update mixing animations if we have ingredients
        if self.mixing_layers:
            self.update_mixing_animation(dt)

        # Update baking animations
        if self.is_baking:
            self.baking_effect.update()
            if self.baking_effect.is_complete():
                self.is_baking = False
                game.on_baking_complete()

        # Update effects
        self.ghibli_effects.update(dt)

        # Update popup messages
        self.popup_messages = [msg for msg in self.popup_messages if msg.update()]

        # Draw everything
        self.draw(screen)

    def update_mixing_layers(self, settled_ingredient):
        """Update mixing layers when an ingredient settles"""
        # Create a new layer if it doesn't exist
        layer_exists = False
        for layer in self.mixing_layers:
            if layer.ingredient == settled_ingredient.ingredient:
                layer.y_offset = self.get_layer_height()
                layer_exists = True
                break
        
        if not layer_exists:
            new_layer = MixingLayer(settled_ingredient.ingredient, self.get_layer_height())
            self.mixing_layers.append(new_layer)

    def get_layer_height(self):
        """Calculate the height for new layers based on current bowl level"""
        return (self.bowl_height / 2) * (1 - self.current_bowl_level)

    def add_ingredient_animation(self, ingredient, start_x, start_y):
        """Add a new ingredient animation"""
        if len(self.animated_ingredients) >= self.max_concurrent_animations:
            self.add_popup_message("Wait for ingredients to settle!", color=(255, 165, 0))
            return False
            
        if not self.add_ingredient_volume(ingredient):
            self.add_popup_message("Bowl is full!", color=(255, 0, 0))
            return False

        # Calculate target Y based on current bowl level and existing animations
        base_target_y = HEIGHT//2 + (self.bowl_height//2 * (1 - self.current_bowl_level))
        
        # Add some vertical spacing between ingredients
        spacing = 10
        target_y = base_target_y - (len(self.animated_ingredients) * spacing)

        new_ingredient = AnimatedIngredient(
            ingredient, 
            start_x, 
            start_y, 
            target_y=target_y
        )
        self.animated_ingredients.append(new_ingredient)
        
        # Create a new mixing layer
        new_layer = MixingLayer(ingredient, self.current_bowl_level)
        self.mixing_layers.append(new_layer)
        
        return True

    def draw_mixing_bowl(self, screen):
        """Draw the mixing bowl with current fill level"""
        # Draw bowl outline
        bowl_color = DARK_GRAY
        bowl_thickness = 3
        
        # Calculate bowl dimensions based on fill level
        bowl_rect = pygame.Rect(
            WIDTH//2 - self.bowl_width//2,
            HEIGHT//2 - self.bowl_height//2,
            self.bowl_width,
            self.bowl_height
        )
        
        # Draw filled bowl background
        pygame.draw.ellipse(screen, GRAY, bowl_rect)
        
        # Draw fill level indicator
        if self.current_bowl_level > 0:
            fill_height = int(self.bowl_height * self.current_bowl_level)
            fill_rect = pygame.Rect(
                WIDTH//2 - self.bowl_width//2,
                HEIGHT//2 + self.bowl_height//2 - fill_height,
                self.bowl_width,
                fill_height
            )
            fill_color = self.get_mixed_color()
            pygame.draw.ellipse(screen, fill_color, fill_rect)
        
        # Draw bowl outline
        pygame.draw.ellipse(screen, bowl_color, bowl_rect, bowl_thickness)
        
        # Draw bowl rim
        rim_height = 20
        rim_rect = pygame.Rect(
            WIDTH//2 - self.bowl_width//2,
            HEIGHT//2 - self.bowl_height//2 - rim_height//2,
            self.bowl_width,
            rim_height
        )
        pygame.draw.ellipse(screen, bowl_color, rim_rect, bowl_thickness)

    def get_mixed_color(self):
        """Get the current mixed color of all ingredients"""
        if not self.mixing_layers:
            return GRAY
        
        mixed_color = self.mixing_layers[0].color
        for layer in self.mixing_layers[1:]:
            mixed_color = mix_colors(mixed_color, layer.color)
        return mixed_color

    def update_mixing_animation(self, dt):
        """Update the mixing animation"""
        # Update each layer
        for layer in self.mixing_layers:
            layer.update(dt)
            
            # Add Ghibli effects during mixing
            if random.random() < 0.1:
                self.ghibli_effects.add_sparkle(
                    WIDTH/2 + random.uniform(-50, 50),
                    HEIGHT/2 + random.uniform(-20, 20)
                )
                if random.random() < 0.3:
                    self.ghibli_effects.add_swirl(
                        WIDTH/2 + random.uniform(-30, 30),
                        HEIGHT/2 + random.uniform(-15, 15),
                        layer.color
                    )

    def add_error_message(self, message, color=(255, 0, 0)):
        """Add an error message as a popup"""
        self.popup_messages.append(
            PopupText(
                message,
                WIDTH // 2,
                HEIGHT // 2,
                color=color,
                size=24,
                duration=3.0,
                rise_speed=1.0
            )
        )

    def add_popup_message(self, message, color=(0, 0, 0), size=36, duration=2.0):
        """Add a popup message"""
        self.popup_messages.append(
            PopupText(
                message,
                WIDTH // 2,
                HEIGHT // 2,
                color=color,
                size=size,
                duration=duration,
                rise_speed=2.0
            )
        )

    def start_baking(self):
        """Start the baking process"""
        if not self.is_baking:
            self.is_baking = True
            self.baking_effect = BakingEffect()

    def stop_baking(self):
        """Stop the baking process"""
        if self.is_baking:
            self.is_baking = False

    def draw(self, screen):
        """Draw all animations"""
        # Draw mixing bowl
        self.draw_mixing_bowl(screen)
        
        # Draw mixing layers
        for layer in self.mixing_layers:
            layer.draw(screen, WIDTH//2, HEIGHT//2, self.bowl_width, self.bowl_height)
        
        # Draw ingredient animations
        for ingredient in self.animated_ingredients:
            ingredient.draw(screen)
        
        # Draw Ghibli effects
        self.ghibli_effects.draw(screen)
        
        # Draw baking effects
        if self.is_baking:
            self.baking_effect.draw(screen, WIDTH//2, HEIGHT//2)
        
        # Draw popup messages
        for msg in self.popup_messages:
            msg.draw(screen)

    def trigger_disaster_animation(self, disaster_type, game):
        """Start a disaster animation"""
        if disaster_type == "Oven malfunction":
            self.shake_duration = 60  # 1 second at 60 FPS
            self.shake_intensity = 5
            self.add_popup_message("Oven malfunction!", color=(255, 0, 0))
            if self.is_baking:
                self.stop_baking()
        
        elif disaster_type == "Ingredient spill":
            # Add spill particles
            for _ in range(10):
                self.disaster_effects.append({
                    'type': 'spill',
                    'x': WIDTH//2 + random.randint(-50, 50),
                    'y': HEIGHT//2,
                    'dx': random.uniform(-2, 2),
                    'dy': random.uniform(-1, 3),
                    'color': GRAY,
                    'life': 1.0
                })
            self.add_popup_message("Ingredients spilled!", color=(255, 0, 0))
        
        elif disaster_type == "Power outage":
            self.disaster_effects.append({
                'type': 'blackout',
                'alpha': 0,
                'target_alpha': 180,
                'duration': self.disaster_duration
            })
            self.add_popup_message("Power outage!", color=(255, 0, 0))
            if self.is_baking:
                self.stop_baking()

    def clear_disaster_animations(self):
        """Clear all disaster animations"""
        self.disaster_effects.clear()
        self.shake_duration = 0
        self.shake_intensity = 0

def safe_color_mix(color1, color2):
    """Safely mix two colors with error handling using Mixbox"""
    try:
        # Ensure both colors are in RGB format
        c1 = ensure_rgb(color1)
        c2 = ensure_rgb(color2)
        
        # Convert colors from 0-255 range to 0-1 range for Mixbox
        c1_norm = [c/255 for c in c1]
        c2_norm = [c/255 for c in c2]
        
        # Mix colors using Mixbox's pigment-based mixing
        mixed = mixbox.mixLab(c1_norm, c2_norm)
        
        # Convert back to 0-255 range and ensure minimum brightness
        mixed_rgb = tuple(max(30, int(c * 255)) for c in mixed)
        return mixed_rgb
    except Exception as e:
        # Fallback to simple averaging if Mixbox fails
        return tuple(max(30, (c1 + c2) // 2) for c1, c2 in zip(ensure_rgb(color1), ensure_rgb(color2)))

def mix_colors(color1, color2, ratio=0.5):
    """Mix colors using Mixbox's realistic pigment mixing"""
    # Cache for mixed colors to avoid recalculating
    cache_key = (color1, color2, ratio)
    if hasattr(mix_colors, 'cache') and cache_key in mix_colors.cache:
        return mix_colors.cache[cache_key]
    
    # Ensure we're only using RGB components, not alpha
    rgb1 = color1[:3] if len(color1) > 3 else color1
    rgb2 = color2[:3] if len(color2) > 3 else color2
    
    try:
        # Convert to 0-1 range for Mixbox
        c1_norm = [c/255 for c in rgb1]
        c2_norm = [c/255 for c in rgb2]
        
        # Mix using Mixbox
        mixed = mixbox.mixLab(c1_norm, c2_norm)
        
        # Convert back to 0-255 range and ensure minimum brightness
        mixed_rgb = tuple(max(30, int(c * 255)) for c in mixed)
        
        # Cache the result
        if not hasattr(mix_colors, 'cache'):
            mix_colors.cache = {}
        mix_colors.cache[cache_key] = mixed_rgb
        
        return mixed_rgb
    except Exception as e:
        # Fallback to simple linear interpolation
        mixed_rgb = tuple(
            max(30, int(c1 * (1 - ratio) + c2 * ratio))
            for c1, c2 in zip(rgb1, rgb2)
        )
        return mixed_rgb

def ensure_rgb(color):
    """Ensure color is in RGB format (3 components)"""
    if len(color) > 3:
        return color[:3]
    return color

class BakingEffect:
    def __init__(self, initial_color=(200, 200, 200), target_color=(139, 69, 19), bowl_width=150, bowl_height=100):
        self.initial_color = initial_color
        self.target_color = target_color
        self.bowl_width = bowl_width
        self.bowl_height = bowl_height
        self.baking_progress = 0
        self.smoke_particles = []
        self.splash_particles = []
        self.heat_distortion = 0
        self.rising_amount = 0
        self.bubbles = []
        self.steam_particles = []
        self.baking_duration = 5.0  # Baking takes 5 seconds
        self.baking_timer = 0
        self.baking_complete = False

    def is_complete(self):
        """Check if baking is complete"""
        return self.baking_complete

    def update(self):
        """Update all particle effects"""
        if self.baking_complete:
            return

        # Update baking timer
        self.baking_timer += 1/60  # Assuming 60 FPS
        if self.baking_timer >= self.baking_duration:
            self.baking_complete = True
            return

        # Update baking progress
        self.baking_progress = min(1.0, self.baking_timer / self.baking_duration)

        # Update smoke particles
        for particle in self.smoke_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] -= particle['fade_speed']
            if particle['alpha'] <= 0:
                self.smoke_particles.remove(particle)

        # Update splash particles
        for particle in self.splash_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['dy'] += particle['gravity']
            particle['alpha'] -= particle['fade_speed']
            if particle['alpha'] <= 0:
                self.splash_particles.remove(particle)

        # Update bubbles
        for bubble in self.bubbles[:]:
            bubble['y'] -= bubble['speed']
            bubble['size'] *= 0.95
            if bubble['size'] < 1:
                self.bubbles.remove(bubble)

        # Update steam particles
        for particle in self.steam_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] -= particle['fade_speed']
            if particle['alpha'] <= 0:
                self.steam_particles.remove(particle)

        # Update heat distortion
        self.heat_distortion = (self.heat_distortion + 1) % 360

        # Add effects based on progress
        if random.random() < 0.1 * self.baking_progress:
            self.add_bubble()
        if self.baking_progress > 0.5 and random.random() < 0.05:
            self.add_steam_particle()

    def draw(self, screen, center_x, center_y):
        """Draw all baking effects"""
        # Draw heat distortion
        if self.heat_distortion > 0:
            amplitude = 3 * self.baking_progress
            wavelength = 20
            for y in range(-30, 31, 2):
                offset = amplitude * math.sin((y + self.heat_distortion) / wavelength)
                alpha = int(100 * self.baking_progress)
                heat_surface = pygame.Surface((80, 2), pygame.SRCALPHA)
                pygame.draw.line(heat_surface, (255, 200, 100, alpha),
                               (0, 1),
                               (80, 1), 1)
                screen.blit(heat_surface,
                           (center_x - 40 + offset, center_y + y))

        # Draw bubbles with progress-based intensity
        for bubble in self.bubbles:
            alpha = int(150 * self.baking_progress)
            bubble_surface = pygame.Surface((int(bubble['size']*2), int(bubble['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(bubble_surface, (255, 255, 255, alpha),
                             (int(bubble['size']), int(bubble['size'])),
                             int(bubble['size']))
            screen.blit(bubble_surface,
                       (int(center_x + bubble['x'] - bubble['size']),
                        int(center_y + bubble['y'] - bubble['size'])))

        # Draw steam particles with progress-based intensity
        for particle in self.steam_particles:
            alpha = int(particle['alpha'] * self.baking_progress)
            steam_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            pygame.draw.circle(steam_surface, (255, 255, 255, alpha),
                             (particle['size']//2, particle['size']//2),
                             particle['size']//2)
            screen.blit(steam_surface,
                       (center_x + particle['x'] - particle['size']//2,
                        center_y + particle['y'] - particle['size']//2))

        # Draw completion effects
        if self.baking_complete:
            self.draw_completion_effects(screen, center_x, center_y)

class GhibliMixingEffect:
    def __init__(self):
        self.particles = []
        self.swirls = []
        self.sparkles = []
        
    def add_swirl(self, x, y, color):
        self.swirls.append({
            'x': x,
            'y': y,
            'radius': random.uniform(10, 30),
            'angle': random.uniform(0, math.pi * 2),
            'speed': random.uniform(1, 3),
            'color': color,
            'life': random.uniform(1, 2)
        })
    
    def add_sparkle(self, x, y, color=(255, 255, 255)):
        self.sparkles.append({
            'x': x,
            'y': y,
            'size': random.uniform(1, 3),
            'angle': random.uniform(0, math.pi * 2),
            'color': color,
            'life': random.uniform(0.3, 0.8)
        })
    
    def update(self, dt):
        # Update swirls
        for swirl in self.swirls[:]:
            swirl['life'] -= dt
            if swirl['life'] <= 0:
                self.swirls.remove(swirl)
            else:
                swirl['angle'] += swirl['speed'] * dt
                swirl['radius'] *= 0.99
        
        # Update sparkles
        for sparkle in self.sparkles[:]:
            sparkle['life'] -= dt
            if sparkle['life'] <= 0:
                self.sparkles.remove(sparkle)
            else:
                sparkle['size'] *= 0.95
    
    def draw(self, surface):
        # Draw swirls
        for swirl in self.swirls:
            alpha = int(255 * (swirl['life'] / 2.0))
            points = []
            for i in range(8):  # Create spiral points
                angle = swirl['angle'] + (i * math.pi / 4)
                r = swirl['radius'] * (1 - i/16)
                x = swirl['x'] + math.cos(angle) * r
                y = swirl['y'] + math.sin(angle) * r
                points.append((x, y))
            if len(points) > 1:
                color_with_alpha = (*swirl['color'], alpha)
                pygame.draw.lines(surface, color_with_alpha, False, points, 2)
        
        # Draw sparkles
        for sparkle in self.sparkles:
            alpha = int(255 * (sparkle['life'] / 0.8))
            color_with_alpha = (*sparkle['color'], alpha)
            size = sparkle['size']
            x, y = sparkle['x'], sparkle['y']
            # Draw a star shape
            for i in range(4):
                angle = sparkle['angle'] + (i * math.pi / 4)
                end_x = x + math.cos(angle) * size * 2
                end_y = y + math.sin(angle) * size * 2
                pygame.draw.line(surface, color_with_alpha, (x, y), (end_x, end_y), 1)

class MixingLayer:
    def __init__(self, ingredient, y_offset=0):
        self.ingredient = ingredient
        self.color = INGREDIENT_COLORS.get(ingredient, (200, 200, 200))
        self.type = INGREDIENT_TYPES.get(ingredient, "dry")
        self.mixing_progress = 0
        self.y_offset = y_offset
        self.surface_points = []
        self.surface_offset = 0

    def update(self, dt):
        """Update the mixing layer animation"""
        # Update mixing progress
        if self.mixing_progress < 1:
            self.mixing_progress = min(1, self.mixing_progress + dt * 0.5)
        
        # Update surface animation
        self.surface_offset += dt * 2
        self.update_surface_points()

    def update_surface_points(self):
        """Update the surface points for organic movement"""
        self.surface_points = []
        num_points = 20
        for i in range(num_points):
            x = (i / (num_points - 1) - 0.5) * 2
            # Create organic movement with multiple sine waves
            y_offset = (
                math.sin(x * 10 + self.surface_offset) * 2 +
                math.sin(x * 5 + self.surface_offset * 0.7) * 3 +
                math.sin(x * 2 + self.surface_offset * 1.3)
            )
            self.surface_points.append((x, self.y_offset + y_offset))

    def draw(self, screen, center_x, center_y, bowl_width, bowl_height):
        """Draw the mixing layer"""
        if not self.surface_points:
            return
            
        # Convert relative coordinates to screen coordinates
        screen_points = []
        for x, y in self.surface_points:
            screen_x = center_x + x * bowl_width/2
            screen_y = center_y + y
            screen_points.append((screen_x, screen_y))
        
        # Add bottom points to complete the polygon
        screen_points.append((center_x + bowl_width/2, center_y + bowl_height/2))
        screen_points.append((center_x - bowl_width/2, center_y + bowl_height/2))
        
        # Draw the layer with transparency based on mixing progress
        alpha = int(200 + 55 * self.mixing_progress)
        color_surface = pygame.Surface((bowl_width, bowl_height), pygame.SRCALPHA)
        pygame.draw.polygon(color_surface, (*self.color, alpha), screen_points)
        screen.blit(color_surface, (center_x - bowl_width/2, center_y - bowl_height/2))
        
        # Draw surface line for definition
        if len(screen_points) > 2:
            surface_line_points = screen_points[:-2]  # Exclude bottom points
            pygame.draw.lines(screen, (*self.color, 255), False, surface_line_points, 2)

def flash_screen_red(screen):
    """Flash the screen red to indicate an error"""
    for _ in range(3):  # Flash 3 times
        screen.fill(RED)
        pygame.display.flip()
        pygame.time.delay(50)
        screen.fill(WHITE)
        pygame.display.flip()
        pygame.time.delay(50)

class AnimatedIngredient:
    def __init__(self, ingredient, start_x, start_y, target_y=HEIGHT//2 + 30):
        self.ingredient = ingredient
        self.x = start_x
        self.y = start_y
        self.target_x = WIDTH // 2
        self.target_y = target_y
        self.speed = random.uniform(8, 12)  # Slightly faster movement
        self.size = random.randint(15, 20)
        self.color = INGREDIENT_COLORS.get(ingredient, (200, 200, 200))
        self.alpha = 255
        self.particles = []
        self.done = False
        self.type = INGREDIENT_TYPES.get(ingredient, "dry")
        self.last_particle_time = 0
        self.particle_interval = 0.1  # Seconds between particle spawns

    def update(self, current_bowl_level):
        """Update the ingredient animation"""
        if self.done:
            return True

        # Calculate direction to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.speed:
            # When reaching the target, mark as done
            self.done = True
            return True
        else:
            # Move directly towards target
            move_dx = (dx / distance) * self.speed
            move_dy = (dy / distance) * self.speed
            
            # Update position
            self.x += move_dx
            self.y += move_dy
            
            # Add movement particles less frequently
            current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
            if current_time - self.last_particle_time >= self.particle_interval:
                if random.random() < 0.3:
                    self.add_movement_particle()
                self.last_particle_time = current_time
        
        # Update existing particles
        self.update_particles()
        
        return False

    def add_movement_particle(self):
        """Add particles that follow the ingredient's movement"""
        particle = {
            'x': self.x + random.uniform(-self.size/2, self.size/2),
            'y': self.y + random.uniform(-self.size/2, self.size/2),
            'dx': random.uniform(-1, 1),
            'dy': random.uniform(-1, 1),
            'size': random.randint(2, 4),
            'alpha': 150,
            'fade_speed': random.uniform(8, 12)
        }
        self.particles.append(particle)

    def update_particles(self):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] -= particle['fade_speed']
            if particle['alpha'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        """Draw the ingredient and its particles"""
        # Draw particles
        for particle in self.particles:
            alpha_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*self.color, int(particle['alpha'])),
                             (particle['size']//2, particle['size']//2), particle['size']//2)
            screen.blit(alpha_surface,
                       (particle['x'] - particle['size']//2,
                        particle['y'] - particle['size']//2))
        
        # Only draw the ingredient if it hasn't reached the target
        if not self.done:
            # Draw glow
            glow_size = self.size + 4
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_color = (*self.color, 100)  # Semi-transparent glow
            pygame.draw.circle(glow_surface, glow_color,
                             (glow_size, glow_size), glow_size)
            screen.blit(glow_surface,
                       (int(self.x - glow_size),
                        int(self.y - glow_size)))
            
            # Draw main ingredient
            pygame.draw.circle(screen, self.color,
                             (int(self.x), int(self.y)), self.size)

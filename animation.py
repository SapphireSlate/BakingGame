import pygame
import math
import random
import time
from config import WIDTH, HEIGHT, WHITE, RED, GRAY, DARK_GRAY, YELLOW, BLUE, BLACK
from colorsys import rgb_to_hsv, hsv_to_rgb
from sprites import INGREDIENT_COLORS

def ensure_rgb(color):
    """Ensure color is in RGB format (3 components)"""
    try:
        if len(color) > 3:
            return color[:3]
        return tuple(max(0, min(255, int(c))) for c in color)
    except (TypeError, ValueError):
        print(f"Warning: Invalid color value {color}, defaulting to gray")
        return (128, 128, 128)

def safe_color_mix(color1, color2):
    """Safely mix two colors with error handling"""
    try:
        # Ensure both colors are in RGB format
        c1 = ensure_rgb(color1)
        c2 = ensure_rgb(color2)
        
        # Mix colors using subtractive mixing
        mixed = mix_colors(c1, c2)
        
        # Ensure result is valid RGB
        return ensure_rgb(mixed)
    except Exception as e:
        print(f"Error mixing colors {color1} and {color2}: {e}")
        return (128, 128, 128)  # Return gray as fallback

def mix_colors(color1, color2):
    """Mix colors like real paint using subtractive color mixing"""
    # Ensure we're only using RGB components, not alpha
    rgb1 = color1[:3] if len(color1) > 3 else color1
    rgb2 = color2[:3] if len(color2) > 3 else color2
    
    # Convert to CMY (Cyan, Magenta, Yellow) space
    cmy1 = [1 - (c / 255) for c in rgb1]
    cmy2 = [1 - (c / 255) for c in rgb2]
    
    # Mix the colors in CMY space (subtractive mixing)
    mixed_cmy = [(c1 + c2) / 2 for c1, c2 in zip(cmy1, cmy2)]
    
    # Convert back to RGB
    mixed_rgb = [max(0, min(255, int((1 - c) * 255))) for c in mixed_cmy]
    
    # Ensure some minimal brightness
    min_value = 30
    mixed_rgb = [max(min_value, c) for c in mixed_rgb]
    
    return tuple(mixed_rgb)

class AnimatedIngredient:
    def __init__(self, name, start_x, start_y):
        self.name = name
        self.x = start_x
        self.y = start_y
        self.target_x = WIDTH // 2
        self.target_y = HEIGHT // 2
        self.speed = 5
        self.color = INGREDIENT_COLORS.get(name, (200, 200, 200))  # Use colors from sprites.py

    def move(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > self.speed:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            return False
        return True

    def draw(self, screen):
        # Create a surface with transparency
        circle_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Draw the colored circle with the ingredient's color and enhanced visibility
        pygame.draw.circle(circle_surface, (*self.color, 230), (20, 20), 20)
        pygame.draw.circle(circle_surface, WHITE, (20, 20), 20, 2)  # White border
        
        # Add a subtle glow effect
        glow_radius = 22
        glow_color = (*self.color, 100)  # Semi-transparent glow
        pygame.draw.circle(circle_surface, glow_color, (20, 20), glow_radius)
        
        screen.blit(circle_surface, (int(self.x) - 20, int(self.y) - 20))
        
        # Render text with transparent background
        font = pygame.font.Font(None, 20)
        text_surface = font.render(self.name[:1], True, BLACK, None)
        screen.blit(text_surface, (int(self.x) - text_surface.get_width() // 2, 
                                 int(self.y) - text_surface.get_height() // 2))

class AnimationManager:
    def __init__(self):
        self.animated_ingredients = []
        self.spill_line = []
        self.power_flicker = False
        self.oven_fire = []
        self.bowl_fill_level = 0
        self.is_animating = False
        self.bowl_color = (200, 200, 200)
        self.color_transition = None
        self.transition_progress = 0
        self.transition_speed = 0.05
        self.pending_color_transitions = []
        self.disaster_message = None
        self.disaster_timer = 0
        self.disaster_duration = 180  # 3 seconds at 60 FPS
        self.current_disaster = None
        self.min_color_value = 100
        self.disaster_particles = []
        self.flicker_count = 0
        self.flame_particles = []
        self.steam_particles = []
        self.flour_clouds = []
        self.sugar_crystals = []
        self.liquid_droplets = []
        self.ingredient_effects = {
            "Flour": self.add_flour_effect,
            "Sugar": self.add_sugar_effect,
            "Eggs": self.add_egg_effect,
            "Milk": self.add_liquid_effect,
            "Butter": self.add_butter_effect,
            "Vanilla": self.add_liquid_effect,
            "Cocoa": self.add_flour_effect,
        }
        self.previous_colors = []  # Store previous colors for mixing
        self.max_ingredients = 8  # Maximum number of ingredients that can be mixed
        self.error_messages = []  # Store error messages to display
        self.error_message_duration = 3  # seconds
        self.error_message_timer = 0

    def add_ingredient_animation(self, ing, start_x, start_y):
        new_ingredient = AnimatedIngredient(ing, start_x, start_y)
        self.animated_ingredients.append(new_ingredient)
        self.is_animating = True
        # Don't add color transition until ingredient reaches bowl
        self.pending_color_transitions.append((INGREDIENT_COLORS.get(ing, (255, 255, 255)), ing))

    def mix_colors(self, color1, color2):
        """Mix colors while maintaining minimum visibility"""
        mixed = mix_colors(color1, color2)
        # Ensure each color component is at least min_color_value
        return tuple(max(c, self.min_color_value) for c in mixed)

    def start_color_transition(self, new_color):
        # Check if we've hit the ingredient limit
        if len(self.previous_colors) >= self.max_ingredients:
            self.add_error_message("Bowl is too full! Cannot add more ingredients.")
            return
        
        # If there's no existing color, just set it
        if not self.bowl_color or self.bowl_color == (200, 200, 200):
            self.bowl_color = ensure_rgb(new_color)
            return
        
        try:
            # Add new color to the mix
            self.previous_colors.append(self.bowl_color)
            
            # Mix colors safely
            mixed_color = ensure_rgb(new_color)
            for color in self.previous_colors:
                mixed_color = safe_color_mix(mixed_color, ensure_rgb(color))
            
            # Store the transition
            self.color_transition = (self.bowl_color, mixed_color)
            self.transition_progress = 0
            
        except Exception as e:
            print(f"Error in color transition: {e}")
            self.add_error_message("Error mixing ingredients!")
    
    def add_error_message(self, message):
        """Add an error message to display"""
        self.error_messages.append({
            'text': message,
            'timer': self.error_message_duration
        })
    
    def update_error_messages(self, dt):
        """Update error message timers and remove expired messages"""
        for msg in self.error_messages[:]:
            msg['timer'] -= dt
            if msg['timer'] <= 0:
                self.error_messages.remove(msg)
    
    def draw_error_messages(self, screen):
        """Draw any active error messages"""
        if not self.error_messages:
            return
            
        font = pygame.font.Font(None, 36)
        y_offset = 150  # Start below other UI elements
        
        for msg in self.error_messages:
            # Create semi-transparent background
            text = font.render(msg['text'], True, (255, 50, 50))
            bg_surface = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (40, 0, 0, 180), bg_surface.get_rect(), border_radius=10)
            
            # Calculate position
            x = WIDTH//2 - text.get_width()//2
            
            # Draw background and text
            screen.blit(bg_surface, (x - 10, y_offset - 5))
            screen.blit(text, (x, y_offset))
            
            y_offset += 40  # Space between messages
    
    def update_bowl_color(self):
        if self.color_transition:
            self.transition_progress += self.transition_speed
            if self.transition_progress >= 1:
                self.bowl_color = self.color_transition[1]
                self.color_transition = None
                self.add_sparkle_effect()
            else:
                # Smooth transition between colors
                progress = self.transition_progress
                start_color = self.color_transition[0]
                end_color = self.color_transition[1]
                
                # Linear interpolation between colors
                current_color = tuple(
                    int(start_color[i] * (1 - progress) + end_color[i] * progress)
                    for i in range(3)
                )
                self.bowl_color = current_color

    def add_sparkle_effect(self):
        # Create a surface for the sparkle effects
        sparkle_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Add multiple layers of sparkles with different sizes and colors
        for _ in range(20):  # Increased number of sparkles
            x = random.randint(WIDTH//2 - 100, WIDTH//2 + 100)
            y = random.randint(HEIGHT//2 - 50, HEIGHT//2 + 50)
            size = random.randint(2, 6)  # Varied sizes
            
            # Create a glowing effect with multiple circles
            for radius in range(size, 0, -1):
                alpha = int(200 * (radius/size))
                glow_color = tuple(min(255, c + 100) for c in self.bowl_color)  # Brighter version
                pygame.draw.circle(sparkle_surface, (*glow_color, alpha), (x, y), radius)
        
        # Add some shooting sparkles
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.randint(30, 80)
            x = WIDTH//2 + math.cos(angle) * distance
            y = HEIGHT//2 + math.sin(angle) * distance
            pygame.draw.circle(sparkle_surface, (255, 255, 255, 200), (int(x), int(y)), 2)
        
        return sparkle_surface

    def update_animations(self, screen, game, dt):
        # Update error messages
        self.update_error_messages(dt)
        
        # Store the disaster message state at the start
        should_show_disaster = self.disaster_timer > 0 and self.current_disaster
        
        self.update_bowl_color()
        
        # Handle disaster effects first
        if self.disaster_timer > 0:
            # Create red overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255, 0, 0, 128), overlay.get_rect())
            screen.blit(overlay, (0, 0))
            
            # Update and draw the specific disaster effect
            if self.current_disaster == "Oven malfunction":
                self.update_oven_fire(screen)
            elif self.current_disaster == "Power outage":
                self.update_power_flicker(screen)
            elif self.current_disaster == "Ingredient spill":
                self.update_spill_particles(screen)
        
        # Continue with regular animations
        self.draw_mixing_bowl(screen, game)
        
        # Update ingredient effects
        if self.flour_clouds or self.sugar_crystals or self.liquid_droplets:
            self.update_ingredient_effects(screen)
        
        # Handle animated ingredients
        if self.animated_ingredients:
            completed = []
            for i, ingredient in enumerate(self.animated_ingredients):
                if ingredient.move():
                    completed.append(i)
                    if self.pending_color_transitions:
                        new_color, ing_type = self.pending_color_transitions.pop(0)
                        self.start_color_transition(new_color)
                        if ing_type in self.ingredient_effects:
                            self.ingredient_effects[ing_type]()
                        self.bowl_fill_level += 0.1
                        if self.bowl_fill_level > 1:
                            self.bowl_fill_level = 1
                else:
                    ingredient.draw(screen)
            
            for i in reversed(completed):
                self.animated_ingredients.pop(i)
            
            self.is_animating = bool(self.animated_ingredients)
        else:
            self.is_animating = False

        # Draw sparkle effects
        if self.color_transition:
            sparkle_surface = self.add_sparkle_effect()
            screen.blit(sparkle_surface, (0, 0))
        
        # Draw error messages and disaster message last
        self.draw_error_messages(screen)
        self.draw_disaster_message(screen)

    def reset_bowl(self):
        """Reset the bowl fill level to zero and reset color"""
        self.bowl_fill_level = 0
        self.bowl_color = (200, 200, 200)
        self.color_transition = None
        self.animated_ingredients.clear()
        self.is_animating = False
        self.previous_colors = []  # Clear color history

    def draw_mixing_bowl(self, screen, game):
        bowl_color = BLUE if "Larger Bowl" in game.active_upgrades else DARK_GRAY
        bowl_size = 160 if "Larger Bowl" in game.active_upgrades else 150
        
        # Draw bowl glow with enhanced effect
        glow_surface = pygame.Surface((bowl_size + 20, 150), pygame.SRCALPHA)
        for r in range(10, 0, -1):
            alpha = int(25 * r)
            pygame.draw.ellipse(glow_surface, (*self.bowl_color, alpha), 
                              (r, r, bowl_size + 20 - 2*r, 50 - r))
        screen.blit(glow_surface, (WIDTH//2 - (bowl_size + 20)//2, HEIGHT//2 - 35))
        
        # Draw bowl outline with enhanced neon effect
        for i in range(3):
            alpha = 255 - i * 50
            pygame.draw.ellipse(screen, (*bowl_color, alpha), 
                              (WIDTH//2 - bowl_size//2 - i, HEIGHT//2 - 25 - i, 
                               bowl_size + i*2, 50 + i*2), 2)
        
        # Draw liquid contents with dynamic effects
        if self.bowl_fill_level > 0:
            fill_height = int(max(self.bowl_fill_level, 0.1) * 100)
            gradient_surface = pygame.Surface((bowl_size - 4, fill_height), pygame.SRCALPHA)
            
            # Create dynamic liquid effect
            current_time = time.time()
            
            # Wave parameters
            wave_speed = 2
            wave_height = 3
            num_waves = 3
            
            for y in range(fill_height):
                progress = y / fill_height
                
                # Create multiple overlapping waves
                wave_offset = 0
                for i in range(num_waves):
                    wave_offset += math.sin(current_time * wave_speed + y * 0.1 + i * 2) * wave_height
                
                # Adjust wave effect based on number of ingredients
                wave_intensity = min(1.0, len(game.current_ingredients) * 0.2)
                wave_offset *= wave_intensity
                
                # Base color with alpha
                alpha = int(255 * (0.5 + 0.5 * progress))
                base_color = self.bowl_color[:3]  # Ensure RGB only
                glow_color = tuple(min(255, c + 50) for c in base_color)  # Brighter version
                
                # Create proper RGBA colors
                base_rgba = (*base_color, alpha)
                glow_rgba = (*glow_color, alpha)
                
                # Draw the liquid line with wave effect
                x_offset = int(wave_offset)
                pygame.draw.line(gradient_surface, base_rgba,
                               (max(0, x_offset), y),
                               (min(bowl_size - 4, bowl_size - 4 + x_offset), y))
                
                # Add bubbles with proper RGBA colors
                if random.random() < 0.02 * wave_intensity:
                    bubble_x = random.randint(10, bowl_size - 14)
                    bubble_size = random.randint(2, 4)
                    bubble_alpha = random.randint(100, 200)
                    pygame.draw.circle(gradient_surface, (*glow_color, bubble_alpha),
                                     (bubble_x, y), bubble_size)
            
            # Add dynamic swirl effects
            swirl_time = current_time * 3
            for i in range(3):
                swirl_x = bowl_size//2 + math.cos(swirl_time + i*2) * 20
                swirl_y = fill_height//2 + math.sin(swirl_time + i*2) * 10
                swirl_color = (*glow_color, 150)
                
                # Draw swirl pattern
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    end_x = swirl_x + math.cos(rad + swirl_time) * 10
                    end_y = swirl_y + math.sin(rad + swirl_time) * 5
                    if 0 <= end_x <= bowl_size-4 and 0 <= end_y <= fill_height:
                        pygame.draw.line(gradient_surface, swirl_color,
                                       (swirl_x, swirl_y), (end_x, end_y), 2)
            
            # Add magical sparkles
            for _ in range(int(fill_height / 5)):
                spark_x = random.randint(0, bowl_size - 4)
                spark_y = random.randint(0, fill_height)
                spark_size = random.randint(1, 3)
                spark_alpha = random.randint(150, 255)
                
                # Draw star-shaped sparkle
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    end_x = spark_x + math.cos(rad) * spark_size
                    end_y = spark_y + math.sin(rad) * spark_size
                    pygame.draw.line(gradient_surface, (255, 255, 255, spark_alpha),
                                   (spark_x, spark_y), (end_x, end_y), 1)
            
            # Add color swirls when mixing
            if self.color_transition:
                transition_color = self.color_transition[1]
                swirl_points = []
                swirl_time = current_time * 2
                for i in range(5):
                    x = bowl_size//2 + math.cos(swirl_time + i) * (20 - i*3)
                    y = fill_height//2 + math.sin(swirl_time + i) * (10 - i*2)
                    swirl_points.append((x, y))
                
                if len(swirl_points) > 2:
                    pygame.draw.lines(gradient_surface, (*transition_color, 200),
                                    False, swirl_points, 3)
            
            # Blit the liquid to the screen
            screen.blit(gradient_surface, 
                       (WIDTH//2 - bowl_size//2 + 2, HEIGHT//2 + 73 - fill_height))
            
            # Add surface reflection
            reflection_height = 10
            reflection_surface = pygame.Surface((bowl_size - 4, reflection_height), pygame.SRCALPHA)
            pygame.draw.ellipse(reflection_surface, (255, 255, 255, 30),
                              (0, 0, bowl_size - 4, reflection_height * 2))
            screen.blit(reflection_surface,
                       (WIDTH//2 - bowl_size//2 + 2, HEIGHT//2 + 73 - fill_height))

    def draw_disaster_animations(self, screen):
        if self.spill_line:
            if len(self.spill_line) < 50:
                last_point = self.spill_line[-1]
                self.spill_line.append((last_point[0], last_point[1] + 10))
            pygame.draw.lines(screen, GRAY, False, self.spill_line, 5)

        if self.power_flicker:
            screen.fill(DARK_GRAY)
            self.power_flicker = not self.power_flicker

        for flame in self.oven_fire:
            pygame.draw.circle(screen, RED, flame, random.randint(5, 15))
            pygame.draw.circle(screen, YELLOW, flame, random.randint(3, 8))

    def trigger_disaster_animation(self, disaster_type, game=None):
        self.disaster_message = f"DISASTER: {disaster_type}!"
        self.disaster_timer = self.disaster_duration
        self.current_disaster = disaster_type
        
        # For ingredient spill, we need to handle the current ingredients
        if disaster_type == "Ingredient spill":
            num_particles = 30  # Default number
            if game and hasattr(game, 'current_ingredients'):
                num_particles = max(30, len(game.current_ingredients) * 15)
            self.trigger_spill_effect(num_particles)
        elif disaster_type == "Power outage":
            self.trigger_power_flicker_effect()
        elif disaster_type == "Oven malfunction":
            self.trigger_oven_fire_effect()

    def clear_disaster_animations(self):
        """Clear all disaster-related effects"""
        self.spill_line = []
        self.power_flicker = False
        self.oven_fire = []
        self.flame_particles = []
        self.disaster_particles = []
        self.flicker_count = 0
        self.current_disaster = None
        self.disaster_timer = 0

    def draw_disaster_message(self, screen):
        if not self.disaster_message or self.disaster_timer <= 0:
            return
            
        try:
            # Create semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255, 0, 0, 128), overlay.get_rect())
            screen.blit(overlay, (0, 0))
            
            # Create background for text
            font = pygame.font.Font(None, 48)
            text = font.render(self.disaster_message, True, WHITE[:3])
            
            # Add pulsing effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.2 + 0.8
            scaled_size = (
                int(text.get_width() * pulse),
                int(text.get_height() * pulse)
            )
            
            # Create background surface
            padding = 20
            bg_surface = pygame.Surface((scaled_size[0] + padding * 2, 
                                      scaled_size[1] + padding * 2), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (40, 0, 0, 200), 
                           bg_surface.get_rect(), border_radius=15)
            
            # Position and draw
            x = WIDTH//2 - scaled_size[0]//2
            y = HEIGHT//2 - scaled_size[1]//2
            
            screen.blit(bg_surface, (x - padding, y - padding))
            
            # Scale and draw the text
            scaled_text = pygame.transform.smoothscale(text, scaled_size)
            screen.blit(scaled_text, (x, y))
            
        except Exception as e:
            print(f"Error drawing disaster message: {e}")
    
    def trigger_oven_fire_effect(self):
        # Create more flame particles that rise from bottom of screen
        for _ in range(40):  # Increased from 20
            x = random.randint(0, WIDTH)
            y = HEIGHT + random.randint(0, 50)
            speed = random.uniform(3, 7)  # Increased speed
            size = random.randint(50, 120)  # Increased size
            self.flame_particles.append({
                'x': x, 'y': y,
                'speed': speed,
                'size': size,
                'wobble': random.uniform(0, 2 * math.pi),
                'intensity': random.uniform(0.8, 1.2)  # Variation in flame intensity
            })

    def update_oven_fire(self, screen):
        if self.flame_particles:
            # Create an overlay for the heat distortion effect
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 50, 0, 30))  # Red tint with alpha
            screen.blit(overlay, (0, 0))
            
            for flame in self.flame_particles[:]:
                flame['y'] -= flame['speed']
                flame['wobble'] += 0.1
                x = flame['x'] + math.sin(flame['wobble']) * 20
                
                # Enhanced flame gradient with proper RGBA tuples
                colors = [
                    (255, 50, 0, 200),    # Red
                    (255, 150, 0, 180),   # Orange
                    (255, 200, 0, 160),   # Yellow
                    (255, 255, 200, 140)  # White-yellow core
                ]
                
                for i, color in enumerate(colors):
                    size = flame['size'] * (1 - i * 0.2) * flame['intensity']
                    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(surf, color, (0, 0, size * 2, size * 2))
                    screen.blit(surf, (x - size, flame['y'] - size))
                
                if flame['y'] < -100:
                    self.flame_particles.remove(flame)

    def trigger_power_flicker_effect(self):
        self.flicker_count = 30  # More flickers
        self.flicker_intensity = random.uniform(0.5, 1.0)

    def update_power_flicker(self, screen):
        if self.flicker_count > 0:
            if self.flicker_count % 2 == 0:
                intensity = int(255 * self.flicker_intensity)
                screen.fill((intensity, intensity, intensity))
            else:
                screen.fill((0, 0, 0))
            self.flicker_count -= 1

    def trigger_spill_effect(self, num_particles=30):
        bowl_center = (WIDTH//2, HEIGHT//2)
        
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 20)
            size = random.randint(30, 70)
            # Ensure RGB format for bowl color
            color = (self.bowl_color[:3] if len(self.bowl_color) > 3 else self.bowl_color) if self.bowl_color != (200, 200, 200) else random.choice([c[:3] if len(c) > 3 else c for c in INGREDIENT_COLORS.values()])
            
            self.disaster_particles.append({
                'x': bowl_center[0],
                'y': bowl_center[1],
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed - 8,
                'size': size,
                'color': color,
                'gravity': 0.4,
                'squish': 1.0,
                'rotation': random.uniform(0, 360),
                'spin': random.uniform(-5, 5)
            })

    def update_spill_particles(self, screen):
        if self.disaster_particles:
            for particle in self.disaster_particles[:]:
                # Update position with more dynamic movement
                particle['x'] += particle['dx']
                particle['dy'] += particle['gravity']
                particle['y'] += particle['dy']
                particle['rotation'] += particle['spin']
                
                # Enhanced squish effect when hitting bottom
                if particle['y'] + particle['size'] > HEIGHT:
                    particle['dy'] *= -0.6
                    particle['dx'] *= 0.8
                    particle['squish'] = 0.5
                    particle['spin'] *= 0.8
                else:
                    particle['squish'] = max(0.8, particle['squish'] + 0.05)
                
                # Draw blob with rotation and proper RGBA
                size_x = particle['size'] * 2
                size_y = particle['size'] * 2 * particle['squish']
                surf = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
                
                # Draw main blob with alpha
                color = (*particle['color'][:3], 200)  # Ensure RGB + alpha
                pygame.draw.ellipse(surf, color, (0, 0, size_x, size_y))
                
                # Rotate and draw
                rotated_surf = pygame.transform.rotate(surf, particle['rotation'])
                screen.blit(rotated_surf, (particle['x'] - rotated_surf.get_width()//2,
                                         particle['y'] - rotated_surf.get_height()//2))
                
                if particle['y'] > HEIGHT + 100:
                    self.disaster_particles.remove(particle)

    def add_flour_effect(self):
        # Create flour puff cloud
        for _ in range(10):
            self.flour_clouds.append({
                'x': WIDTH//2 + random.randint(-30, 30),
                'y': HEIGHT//2 + random.randint(-10, 10),
                'size': random.randint(10, 20),
                'alpha': 255,
                'fade_speed': random.uniform(2, 4)
            })

    def add_sugar_effect(self):
        # Create sparkly crystallization effect
        for _ in range(15):
            self.sugar_crystals.append({
                'x': WIDTH//2 + random.randint(-40, 40),
                'y': HEIGHT//2 + random.randint(-20, 20),
                'size': random.randint(1, 3),
                'sparkle_time': 0,
                'lifetime': random.randint(30, 60)
            })

    def add_egg_effect(self):
        # Create egg crack and splash effect
        center_x = WIDTH//2
        center_y = HEIGHT//2
        for _ in range(20):
            angle = random.uniform(0, math.pi)  # Upper half circle
            speed = random.uniform(2, 5)
            self.liquid_droplets.append({
                'x': center_x,
                'y': center_y,
                'dx': math.cos(angle) * speed,
                'dy': -math.sin(angle) * speed,
                'size': random.randint(2, 4),
                'color': (255, 250, 220),  # Egg yolk color
                'gravity': 0.2,
                'lifetime': 30
            })

    def add_liquid_effect(self):
        # Create liquid splash effect
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            self.liquid_droplets.append({
                'x': WIDTH//2 + random.randint(-20, 20),
                'y': HEIGHT//2,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.randint(2, 5),
                'color': self.bowl_color,
                'gravity': 0.1,
                'lifetime': 40
            })

    def add_butter_effect(self):
        # Create melting butter effect with golden droplets
        for _ in range(12):
            self.liquid_droplets.append({
                'x': WIDTH//2 + random.randint(-30, 30),
                'y': HEIGHT//2 - 20,
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(0.5, 1.5),
                'size': random.randint(3, 6),
                'color': (255, 220, 100),  # Golden color
                'gravity': 0.05,
                'lifetime': 50
            })

    def update_ingredient_effects(self, screen):
        # Update flour clouds
        for cloud in self.flour_clouds[:]:
            cloud['alpha'] = max(0, int(cloud['alpha'] - cloud['fade_speed']))
            if cloud['alpha'] <= 0:
                self.flour_clouds.remove(cloud)
            else:
                surf = pygame.Surface((cloud['size'] * 2, cloud['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 255, 255, cloud['alpha']),
                                (cloud['size'], cloud['size']), cloud['size'])
                screen.blit(surf, (cloud['x'] - cloud['size'], cloud['y'] - cloud['size']))

        # Update sugar crystals
        for crystal in self.sugar_crystals[:]:
            crystal['sparkle_time'] += 1
            if crystal['sparkle_time'] >= crystal['lifetime']:
                self.sugar_crystals.remove(crystal)
            else:
                sparkle_alpha = int(255 * abs(math.sin(crystal['sparkle_time'] * 0.2)))
                color = (*self.bowl_color, sparkle_alpha)  # Create proper RGBA tuple
                pygame.draw.circle(screen, color, 
                                (int(crystal['x']), int(crystal['y'])), 
                                crystal['size'])

        # Update liquid droplets
        for drop in self.liquid_droplets[:]:
            drop['x'] += drop['dx']
            drop['dy'] += drop['gravity']
            drop['y'] += drop['dy']
            drop['lifetime'] -= 1
            
            if drop['lifetime'] <= 0:
                self.liquid_droplets.remove(drop)
            else:
                alpha = int(255 * (drop['lifetime'] / 40))
                # Ensure color is RGB before adding alpha
                base_color = drop['color'][:3] if len(drop['color']) > 3 else drop['color']
                color = (*base_color, alpha)  # Create proper RGBA tuple
                pygame.draw.circle(screen, color,
                                (int(drop['x']), int(drop['y'])), drop['size'])

def flash_screen_red(screen):
    for _ in range(3):  # Flash 3 times
        screen.fill(RED)
        pygame.display.flip()
        pygame.time.delay(200)
        screen.fill(WHITE)
        pygame.display.flip()
        pygame.time.delay(200)

class PopupText:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.alpha = 255
        self.font = pygame.font.Font(None, 48)
        self.fade_speed = 5

    def update(self):
        self.alpha = max(0, self.alpha - self.fade_speed)
        self.y -= 1

    def draw(self, screen):
        # Create main text surface with proper color handling
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        
        # Create semi-transparent background with padding
        padding = 20
        bg_surface = pygame.Surface((text_surface.get_width() + padding * 2, 
                                   text_surface.get_height() + padding * 2), 
                                   pygame.SRCALPHA)
        
        # Draw rounded rectangle background with proper alpha
        bg_color = (40, 0, 0, int(self.alpha * 0.9))
        pygame.draw.rect(bg_surface, bg_color, bg_surface.get_rect(), border_radius=12)
        
        # Calculate positions
        bg_x = self.x - bg_surface.get_width() // 2
        bg_y = self.y - bg_surface.get_height() // 2
        text_x = self.x - text_surface.get_width() // 2
        text_y = self.y - text_surface.get_height() // 2
        
        # Create a new surface for text with alpha
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, self.alpha))
        text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw background and text
        screen.blit(bg_surface, (bg_x, bg_y))
        screen.blit(text_surface, (text_x, text_y))

    def is_finished(self):
        return self.alpha <= 0

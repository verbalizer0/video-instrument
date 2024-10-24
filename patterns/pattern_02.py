# patterns/pattern_02.py

# Standard library imports first
import random
import math
from typing import List, Tuple

# Third-party imports second
import pygame

# Local imports last
from .pattern_base import BasePattern
from visuals.shapes.shape_factory import ShapeFactory
from visuals.shapes.sprite_shapes import AnimatedSprite

class SpriteEntity:
    """
    Represents an animated sprite entity in the showcase.
    """
    def __init__(self, pos: Tuple[float, float], sprite_name: str, 
                 animation_name: str, size: float = 30):
        self.pos = list(pos)
        self.sprite_name = sprite_name
        self.animation_name = animation_name
        self.size = size
        self.velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.color = pygame.Color(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        self.life = 1.0
        self.fade_speed = random.uniform(0.001, 0.005)
        self.position_history: List[Tuple[float, float]] = []
        self.max_history = 30

    def update(self, width: int, height: int) -> bool:
        """Update entity state and return False if entity should be removed."""
        # Update position history
        self.position_history.append(tuple(self.pos))
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)

        # Update position
        self.pos[0] = (self.pos[0] + self.velocity[0]) % width
        self.pos[1] = (self.pos[1] + self.velocity[1]) % height
        
        # Update rotation
        self.rotation = (self.rotation + self.rotation_speed) % 360
        
        # Update life
        self.life = max(0, self.life - self.fade_speed)
        return self.life > 0

class SpriteShowcasePattern(BasePattern):
    """
    Pattern that demonstrates sprite animations and effects.
    """
    def __init__(self, screen: pygame.Surface, core_systems, sprite_manager=None):
        super().__init__(screen, core_systems, sprite_manager)
        
        if not sprite_manager:
            raise ValueError("Sprite manager is required for SpriteShowcasePattern")
            
        self.entities: List[SpriteEntity] = []
        self.spawn_timer = 0
        self.spawn_interval = 30
        self.pattern_mode = 0  # 0: random, 1: spiral, 2: grid
        
        # Grid setup
        self.grid_size = 5
        self.grid_spacing_x = self.width / (self.grid_size + 1)
        self.grid_spacing_y = self.height / (self.grid_size + 1)
        
        # Available sprite types
        self.sprite_types = list(self.sprite_manager.sprites.keys())
        if not self.sprite_types:
            raise ValueError("No sprites available in sprite manager")
        
        # Initialize grid
        self.setup_grid()

    def setup_grid(self) -> None:
        """Set up grid-based sprite arrangement."""
        if self.pattern_mode == 2:  # Grid mode
            self.entities.clear()
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    x = (i + 1) * self.grid_spacing_x
                    y = (j + 1) * self.grid_spacing_y
                    sprite_name = random.choice(self.sprite_types)
                    animation = self.get_random_animation(sprite_name)
                    self.entities.append(
                        SpriteEntity((x, y), sprite_name, animation)
                    )

    def get_random_animation(self, sprite_name: str) -> str:
        """Get a random animation name for the given sprite."""
        animations = self.sprite_manager.sprites[sprite_name]
        return random.choice(list(animations.keys()))

    def spawn_entity(self) -> None:
        """Spawn a new sprite entity based on current pattern mode."""
        if self.pattern_mode == 2:  # Don't spawn in grid mode
            return
            
        if self.pattern_mode == 0:  # Random mode
            pos = (
                random.randint(0, self.width),
                random.randint(0, self.height)
            )
        else:  # Spiral mode
            angle = len(self.entities) * 0.5
            radius = 100 + len(self.entities)
            pos = (
                self.width/2 + math.cos(angle) * radius,
                self.height/2 + math.sin(angle) * radius
            )

        sprite_name = random.choice(self.sprite_types)
        animation = self.get_random_animation(sprite_name)
        self.entities.append(SpriteEntity(pos, sprite_name, animation))

    def update(self) -> None:
        """Update pattern state."""
        super().update()
        
        # Update existing entities
        self.entities = [e for e in self.entities if e.update(self.width, self.height)]
        
        # Spawn new entities
        if self.pattern_mode != 2:  # Don't auto-spawn in grid mode
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self.spawn_entity()

    def draw_frame(self, surface: pygame.Surface) -> None:
        """Draw the current frame."""
        for entity in self.entities:
            # Draw trails
            if len(entity.position_history) > 1:
                self.trail_manager.draw_trail(
                    surface,
                    entity.position_history,
                    entity.color,
                    max(1, int(entity.size * 0.2))
                )
            
            # Draw sprite
            sprite = AnimatedSprite(
                pos=tuple(entity.pos),
                radius=entity.size,
                color=entity.color,
                sprite_name=entity.sprite_name,
                sprite_manager=self.sprite_manager,
                animation_name=entity.animation_name
            )
            sprite.rotation = entity.rotation
            
            # Apply life-based fade
            color = entity.color.copy()
            color.a = int(255 * entity.life)
            sprite.draw(surface)

    def handle_note(self, note: int, velocity: int) -> None:
        """Handle MIDI note input."""
        if note == 0:  # Change pattern mode
            self.pattern_mode = (self.pattern_mode + 1) % 3
            mode_names = ["Random", "Spiral", "Grid"]
            print(f"Pattern mode: {mode_names[self.pattern_mode]}")
            if self.pattern_mode == 2:
                self.setup_grid()
        else:
            # Spawn entities based on note
            count = max(1, velocity // 20)
            for _ in range(count):
                self.spawn_entity()

    def handle_cc(self, cc_number: int, cc_value: int) -> None:
        """Handle MIDI CC input."""
        normalized = cc_value / 127
        if cc_number == 1:  # Spawn interval
            self.spawn_interval = max(1, int(60 * (1 - normalized)))
        elif cc_number == 2:  # Entity size
            for entity in self.entities:
                entity.size = 20 + normalized * 40
        elif cc_number == 3:  # Rotation speed
            for entity in self.entities:
                entity.rotation_speed = normalized * 10 - 5
        elif cc_number == 4:  # Trail length
            self.trail_manager.trail_length = normalized
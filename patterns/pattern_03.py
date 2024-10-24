# patterns/pattern_03.py

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

class GifSprite:
    """
    Represents an animated GIF sprite instance.
    """
    def __init__(self, pos: Tuple[float, float], name: str, size: int = 50):
        self.pos = list(pos)
        self.name = name
        self.size = size
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.1

    def update(self, width: int, height: int) -> None:
        """Update sprite state."""
        # Update position
        self.pos[0] = (self.pos[0] + self.velocity[0]) % width
        self.pos[1] = (self.pos[1] + self.velocity[1]) % height
        
        # Update rotation
        self.rotation += self.rotation_speed
        
        # Update scale with smooth interpolation
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * self.scale_speed

class GifTestPattern(BasePattern):
    """
    Pattern for testing and demonstrating GIF animations.
    """
    def __init__(self, screen: pygame.Surface, core_systems, sprite_manager=None):
        super().__init__(screen, core_systems, sprite_manager)
        
        if not sprite_manager:
            raise ValueError("Sprite manager is required for GifTestPattern")
        
        self.sprites: List[GifSprite] = []
        self.available_gifs = [
            name for name, info in sprite_manager.sprite_info.items()
            if info.get('type') == 'gif'
        ]
        
        if not self.available_gifs:
            raise ValueError("No GIF sprites available")
        
        # Create initial sprite in center
        self.add_sprite(self.width // 2, self.height // 2)
        
        # Pattern settings
        self.layout_mode = 0  # 0: free, 1: circle, 2: grid
        self.auto_spawn = False
        self.spawn_timer = 0
        self.spawn_interval = 60

    def add_sprite(self, x: float, y: float) -> None:
        """Add a new GIF sprite at the specified position."""
        if not self.available_gifs:
            return
            
        sprite_name = random.choice(self.available_gifs)
        self.sprites.append(
            GifSprite((x, y), sprite_name, random.randint(30, 100))
        )

    def arrange_sprites(self) -> None:
        """Arrange sprites according to current layout mode."""
        if not self.sprites:
            return
            
        if self.layout_mode == 1:  # Circle
            radius = min(self.width, self.height) * 0.3
            center_x = self.width / 2
            center_y = self.height / 2
            
            for i, sprite in enumerate(self.sprites):
                angle = (i / len(self.sprites)) * math.pi * 2
                sprite.pos[0] = center_x + math.cos(angle) * radius
                sprite.pos[1] = center_y + math.sin(angle) * radius
                
        elif self.layout_mode == 2:  # Grid
            cols = math.ceil(math.sqrt(len(self.sprites)))
            spacing_x = self.width / (cols + 1)
            spacing_y = self.height / (cols + 1)
            
            for i, sprite in enumerate(self.sprites):
                col = i % cols
                row = i // cols
                sprite.pos[0] = spacing_x * (col + 1)
                sprite.pos[1] = spacing_y * (row + 1)

    def update(self) -> None:
        """Update pattern state."""
        super().update()
        
        # Update sprites
        for sprite in self.sprites:
            sprite.update(self.width, self.height)
            
        # Auto-spawn if enabled
        if self.auto_spawn:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self.add_sprite(
                    random.randint(0, self.width),
                    random.randint(0, self.height)
                )

    def draw_frame(self, surface: pygame.Surface) -> None:
        """Draw the current frame."""
        for sprite in self.sprites:
            gif_sprite = AnimatedSprite(
                pos=tuple(sprite.pos),
                radius=sprite.size * sprite.scale,
                color=pygame.Color(255, 255, 255),
                sprite_name=sprite.name,
                sprite_manager=self.sprite_manager
            )
            gif_sprite.rotation = sprite.rotation
            gif_sprite.draw(surface)

    def handle_note(self, note: int, velocity: int) -> None:
        """Handle MIDI note input."""
        if note == 0:  # Change layout mode
            self.layout_mode = (self.layout_mode + 1) % 3
            mode_names = ["Free", "Circle", "Grid"]
            print(f"Layout mode: {mode_names[self.layout_mode]}")
            self.arrange_sprites()
            
        elif note == 1:  # Toggle auto-spawn
            self.auto_spawn = not self.auto_spawn
            print(f"Auto-spawn: {'On' if self.auto_spawn else 'Off'}")
            
        else:  # Add new sprite
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.add_sprite(x, y)

    def handle_cc(self, cc_number: int, cc_value: int) -> None:
        """Handle MIDI CC input."""
        normalized = cc_value / 127
        
        if cc_number == 1:  # Global scale
            for sprite in self.sprites:
                sprite.target_scale = 0.5 + normalized * 1.5
                
        elif cc_number == 2:  # Rotation speed
            for sprite in self.sprites:
                sprite.rotation_speed = (normalized * 8) - 4
                
        elif cc_number == 3:  # Movement speed
            for sprite in self.sprites:
                speed = normalized * 2
                angle = math.atan2(sprite.velocity[1], sprite.velocity[0])
                sprite.velocity = [
                    speed * math.cos(angle),
                    speed * math.sin(angle)
                ]
                
        elif cc_number == 4:  # Spawn interval
            self.spawn_interval = max(10, int((1 - normalized) * 120))
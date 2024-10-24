# visuals/shapes/sprite_shapes.py

import pygame
from typing import Optional, Tuple
from .base_shape import BaseShape

class AnimatedSprite(BaseShape):
    """Shape that uses animated sprites for its appearance."""
    def __init__(self, pos: Tuple[float, float], radius: float, color: pygame.Color, 
                 sprite_name: str, sprite_manager, animation_name: str = "default"):
        super().__init__(pos, radius, color)
        self.sprite_manager = sprite_manager
        self.sprite_name = sprite_name
        self.animation_name = animation_name
        self.scale_to_radius = True
        self._current_frame = None

    def draw(self, surface: pygame.Surface) -> None:
        # Get current frame from sprite manager
        frame = self.sprite_manager.get_sprite_frame(self.sprite_name, self.animation_name)
        
        if frame is None:
            # Fallback to a simple circle if sprite not found
            pygame.draw.circle(surface, self.color, 
                             (int(self.pos[0]), int(self.pos[1])), 
                             int(self.radius))
            return

        # Scale sprite to match the desired radius
        if self.scale_to_radius:
            original_size = frame.get_size()
            scale_factor = (self.radius * 2) / max(original_size)
            new_size = (int(original_size[0] * scale_factor), 
                       int(original_size[1] * scale_factor))
            frame = pygame.transform.scale(frame, new_size)

        # Calculate position to center the sprite
        frame_rect = frame.get_rect()
        frame_rect.center = (int(self.pos[0]), int(self.pos[1]))

        # Apply rotation if needed
        if self.rotation != 0:
            frame = pygame.transform.rotate(frame, self.rotation)
            frame_rect = frame.get_rect(center=frame_rect.center)

        # Apply color modulation if not white
        if self.color != pygame.Color(255, 255, 255):
            colored_frame = frame.copy()
            colored_frame.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            frame = colored_frame

        # Draw the frame
        surface.blit(frame, frame_rect)
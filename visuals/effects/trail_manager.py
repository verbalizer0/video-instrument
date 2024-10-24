# visuals/effects/trail_manager.py

import pygame
import numpy as np
from enum import Enum
from typing import Optional, Tuple, List

class TrailType(Enum):
    NONE = "none"
    FADE = "fade"
    MOTION_BLUR = "motion_blur"
    ECHO = "echo"
    RIBBON = "ribbon"

class TrailManager:
    """
    Manages various types of visual trails and effects.
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.trail_type = TrailType.NONE
        self.trail_length = 0.5  # 0.0 to 1.0
        self.trail_opacity = 0.8  # 0.0 to 1.0
        
        # Create surfaces for different trail effects
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.echo_surfaces: List[pygame.Surface] = []
        self.max_echoes = 8
        
        # Initialize echo surfaces
        for _ in range(self.max_echoes):
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            self.echo_surfaces.append(surface)
            
        self.frame_count = 0
        self.last_positions = []  # For ribbon effect

    def update(self, decay_rate: float = 0.95) -> None:
        """Update trail effects."""
        self.frame_count += 1
        
        if self.trail_type == TrailType.FADE:
            # Apply decay to the trail surface
            temp_surface = pygame.Surface(self.trail_surface.get_size(), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, int(255 * decay_rate)))
            self.trail_surface.blit(temp_surface, (0, 0), 
                                  special_flags=pygame.BLEND_RGBA_MULT)
        
        elif self.trail_type == TrailType.ECHO:
            # Shift echo surfaces
            if self.frame_count % 3 == 0:  # Adjust timing of echo shifts
                self.echo_surfaces.pop()
                new_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self.echo_surfaces.insert(0, new_surface)

    def begin_frame(self, screen: pygame.Surface) -> None:
        """Apply existing trails at the start of a new frame."""
        if self.trail_type != TrailType.NONE:
            # Apply existing trails to screen
            alpha = int(255 * self.trail_opacity)
            
            if self.trail_type == TrailType.FADE:
                screen.blit(self.trail_surface, (0, 0), 
                          special_flags=pygame.BLEND_ALPHA_SDL2)
            
            elif self.trail_type == TrailType.ECHO:
                for i, surface in enumerate(self.echo_surfaces):
                    echo_alpha = int(alpha * (1 - i / len(self.echo_surfaces)))
                    fade_surface = surface.copy()
                    fade_surface.set_alpha(echo_alpha)
                    screen.blit(fade_surface, (0, 0))

    def capture_frame(self, screen: pygame.Surface) -> None:
        """Capture the current frame for trail effects."""
        if self.trail_type == TrailType.FADE:
            # Capture current frame to trail surface with decay
            self.trail_surface.blit(screen, (0, 0))
            
        elif self.trail_type == TrailType.ECHO:
            # Capture current frame to newest echo surface
            self.echo_surfaces[0].blit(screen, (0, 0))

    def draw_trail(self, surface: pygame.Surface, positions: List[Tuple[float, float]], 
                  color: pygame.Color, width: int = 1) -> None:
        """Draw trail effects for a moving object."""
        if self.trail_type == TrailType.RIBBON and len(positions) > 1:
            # Draw smooth curve through positions
            if len(positions) >= 3:
                pygame.draw.lines(surface, color, False, positions, width)
            
            # Store limited number of positions for ribbon trail
            max_points = int(50 * self.trail_length)
            self.last_positions = positions[-max_points:] if len(positions) > max_points else positions

    def add_motion_point(self, pos: Tuple[float, float], color: pygame.Color, 
                        size: int = 1) -> None:
        """Add a point for motion blur effect."""
        if self.trail_type == TrailType.MOTION_BLUR:
            # Draw point with decreasing opacity based on trail length
            alpha = int(255 * self.trail_opacity)
            blur_color = color.copy()
            blur_color.a = alpha
            pygame.draw.circle(self.trail_surface, blur_color, 
                             (int(pos[0]), int(pos[1])), size)

    def set_trail_type(self, trail_type: TrailType) -> None:
        """Change the current trail effect type."""
        if self.trail_type != trail_type:
            self.trail_type = trail_type
            self.clear_trails()
            print(f"Trail type set to: {trail_type.value}")

    def clear_trails(self) -> None:
        """Clear all trail surfaces."""
        self.trail_surface.fill((0, 0, 0, 0))
        for surface in self.echo_surfaces:
            surface.fill((0, 0, 0, 0))
        self.last_positions.clear()

    def get_settings(self) -> dict:
        """Get current trail effect settings."""
        return {
            'type': self.trail_type.value,
            'length': self.trail_length,
            'opacity': self.trail_opacity
        }

    def apply_settings(self, settings: dict) -> None:
        """Apply trail effect settings."""
        if 'type' in settings:
            self.set_trail_type(TrailType(settings['type']))
        if 'length' in settings:
            self.trail_length = max(0.0, min(1.0, settings['length']))
        if 'opacity' in settings:
            self.trail_opacity = max(0.0, min(1.0, settings['opacity']))
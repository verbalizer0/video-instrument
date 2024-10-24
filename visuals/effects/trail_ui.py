# visuals/effects/trail_ui.py

import pygame
from typing import Tuple, Optional
from .trail_manager import TrailManager, TrailType

class TrailControlUI:
    """
    User interface for controlling trail effects.
    """
    def __init__(self, trail_manager: TrailManager):
        self.trail_manager = trail_manager
        self.font = pygame.font.Font(None, 24)
        self.visible = False
        self.selected_option = 0  # 0: type, 1: length, 2: opacity
        self.position = (10, 150)  # Position below LFO UI
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the trail control interface."""
        if not self.visible:
            return

        x, y = self.position
        spacing = 25
        current_y = y

        # Draw semi-transparent background
        panel_width = 250
        panel_height = 100
        background = pygame.Surface((panel_width, panel_height))
        background.fill((0, 0, 0))
        background.set_alpha(128)
        surface.blit(background, (x-5, y-5))

        settings = self.trail_manager.get_settings()
        options = [
            f"Trail Type: {settings['type']}",
            f"Length: {settings['length']:.2f}",
            f"Opacity: {settings['opacity']:.2f}"
        ]

        for i, text in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (x, current_y + i * spacing))

    def handle_key(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for trail control."""
        if event.key == pygame.K_t:  # Toggle trail UI
            self.visible = not self.visible
            return
            
        if not self.visible:
            return

        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 3
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 3
        elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            self._adjust_value(event.key == pygame.K_RIGHT)

    def _adjust_value(self, increase: bool) -> None:
        """Adjust the selected trail parameter."""
        settings = self.trail_manager.get_settings()
        
        if self.selected_option == 0:  # Trail Type
            types = list(TrailType)
            current_idx = types.index(TrailType(settings['type']))
            new_idx = (current_idx + (1 if increase else -1)) % len(types)
            self.trail_manager.set_trail_type(types[new_idx])
            
        elif self.selected_option == 1:  # Length
            delta = 0.05 if increase else -0.05
            new_length = max(0.0, min(1.0, settings['length'] + delta))
            self.trail_manager.apply_settings({'length': new_length})
            
        elif self.selected_option == 2:  # Opacity
            delta = 0.05 if increase else -0.05
            new_opacity = max(0.0, min(1.0, settings['opacity'] + delta))
            self.trail_manager.apply_settings({'opacity': new_opacity})
# visuals/backgrounds/original_modes.py

import pygame
import math
import random
from .background_base import Background

class OriginalColorCycleBackground(Background):
    """
    Original color cycling background from the initial implementation.
    """
    def __init__(self):
        super().__init__()
        self.base_hue = 0
        self.color_offset = 0
        self.background_color = pygame.Color(0, 0, 0)

    def update(self, beat_position: float) -> None:
        bg_cycle_length = max(1, int((3600 // self.bpm) * self.cycle_ratio))
        bg_progress = (beat_position % bg_cycle_length) / bg_cycle_length
        
        self.background_color.hsva = (
            (self.base_hue + int(bg_progress * 360)) % 360,
            50,  # saturation
            20,  # value
            100  # alpha
        )

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.background_color)

    def set_base_hue(self, hue: int) -> None:
        self.base_hue = hue % 360

class BlackAndWhiteModeBackground(Background):
    """
    Original black and white mode background with multiple states.
    """
    def __init__(self):
        super().__init__()
        self.mode = 0  # 0: Color, 1: B&W, 2: Inverted B&W, 3: Alternating B&W
        self.background_color = pygame.Color(0, 0, 0)

    def update(self, beat_position: float) -> None:
        if self.mode == 1:  # Standard B&W
            self.background_color = pygame.Color(0, 0, 0)
        elif self.mode == 2:  # Inverted B&W
            self.background_color = pygame.Color(255, 255, 255)
        elif self.mode == 3:  # Alternating B&W
            bg_cycle_length = max(1, int((3600 // self.bpm) * self.cycle_ratio))
            bg_progress = (beat_position % bg_cycle_length) / bg_cycle_length
            bg_value = int(abs(math.sin(bg_progress * math.pi)) * 255)
            self.background_color = pygame.Color(bg_value, bg_value, bg_value)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.background_color)

    def cycle_mode(self) -> None:
        self.mode = (self.mode + 1) % 4
        mode_names = ["Color", "Black and White", 
                     "Inverted Black and White", "Alternating Black and White"]
        print(f"Switched to {mode_names[self.mode]} mode")

class BackgroundManagerExtended:
    """
    Enhanced background manager that includes original modes and new background types.
    """
    def __init__(self):
        self.backgrounds = {}
        self.current_background = None
        self.color_cycle_bg = OriginalColorCycleBackground()
        self.bw_mode_bg = BlackAndWhiteModeBackground()
        self.sprite_manager = None
        self.width = 800
        self.height = 600

    def setup_original_modes(self):
        """Initialize the original background modes."""
        self.add_background("color_cycle_original", self.color_cycle_bg)
        self.add_background("black_and_white", self.bw_mode_bg)
        self.switch_background("color_cycle_original")

    def add_background(self, name: str, background: Background) -> None:
        background.resize(self.width, self.height)
        self.backgrounds[name] = background

    def switch_background(self, name: str) -> None:
        if name in self.backgrounds:
            if self.current_background:
                self.current_background.cleanup()
            self.current_background = self.backgrounds[name]
            print(f"Switched to background: {name}")
        else:
            print(f"Background not found: {name}")

    def update(self, beat_position: float) -> None:
        if self.current_background:
            self.current_background.update(beat_position)

    def draw(self, surface: pygame.Surface) -> None:
        if self.current_background:
            self.current_background.draw(surface)
        else:
            surface.fill(pygame.Color(0))

    def cycle_bw_mode(self) -> None:
        """Cycle through black and white modes."""
        self.bw_mode_bg.cycle_mode()
        if self.bw_mode_bg.mode == 0:  # Switched back to color
            self.switch_background("color_cycle_original")
        else:
            self.switch_background("black_and_white")

    def change_base_hue(self) -> None:
        """Change the base hue of the color cycle background."""
        if isinstance(self.current_background, OriginalColorCycleBackground):
            self.color_cycle_bg.set_base_hue(random.randint(0, 360))
            print(f"Base background hue changed to: {self.color_cycle_bg.base_hue}")

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        for background in self.backgrounds.values():
            background.resize(width, height)

    def cleanup(self) -> None:
        for background in self.backgrounds.values():
            background.cleanup()
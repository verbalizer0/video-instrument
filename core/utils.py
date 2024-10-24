# core/utils.py

import math
import pygame
from typing import Tuple, Optional

def calculate_fps(delta_time: float) -> float:
    """Calculate current FPS from delta time."""
    return 1000 / delta_time if delta_time > 0 else 0

def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to the range 0-1."""
    return (value - min_val) / (max_val - min_val)

def denormalize_value(normalized: float, min_val: float, max_val: float) -> float:
    """Convert a normalized value back to its original range."""
    return min_val + normalized * (max_val - min_val)

def constrain(value: float, min_val: float, max_val: float) -> float:
    """Constrain a value between min and max."""
    return max(min_val, min(max_val, value))

def lerp(start: float, end: float, amount: float) -> float:
    """Linear interpolation between start and end values."""
    return start + (end - start) * amount

def create_smooth_surface(width: int, height: int) -> pygame.Surface:
    """Create a surface optimized for smooth drawing."""
    return pygame.Surface((width, height), pygame.SRCALPHA)

def draw_text(surface: pygame.Surface, text: str, pos: Tuple[int, int], 
              font: pygame.font.Font, color: Tuple[int, int, int], 
              background: Optional[Tuple[int, int, int]] = None) -> pygame.Rect:
    """Draw text with optional background."""
    text_surface = font.render(text, True, color, background)
    text_rect = text_surface.get_rect(topleft=pos)
    if background:
        pygame.draw.rect(surface, background, text_rect)
    surface.blit(text_surface, text_rect)
    return text_rect

def calculate_beat_position(clock_counter: int, ppq: int, bpm: float) -> float:
    """Calculate current beat position from MIDI clock."""
    return (clock_counter % ppq) / ppq

def calculate_bar_position(beat_position: float, beats_per_bar: int = 4) -> float:
    """Calculate position within a bar."""
    return beat_position % beats_per_bar

class Timer:
    """Simple timer for tracking elapsed time."""
    def __init__(self):
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.is_paused = False

    def pause(self):
        """Pause the timer."""
        if not self.is_paused:
            self.paused_time = pygame.time.get_ticks()
            self.is_paused = True

    def resume(self):
        """Resume the timer."""
        if self.is_paused:
            self.start_time += pygame.time.get_ticks() - self.paused_time
            self.is_paused = False

    def reset(self):
        """Reset the timer."""
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.is_paused = False

    def get_elapsed(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.is_paused:
            return self.paused_time - self.start_time
        return pygame.time.get_ticks() - self.start_time
# visuals/backgrounds/background_base.py

import pygame
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple, Dict, Any

class BackgroundType(Enum):
    SOLID = "solid"
    COLOR_CYCLE = "color_cycle"
    SPRITE = "sprite"
    VIDEO = "video"
    PATTERN = "pattern"

class Background(ABC):
    """Base class for all background types."""
    def __init__(self):
        self.width = 0
        self.height = 0
        self.bpm = 120
        self.cycle_ratio = 1.0
        self.params: Dict[str, Any] = {}

    @abstractmethod
    def update(self, beat_position: float) -> None:
        """Update background state based on beat position."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw background to the given surface."""
        pass

    def resize(self, width: int, height: int) -> None:
        """Handle surface resize events."""
        self.width = width
        self.height = height

    def set_bpm(self, bpm: float) -> None:
        """Update BPM value."""
        self.bpm = bpm

    def set_cycle_ratio(self, ratio: float) -> None:
        """Update cycle ratio for BPM-based effects."""
        self.cycle_ratio = ratio

    def cleanup(self) -> None:
        """Clean up any resources."""
        pass

class SolidBackground(Background):
    """Simple solid color background."""
    def __init__(self, color: pygame.Color):
        super().__init__()
        self.color = color

    def update(self, beat_position: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.color)

class SpriteBackground(Background):
    """Background using a sprite or animated sprite."""
    def __init__(self, sprite_manager, sprite_name: str):
        super().__init__()
        self.sprite_manager = sprite_manager
        self.sprite_name = sprite_name
        self.animation = None
        self.surface = None
        self._initialize_sprite()

    def _initialize_sprite(self) -> None:
        if self.sprite_name in self.sprite_manager.sprites:
            self.animation = self.sprite_manager.get_sprite_animation(self.sprite_name)
            if self.animation:
                self.surface = pygame.Surface((self.width, self.height))

    def update(self, beat_position: float) -> None:
        if self.animation:
            self.animation.update()

    def draw(self, surface: pygame.Surface) -> None:
        if self.animation and self.surface:
            frame = self.animation.get_current_frame()
            scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
            surface.blit(scaled_frame, (0, 0))
        else:
            surface.fill(pygame.Color(0))

class VideoBackground(Background):
    """Background using video playback."""
    def __init__(self, video_path: str):
        super().__init__()
        self.video_path = video_path
        self.frame_surface = None
        self.video_capture = None
        try:
            import cv2
            self.video_capture = cv2.VideoCapture(video_path)
        except ImportError:
            print("OpenCV (cv2) is required for video backgrounds")

    def update(self, beat_position: float) -> None:
        if self.video_capture and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
                self.frame_surface = pygame.surfarray.make_surface(frame)
            else:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def draw(self, surface: pygame.Surface) -> None:
        if self.frame_surface:
            surface.blit(self.frame_surface, (0, 0))
        else:
            surface.fill(pygame.Color(0))

    def cleanup(self) -> None:
        if self.video_capture:
            self.video_capture.release()
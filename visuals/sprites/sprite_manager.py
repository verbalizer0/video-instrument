# visuals/sprites/sprite_manager.py

import pygame
import os
import json
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto
from .gif_loader import GifLoader

class AnimationMode(Enum):
    """Available animation playback modes."""
    NORMAL = auto()
    PING_PONG = auto()
    REVERSE = auto()
    LOOP = auto()
    ONCE = auto()

class SpriteAnimation:
    """
    Handles sprite animation playback and control.
    """
    def __init__(self, name: str, frames: List[pygame.Surface], 
                 frame_durations: Optional[List[int]] = None):
        self.name = name
        self.frames = frames
        self.frame_durations = frame_durations or [100] * len(frames)  # Default 100ms
        self.current_frame = 0
        self.frame_time = 0
        self.playing = True
        self.mode = AnimationMode.LOOP
        self.direction = 1  # 1 for forward, -1 for reverse
        self.loop_count = 0
        self.finished = False

    def update(self, dt: float) -> pygame.Surface:
        """
        Update animation state and return current frame.
        
        Args:
            dt: Time elapsed since last update in milliseconds.
            
        Returns:
            Current frame as pygame surface.
        """
        if not self.playing or self.finished:
            return self.frames[self.current_frame]

        self.frame_time += dt
        duration = self.frame_durations[self.current_frame]

        if self.frame_time >= duration:
            self.frame_time = 0
            self._advance_frame()

        return self.frames[self.current_frame]

    def _advance_frame(self) -> None:
        """Update to next frame based on animation mode."""
        if self.mode == AnimationMode.NORMAL or self.mode == AnimationMode.LOOP:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            if self.current_frame == 0:
                self.loop_count += 1
                if self.mode == AnimationMode.NORMAL:
                    self.finished = True
                    self.playing = False

        elif self.mode == AnimationMode.PING_PONG:
            self.current_frame += self.direction
            if self.current_frame >= len(self.frames) or self.current_frame < 0:
                self.direction *= -1
                self.current_frame += self.direction * 2

        elif self.mode == AnimationMode.REVERSE:
            self.current_frame = (self.current_frame - 1) % len(self.frames)

        elif self.mode == AnimationMode.ONCE:
            if self.current_frame < len(self.frames) - 1:
                self.current_frame += 1
            else:
                self.finished = True
                self.playing = False

    def reset(self) -> None:
        """Reset animation to initial state."""
        self.current_frame = 0
        self.frame_time = 0
        self.playing = True
        self.finished = False
        self.loop_count = 0
        self.direction = 1

class SpriteManager:
    """
    Manages sprite loading, storage, and retrieval.
    """
    def __init__(self):
        self.sprites: Dict[str, Dict[str, SpriteAnimation]] = {}
        self.sprite_sheets: Dict[str, pygame.Surface] = {}
        self.sprite_info: Dict[str, dict] = {}
        self.gif_loader = GifLoader()

    def load_sprite_sheet(self, name: str, path: str, 
                         frame_size: Tuple[int, int], 
                         animations: Dict[str, dict]) -> bool:
        """
        Load a sprite sheet and set up animations.
        
        Args:
            name: Identifier for the sprite.
            path: Path to sprite sheet image.
            frame_size: Size of each frame (width, height).
            animations: Dictionary defining animations:
                {
                    "idle": {"start_frame": 0, "num_frames": 4, "duration": 100},
                    "walk": {"start_frame": 4, "num_frames": 8, "duration": 80},
                }
        """
        try:
            # Load sprite sheet
            sheet = pygame.image.load(path).convert_alpha()
            self.sprite_sheets[name] = sheet
            
            # Extract frames
            frames = []
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            cols = sheet_width // frame_size[0]
            rows = sheet_height // frame_size[1]
            
            for row in range(rows):
                for col in range(cols):
                    x = col * frame_size[0]
                    y = row * frame_size[1]
                    rect = pygame.Rect(x, y, frame_size[0], frame_size[1])
                    frame = sheet.subsurface(rect)
                    frames.append(frame)

            # Create animations
            sprite_animations = {}
            for anim_name, anim_info in animations.items():
                start = anim_info["start_frame"]
                count = anim_info["num_frames"]
                duration = anim_info["duration"]
                anim_frames = frames[start:start + count]
                sprite_animations[anim_name] = SpriteAnimation(
                    anim_name,
                    anim_frames,
                    [duration] * count
                )

            self.sprites[name] = sprite_animations
            self.sprite_info[name] = {
                "type": "sheet",
                "frame_size": frame_size,
                "animations": animations
            }
            
            print(f"Loaded sprite sheet '{name}' with {len(animations)} animations")
            return True

        except Exception as e:
            print(f"Error loading sprite sheet {path}: {e}")
            return False

    def load_sprite_sequence(self, name: str, folder_path: str, 
                           animation_name: str = "default", 
                           frame_duration: int = 100) -> bool:
        """Load individual sprite frames from a folder."""
        try:
            frames = []
            frame_files = sorted([f for f in os.listdir(folder_path) 
                                if f.lower().endswith(('.png', '.jpg', '.gif'))])
            
            for frame_file in frame_files:
                frame_path = os.path.join(folder_path, frame_file)
                frame = pygame.image.load(frame_path).convert_alpha()
                frames.append(frame)

            if frames:
                animation = SpriteAnimation(
                    animation_name,
                    frames,
                    [frame_duration] * len(frames)
                )
                
                self.sprites[name] = {animation_name: animation}
                self.sprite_info[name] = {
                    "type": "sequence",
                    "frame_size": frames[0].get_size(),
                    "animations": {animation_name: {
                        "frame_count": len(frames),
                        "duration": frame_duration
                    }}
                }
                
                print(f"Loaded sprite sequence '{name}' with {len(frames)} frames")
                return True
                
            return False

        except Exception as e:
            print(f"Error loading sprite sequence from {folder_path}: {e}")
            return False

    def load_gif(self, name: str, gif_path: str) -> bool:
        """Load a GIF file as a sprite animation."""
        try:
            frames, durations = self.gif_loader.load_gif(gif_path)
            if not frames:
                return False
                
            animation = SpriteAnimation(name, frames, durations)
            self.sprites[name] = {"default": animation}
            self.sprite_info[name] = {
                "type": "gif",
                "frame_size": frames[0].get_size(),
                "frame_count": len(frames)
            }
            
            print(f"Loaded GIF '{name}' with {len(frames)} frames")
            return True
            
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
            return False

    def load_gifs_from_directory(self, directory: str) -> None:
        """Load all GIFs from a directory."""
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            return
            
        for filename in os.listdir(directory):
            if filename.lower().endswith('.gif'):
                name = os.path.splitext(filename)[0]
                path = os.path.join(directory, filename)
                self.load_gif(name, path)

    def get_sprite_animation(self, sprite_name: str, 
                           animation_name: str = "default") -> Optional[SpriteAnimation]:
        """Get an animation instance for a sprite."""
        if sprite_name in self.sprites:
            return self.sprites[sprite_name].get(animation_name)
        return None

    def get_sprite_frame(self, sprite_name: str, 
                        animation_name: str = "default", 
                        dt: float = 16.67) -> Optional[pygame.Surface]:
        """Get current frame for a sprite animation."""
        animation = self.get_sprite_animation(sprite_name, animation_name)
        if animation:
            return animation.update(dt)
        return None

    def save_sprite_info(self, filename: str) -> None:
        """Save sprite configuration to file."""
        with open(filename, 'w') as f:
            json.dump(self.sprite_info, f, indent=2)

    def load_sprite_info(self, filename: str) -> None:
        """Load sprite configuration from file."""
        with open(filename, 'r') as f:
            self.sprite_info = json.load(f)
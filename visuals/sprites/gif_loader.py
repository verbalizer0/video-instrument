# visuals/sprites/gif_loader.py

import pygame
import os
from PIL import Image
from typing import List, Tuple, Optional

class GifLoader:
    """
    Handles loading and converting GIF files into pygame surfaces.
    """
    @staticmethod
    def load_gif(gif_path: str) -> Tuple[List[pygame.Surface], List[int]]:
        """
        Load a GIF and return a list of pygame surfaces and frame durations.
        
        Args:
            gif_path: Path to the GIF file.
            
        Returns:
            Tuple containing:
            - List of pygame surfaces (frames)
            - List of frame durations in milliseconds
        """
        try:
            pil_image = Image.open(gif_path)
            frames = []
            durations = []
            
            # Get all frames from GIF
            try:
                while True:
                    # Convert PIL image to RGBA if needed
                    if pil_image.mode != 'RGBA':
                        pil_image = pil_image.convert('RGBA')
                    
                    # Get frame duration in milliseconds
                    duration = pil_image.info.get('duration', 100)  # Default to 100ms
                    durations.append(duration)
                    
                    # Convert to pygame surface
                    str_format = pil_image.tobytes("raw", 'RGBA')
                    pygame_surface = pygame.image.fromstring(
                        str_format,
                        pil_image.size,
                        'RGBA'
                    )
                    
                    frames.append(pygame_surface)
                    pil_image.seek(pil_image.tell() + 1)  # Go to next frame
                    
            except EOFError:
                pass  # End of frames
            
            pil_image.close()
            return frames, durations
            
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
            return [], []
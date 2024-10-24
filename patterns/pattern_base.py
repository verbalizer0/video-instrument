# patterns/pattern_base.py

# Core imports first
import pygame
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

# Then local imports
from core.parameter_manager import ParameterManager
from core.systems import CoreSystems
from visuals.effects.trail_manager import TrailManager
from visuals.backgrounds.original_modes import BackgroundManagerExtended
from visuals.shapes.shape_factory import ShapeFactory

class BasePattern(ABC):
    """
    Base class for all visual patterns.
    Provides common functionality and required interface.
    """
    def __init__(self, screen: pygame.Surface, 
                 core_systems: CoreSystems,
                 sprite_manager=None):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.core_systems = core_systems
        self.param_manager = core_systems.parameter_manager
        self.sprite_manager = sprite_manager
        
        # Initialize managers
        self.trail_manager = TrailManager(self.width, self.height)
        self.background_manager = BackgroundManagerExtended()
        if sprite_manager:
            self.background_manager.register_sprite_manager(sprite_manager)
        
        # Initialize backgrounds
        self._setup_backgrounds()
        
        # Create drawing surface
        self.draw_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Pattern state
        self.active = True
        self.beat_position = 0.0
        self.params: Dict[str, Any] = {}

    def _setup_backgrounds(self):
        """Initialize available backgrounds."""
        # Setup original modes first
        self.background_manager.setup_original_modes()
        
        # Add other background types
        try:
            from visuals.backgrounds.patterns.wave_pattern import WavePattern
            # Add wave pattern background
            self.background_manager.add_background(
                "wave",
                WavePattern()
            )
        except ImportError:
            print("Wave pattern background not available")
        
        # Add sprite backgrounds if available
        if self.sprite_manager:
            # Import here to avoid circular imports
            from visuals.backgrounds.background_base import SpriteBackground
            for sprite_name in self.sprite_manager.sprites:
                self.background_manager.add_background(
                    f"sprite_{sprite_name}",
                    SpriteBackground(self.sprite_manager, sprite_name)
                )

    @abstractmethod
    def update(self) -> None:
        """Update pattern state."""
        if not self.active:
            return
            
        # Update background with current beat position
        self.background_manager.update(self.beat_position)

    def draw(self) -> None:
        """Draw pattern with background and trails."""
        if not self.active:
            return
            
        # Draw background
        self.background_manager.draw(self.screen)
        
        # Begin frame - apply existing trails
        self.trail_manager.begin_frame(self.screen)
        
        # Clear drawing surface
        self.draw_surface.fill((0, 0, 0, 0))
        
        # Draw current frame
        self.draw_frame(self.draw_surface)
        
        # Capture frame for trails
        self.trail_manager.capture_frame(self.draw_surface)
        
        # Draw final result to screen
        self.screen.blit(self.draw_surface, (0, 0))

    @abstractmethod
    def draw_frame(self, surface: pygame.Surface) -> None:
        """Draw single frame of the pattern."""
        pass

    def handle_note(self, note: int, velocity: int) -> None:
        """Handle MIDI note input."""
        pass

    def handle_cc(self, cc_number: int, value: int) -> None:
        """Handle MIDI CC input."""
        pass

    def resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        self.width = width
        self.height = height
        self.draw_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.trail_manager = TrailManager(width, height)
        self.background_manager.resize(width, height)

    def toggle_black_and_white_mode(self) -> None:
        """Toggle through black and white modes."""
        self.background_manager.cycle_bw_mode()

    def cycle_background(self) -> None:
        """Cycle through available backgrounds."""
        self.background_manager.cycle_background()

    def change_background_color(self) -> None:
        """Change the base hue of the color cycle background."""
        self.background_manager.change_base_hue()

    def cleanup(self) -> None:
        """Clean up resources."""
        self.active = False
        self.trail_manager.clear_trails()
        self.background_manager.cleanup()
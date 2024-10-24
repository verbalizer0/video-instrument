# core/systems.py

from typing import Optional
import pygame
from .parameter_manager import ParameterManager
from .lfo_manager import LFOManager
from .lfo_ui import LFOControlUI

class CoreSystems:
    """
    Centralizes access to all core systems and manages their interactions.
    """
    def __init__(self):
        self.parameter_manager = ParameterManager()
        self.lfo_manager = LFOManager(self.parameter_manager)
        self.lfo_ui = LFOControlUI(self.lfo_manager)
        
        # Initialize default LFOs
        self._setup_default_lfos()

    def _setup_default_lfos(self):
        """Create and configure default LFOs."""
        from .lfo_manager import WaveformType
        
        # Create LFOs with different waveforms
        lfo1 = self.lfo_manager.create_lfo(WaveformType.SINE)
        lfo2 = self.lfo_manager.create_lfo(WaveformType.TRIANGLE)
        lfo3 = self.lfo_manager.create_lfo(WaveformType.SQUARE)
        
        # Configure frequencies
        self.lfo_manager.configure_lfo(lfo1, frequency=0.5)  # One cycle every 2 beats
        self.lfo_manager.configure_lfo(lfo2, frequency=0.25)  # One cycle every 4 beats
        self.lfo_manager.configure_lfo(lfo3, frequency=1.0)  # One cycle per beat

    def update(self, beat_position: float):
        """Update all core systems."""
        self.lfo_manager.update(beat_position)

    def draw_ui(self, surface: pygame.Surface):
        """Draw UI elements for all core systems."""
        self.lfo_ui.draw(surface)

    def handle_key(self, event: pygame.event.Event) -> bool:
        """
        Handle keyboard input for core systems.
        Returns: True if input was handled, False otherwise.
        """
        self.lfo_ui.handle_key(event)
        return True

    def save_state(self, filename_prefix: str):
        """Save state of all core systems."""
        self.parameter_manager.save_mappings(f"{filename_prefix}_parameters.json")
        lfo_state = self.lfo_manager.save_state()
        # Add more state saving as needed

    def load_state(self, filename_prefix: str):
        """Load state of all core systems."""
        self.parameter_manager.load_mappings(f"{filename_prefix}_parameters.json")
        # Add more state loading as needed

    def cleanup(self):
        """Clean up resources for all core systems."""
        pass  # Add cleanup code if needed
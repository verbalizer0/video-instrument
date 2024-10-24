# __init__.py

"""
Video Instrument - A visual performance tool using MIDI input.
"""

from . import patterns
from . import visuals
from .video_instrument import VideoInstrument

# Version info
__version__ = '1.0.0'
__author__ = 'Your Name'
__license__ = 'MIT'

# Define what gets imported with "from video_instrument import *"
__all__ = [
    'VideoInstrument',
    'patterns',
    'visuals'
]

# Optional: Set up any package-level configuration
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
WINDOW_TITLE = "Video Instrument"
FPS = 60
MIDI_PPQ = 24  # Pulses Per Quarter Note
DEFAULT_BPM = 120

# Optional: Define any package-level convenience functions
def create_instrument():
    """Convenience function to create and initialize a VideoInstrument instance."""
    return VideoInstrument()
# core/config.py

"""
Configuration settings for the video instrument core systems.
"""

# Performance settings
FPS = 60
FRAME_TIME = 1000 / FPS  # milliseconds per frame

# MIDI settings
MIDI_PPQ = 24  # Pulses Per Quarter note
DEFAULT_BPM = 120

# Display settings
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
WINDOW_TITLE = "Video Instrument"

# UI settings
UI_FONT_SIZE = 24
UI_COLORS = {
    'text': (255, 255, 255),
    'highlight': (255, 255, 0),
    'background': (0, 0, 0, 128)
}

# LFO settings
DEFAULT_LFO_CONFIG = {
    'sine': {
        'frequency': 0.5,
        'amplitude': 1.0,
        'phase': 0.0
    },
    'triangle': {
        'frequency': 0.25,
        'amplitude': 1.0,
        'phase': 0.0
    },
    'square': {
        'frequency': 1.0,
        'amplitude': 1.0,
        'phase': 0.0
    }
}

# File paths
RESOURCES_PATH = "resources"
SPRITE_PATH = f"{RESOURCES_PATH}/sprites"
GIF_PATH = f"{SPRITE_PATH}/gifs"
SEQUENCE_PATH = f"{SPRITE_PATH}/sequences"
CONFIG_PATH = "config"

# Pattern settings
DEFAULT_PATTERN = "pattern_00"
PATTERN_PREFIX = "pattern_"

# Control mappings
DEFAULT_MIDI_MAPPINGS = {
    'cc': {
        1: 'connection_distance',
        2: 'node_speed',
        3: 'activation_spread',
        4: 'decay_rate'
    }
}

# Background settings
BACKGROUND_CYCLE_RATIOS = {
    'very_slow': 0.25,
    'slow': 0.5,
    'normal': 1.0,
    'fast': 2.0,
    'very_fast': 4.0
}
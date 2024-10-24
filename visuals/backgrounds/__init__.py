# visuals/backgrounds/__init__.py

from .background_base import (
    BackgroundType,
    Background,
    SolidBackground,
    SpriteBackground,
    VideoBackground
)

from .original_modes import (
    OriginalColorCycleBackground,
    BlackAndWhiteModeBackground,
    BackgroundManagerExtended
)

__all__ = [
    'BackgroundType',
    'Background',
    'SolidBackground',
    'SpriteBackground',
    'VideoBackground',
    'OriginalColorCycleBackground',
    'BlackAndWhiteModeBackground',
    'BackgroundManagerExtended'
]
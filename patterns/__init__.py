# patterns/__init__.py

# Import necessary core modules first
import pygame

# Import pattern base and implementations
from .pattern_base import BasePattern
from . import pattern_00
from . import pattern_01
from . import pattern_02
from . import pattern_03

__all__ = [
    'BasePattern',
    'pattern_00',
    'pattern_01',
    'pattern_02',
    'pattern_03'
]
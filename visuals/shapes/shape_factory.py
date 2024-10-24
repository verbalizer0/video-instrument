# visuals/shapes/shape_factory.py

from typing import Dict, Type, List
from .base_shape import BaseShape
from .basic_shapes import (Circle, Triangle, Square, Pentagram, 
                          InvertedPentagram, ChaosStarArrow, Star)
from .sprite_shapes import AnimatedSprite

class ShapeFactory:
    """
    Factory class for creating different types of shapes.
    """
    _shapes: Dict[str, Type[BaseShape]] = {
        'circle': Circle,
        'triangle': Triangle,
        'square': Square,
        'pentagram': Pentagram,
        'inverted_pentagram': InvertedPentagram,
        'chaos_star': ChaosStarArrow,
        'star': Star,
        'sprite': AnimatedSprite
    }

    @classmethod
    def create_shape(cls, shape_type: str, pos: tuple, radius: float, 
                    color: pygame.Color, **kwargs) -> BaseShape:
        """Create a shape instance of the specified type."""
        if shape_type not in cls._shapes:
            raise ValueError(f"Unknown shape type: {shape_type}")
            
        shape_class = cls._shapes[shape_type]
        
        if shape_type == 'sprite':
            return shape_class(pos, radius, color, 
                             sprite_name=kwargs.get('sprite_name', ''),
                             sprite_manager=kwargs.get('sprite_manager'),
                             animation_name=kwargs.get('animation_name', 'default'))
        elif shape_type == 'star':
            return shape_class(pos, radius, color,
                             points=kwargs.get('points', 5),
                             inner_radius_ratio=kwargs.get('inner_radius_ratio', 0.5))
        
        return shape_class(pos, radius, color)

    @classmethod
    def get_available_shapes(cls) -> List[str]:
        """Get a list of all available shape types."""
        return list(cls._shapes.keys())

    @classmethod
    def register_shape(cls, name: str, shape_class: Type[BaseShape]) -> None:
        """Register a new shape type."""
        cls._shapes[name] = shape_class
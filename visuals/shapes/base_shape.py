# visuals/shapes/base_shape.py

import math
import pygame
from abc import ABC, abstractmethod
from typing import Tuple, List

class BaseShape(ABC):
    """
    Base class for all shapes in the system.
    """
    def __init__(self, pos: Tuple[float, float], radius: float, color: pygame.Color):
        self.pos = pos
        self.radius = radius
        self.color = color
        self.rotation = 0  # Rotation in degrees

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the shape on the given surface."""
        pass

    def rotate(self, degrees: float) -> None:
        """Rotate the shape by the specified degrees."""
        self.rotation = (self.rotation + degrees) % 360

    def _rotate_point(self, point: Tuple[float, float], origin: Tuple[float, float], 
                     angle: float) -> Tuple[float, float]:
        """Rotate a point around an origin by given angle in degrees."""
        angle_rad = math.radians(angle)
        ox, oy = origin
        px, py = point
        
        qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
        qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
        
        return (qx, qy)

    def _calculate_vertices(self, num_vertices: int, radius: float) -> List[Tuple[float, float]]:
        """Calculate vertices for regular polygon shapes."""
        vertices = []
        for i in range(num_vertices):
            angle = math.radians(i * (360 / num_vertices) - self.rotation)
            x = self.pos[0] + radius * math.cos(angle)
            y = self.pos[1] + radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
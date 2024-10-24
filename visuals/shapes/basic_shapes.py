# visuals/shapes/basic_shapes.py

import pygame
import math
from typing import List, Tuple
from .base_shape import BaseShape

class Circle(BaseShape):
    """Simple circle shape."""
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, 
                         (int(self.pos[0]), int(self.pos[1])), 
                         int(self.radius))

class Triangle(BaseShape):
    """Equilateral triangle shape."""
    def draw(self, surface: pygame.Surface) -> None:
        points = [
            (self.pos[0], self.pos[1] - self.radius),
            (self.pos[0] - self.radius * math.sqrt(3) / 2, self.pos[1] + self.radius / 2),
            (self.pos[0] + self.radius * math.sqrt(3) / 2, self.pos[1] + self.radius / 2)
        ]
        if self.rotation != 0:
            points = [self._rotate_point(p, self.pos, self.rotation) for p in points]
        pygame.draw.polygon(surface, self.color, points)

class Square(BaseShape):
    """Square shape."""
    def draw(self, surface: pygame.Surface) -> None:
        if self.rotation == 0:
            rect = pygame.Rect(
                int(self.pos[0] - self.radius),
                int(self.pos[1] - self.radius),
                int(self.radius * 2),
                int(self.radius * 2)
            )
            pygame.draw.rect(surface, self.color, rect)
        else:
            points = [
                (self.pos[0] - self.radius, self.pos[1] - self.radius),
                (self.pos[0] + self.radius, self.pos[1] - self.radius),
                (self.pos[0] + self.radius, self.pos[1] + self.radius),
                (self.pos[0] - self.radius, self.pos[1] + self.radius)
            ]
            points = [self._rotate_point(p, self.pos, self.rotation) for p in points]
            pygame.draw.polygon(surface, self.color, points)

class Pentagram(BaseShape):
    """Five-pointed star (pentagram) shape."""
    def draw(self, surface: pygame.Surface) -> None:
        # Calculate the five outer points of the star
        points = []
        for i in range(5):
            angle = math.radians(72 * i - 72)  # -72 to start at top
            x = self.pos[0] + self.radius * math.cos(angle)
            y = self.pos[1] + self.radius * math.sin(angle)
            points.append((x, y))
        
        # Connect points to create the star
        draw_points = []
        star_sequence = [0, 2, 4, 1, 3, 0]  # Sequence to draw the star
        for i in star_sequence:
            draw_points.append(points[i])
            
        if self.rotation != 0:
            draw_points = [self._rotate_point(p, self.pos, self.rotation) for p in draw_points]
        
        pygame.draw.polygon(surface, self.color, draw_points)

class InvertedPentagram(Pentagram):
    """Inverted five-pointed star shape."""
    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        self.rotation += 180

class ChaosStarArrow(BaseShape):
    """Eight-pointed chaos star shape."""
    def draw(self, surface: pygame.Surface) -> None:
        for i in range(8):
            angle = math.radians(45 * i + self.rotation)
            # Arrow head point
            x1 = self.pos[0] + self.radius * math.cos(angle)
            y1 = self.pos[1] + self.radius * math.sin(angle)
            # Arrow base points
            base_radius = self.radius * 0.7
            width = self.radius * 0.2
            angle_width = math.radians(10)
            
            x2 = self.pos[0] + base_radius * math.cos(angle + angle_width)
            y2 = self.pos[1] + base_radius * math.sin(angle + angle_width)
            x3 = self.pos[0] + base_radius * math.cos(angle - angle_width)
            y3 = self.pos[1] + base_radius * math.sin(angle - angle_width)
            
            pygame.draw.polygon(surface, self.color, [(x1, y1), (x2, y2), (x3, y3)])

class Star(BaseShape):
    """Configurable multi-pointed star shape."""
    def __init__(self, pos: Tuple[float, float], radius: float, color: pygame.Color, 
                 points: int = 5, inner_radius_ratio: float = 0.5):
        super().__init__(pos, radius, color)
        self.points = points
        self.inner_radius_ratio = inner_radius_ratio

    def draw(self, surface: pygame.Surface) -> None:
        vertices = []
        for i in range(self.points * 2):
            angle = math.radians(i * 180 / self.points - self.rotation)
            radius = self.radius if i % 2 == 0 else self.radius * self.inner_radius_ratio
            x = self.pos[0] + radius * math.cos(angle)
            y = self.pos[1] + radius * math.sin(angle)
            vertices.append((x, y))
        pygame.draw.polygon(surface, self.color, vertices)
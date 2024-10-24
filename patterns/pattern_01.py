# patterns/pattern_01.py

# Standard library imports first
import random
import math
from typing import List, Tuple

# Third-party imports second
import pygame

# Local imports last
from .pattern_base import BasePattern
from visuals.shapes.shape_factory import ShapeFactory
from visuals.effects.trail_manager import TrailType

class Particle:
    """
    Represents a single particle in the trail demonstration.
    """
    def __init__(self, x: float, y: float, speed: float, angle: float):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.color = self._random_color()
        self.size = random.uniform(2, 8)
        self.life = 1.0
        self.position_history: List[Tuple[float, float]] = []
        self.max_history = 50

    def _random_color(self) -> pygame.Color:
        """Generate a random color for the particle."""
        color = pygame.Color(0)
        color.hsva = (random.randint(0, 360), 100, 100, 100)
        return color

    def update(self, width: int, height: int, decay_rate: float) -> bool:
        """Update particle state and return False if particle is dead."""
        # Store position history
        self.position_history.append((self.x, self.y))
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)

        # Update position
        self.x = (self.x + math.cos(self.angle) * self.speed) % width
        self.y = (self.y + math.sin(self.angle) * self.speed) % height
        
        # Update life
        self.life *= decay_rate
        return self.life > 0.01

class TrailShowcasePattern(BasePattern):
    """
    Pattern that showcases different trail effects.
    """
    def __init__(self, screen: pygame.Surface, core_systems, sprite_manager=None):
        super().__init__(screen, core_systems, sprite_manager)
        self.particles: List[Particle] = []
        self.spawn_timer = 0
        self.pattern_mode = 0  # 0: random, 1: spiral, 2: fountain
        self.current_trail_type = 0
        
        # Initialize with fade trail
        self.trail_manager.set_trail_type(TrailType.FADE)
        
        # Pattern-specific parameters
        self.params.update({
            'spawn_rate': 2,
            'particle_speed': 3,
            'particle_decay': 0.99,
            'trail_length': 0.5,
            'trail_opacity': 0.8
        })

    def update(self) -> None:
        """Update pattern state."""
        super().update()
        
        # Update existing particles
        self.particles = [p for p in self.particles 
                         if p.update(self.width, self.height, 
                                   self.params['particle_decay'])]
        
        # Spawn new particles
        self.spawn_timer += 1
        if self.spawn_timer >= self.params['spawn_rate']:
            self.spawn_timer = 0
            self.spawn_particle()
            
        # Update trail manager
        self.trail_manager.update()

    def spawn_particle(self) -> None:
        """Spawn a new particle based on current pattern mode."""
        if self.pattern_mode == 0:  # Random
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            angle = random.uniform(0, math.pi * 2)
            
        elif self.pattern_mode == 1:  # Spiral
            angle = len(self.particles) * 0.1
            radius = 100 + len(self.particles) % 100
            x = self.width/2 + math.cos(angle) * radius
            y = self.height/2 + math.sin(angle) * radius
            angle += math.pi/2  # Perpendicular to radius
            
        else:  # Fountain
            x = self.width/2
            y = self.height
            angle = random.uniform(-math.pi * 0.4, -math.pi * 0.6)

        self.particles.append(
            Particle(x, y, self.params['particle_speed'], angle)
        )

    def draw_frame(self, surface: pygame.Surface) -> None:
        """Draw the current frame."""
        # Draw particles and their trails
        for particle in self.particles:
            # Draw particle trail
            if len(particle.position_history) > 1:
                self.trail_manager.draw_trail(
                    surface,
                    particle.position_history,
                    particle.color,
                    max(1, int(particle.size * particle.life))
                )

            # Draw particle
            alpha = int(255 * particle.life)
            color = particle.color.copy()
            color.a = alpha
            pygame.draw.circle(
                surface,
                color,
                (int(particle.x), int(particle.y)),
                max(1, int(particle.size * particle.life))
            )

    def handle_note(self, note: int, velocity: int) -> None:
        """Handle MIDI note input."""
        if note == 0:  # Change pattern mode
            self.pattern_mode = (self.pattern_mode + 1) % 3
            mode_names = ["Random", "Spiral", "Fountain"]
            print(f"Pattern mode: {mode_names[self.pattern_mode]}")
            
        elif note == 1:  # Cycle trail type
            self.current_trail_type = (self.current_trail_type + 1) % len(TrailType)
            self.trail_manager.set_trail_type(list(TrailType)[self.current_trail_type])
            
        else:  # Spawn particles based on note
            count = max(1, velocity // 20)
            for _ in range(count):
                self.spawn_particle()
            
            # Adjust particle speed based on velocity
            self.params['particle_speed'] = 2 + (velocity / 127) * 4

    def handle_cc(self, cc_number: int, cc_value: int) -> None:
        """Handle MIDI CC input."""
        normalized = cc_value / 127
        
        if cc_number == 1:  # Spawn rate
            self.params['spawn_rate'] = max(1, int(10 * (1 - normalized)))
            
        elif cc_number == 2:  # Particle decay
            self.params['particle_decay'] = 0.95 + normalized * 0.04
            
        elif cc_number == 3:  # Trail length
            self.params['trail_length'] = normalized
            self.trail_manager.apply_settings({'length': normalized})
            
        elif cc_number == 4:  # Trail opacity
            self.params['trail_opacity'] = normalized
            self.trail_manager.apply_settings({'opacity': normalized})
# patterns/pattern_00.py

# Standard library imports first
import random
import math
from typing import List, Tuple

# Third-party imports second
import pygame

# Local imports last
from .pattern_base import BasePattern
from visuals.shapes.shape_factory import ShapeFactory

class Node:
    """
    Represents a single node in the neural network visualization.
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.connections: List['Node'] = []
        self.activation = 0
        self.original_color = self._random_color()
        self.color = self.original_color
        self.size = random.uniform(3, 15)
        self.shape = random.choice([0, 1, 2])  # Circle, Triangle, Square
        self.position_history: List[Tuple[float, float]] = []
        self.max_history = 50

    def _random_color(self) -> pygame.Color:
        """Generate a random color."""
        color = pygame.Color(0)
        color.hsva = (random.randint(0, 360), 100, 100, 100)
        return color

    def update(self, width: float, height: float, decay_rate: float) -> None:
        """Update node position and state."""
        # Store position history for trails
        self.position_history.append((self.x, self.y))
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)

        # Update position
        self.x = (self.x + self.vx) % width
        self.y = (self.y + self.vy) % height
        self.activation *= decay_rate

    def randomize_direction(self, maintain_speed: bool = True) -> None:
        """Randomize movement direction."""
        angle = random.uniform(0, 2 * math.pi)
        if maintain_speed:
            speed = math.sqrt(self.vx**2 + self.vy**2)
        else:
            speed = random.uniform(0.1, 1.0)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

class NeuralNetworkPattern(BasePattern):
    """
    Neural network visualization pattern.
    """
    def __init__(self, screen: pygame.Surface, core_systems, sprite_manager=None):
        super().__init__(screen, core_systems, sprite_manager)
        
        # Initialize nodes
        self.nodes = [Node(random.randint(0, self.width), 
                          random.randint(0, self.height)) 
                     for _ in range(50)]
        self.update_connections()
        
        # Pattern parameters
        self.shape_mode = 0  # 0: Mixed, 1-7: Specific shapes
        
        # Register pattern-specific parameters
        self._register_parameters()

    def _register_parameters(self):
        """Register pattern-specific parameters with parameter manager."""
        self.param_manager.add_parameter(
            "node_count", 50, 10, 200, int, "pattern")
        self.param_manager.add_parameter(
            "connection_distance", 100, 50, 300, float, "pattern")
        self.param_manager.add_parameter(
            "node_speed", 0.5, 0.1, 4.0, float, "pattern")
        self.param_manager.add_parameter(
            "activation_spread", 0.5, 0.0, 1.0, float, "pattern")
        self.param_manager.add_parameter(
            "decay_rate", 0.99, 0.9, 0.999, float, "pattern")

    def update_connections(self) -> None:
        """Update node connections based on distance."""
        connection_distance = self.param_manager.get_value('connection_distance')
        for node in self.nodes:
            node.connections = [
                other for other in self.nodes 
                if other != node and 
                math.hypot(node.x - other.x, node.y - other.y) < connection_distance
            ]

    def update(self) -> None:
        """Update pattern state."""
        super().update()
        
        # Update nodes
        for node in self.nodes:
            node.update(
                self.width, 
                self.height, 
                self.param_manager.get_value('decay_rate')
            )
            
        # Update connections
        self.update_connections()
        
        # Update trail manager
        self.trail_manager.update()

    def draw_frame(self, surface: pygame.Surface) -> None:
        """Draw the current frame."""
        # Draw node trails
        for node in self.nodes:
            if len(node.position_history) > 1:
                self.trail_manager.draw_trail(
                    surface,
                    node.position_history,
                    node.color,
                    max(1, int(node.size * 0.5))
                )

        # Draw connections
        for node in self.nodes:
            for connection in node.connections:
                if self.background_manager.bw_mode_bg.mode == 0:  # Color mode
                    color = pygame.Color(
                        node.color.r, node.color.g, node.color.b, 255)
                else:  # B&W mode
                    color = self._get_bw_color()
                    
                pygame.draw.line(
                    surface, 
                    color,
                    (int(node.x), int(node.y)),
                    (int(connection.x), int(connection.y))
                )

        # Draw nodes
        for node in self.nodes:
            self._draw_node(surface, node)

    def _draw_node(self, surface: pygame.Surface, node: Node) -> None:
        """Draw a single node."""
        radius = max(int(node.size + node.activation * 10), 1)
        color = node.color if self.background_manager.bw_mode_bg.mode == 0 else self._get_bw_color()
        
        shape = self._get_shape_type(node.shape)
        shape_obj = ShapeFactory.create_shape(
            shape,
            (int(node.x), int(node.y)),
            radius,
            color
        )
        shape_obj.draw(surface)

    def _get_shape_type(self, shape_index: int) -> str:
        """Get the current shape type based on mode and index."""
        if self.shape_mode == 0:  # Mixed mode
            shape_types = ['circle', 'triangle', 'square', 'pentagram', 
                         'inverted_pentagram', 'chaos_star', 'star']
            return shape_types[shape_index % len(shape_types)]
        else:
            shape_types = ['circle', 'triangle', 'square', 'pentagram', 
                         'inverted_pentagram', 'chaos_star', 'star']
            return shape_types[self.shape_mode - 1]

    def _get_bw_color(self) -> pygame.Color:
        """Get appropriate color based on black and white mode."""
        mode = self.background_manager.bw_mode_bg.mode
        if mode == 1:  # Standard B&W
            return pygame.Color(255, 255, 255)
        elif mode == 2:  # Inverted B&W
            return pygame.Color(0, 0, 0)
        else:  # Alternating B&W
            bg_color = self.background_manager.bw_mode_bg.background_color
            value = 255 if bg_color.r == 0 else 0
            return pygame.Color(value, value, value)

    def handle_note(self, note: int, velocity: int) -> None:
        """Handle MIDI note input."""
        if note == 0:
            self.toggle_black_and_white_mode()
            return

        # Find closest node to note position
        y_pos = self.height - (note - 36) / (84 - 36) * self.height
        closest_node = min(self.nodes, 
                         key=lambda node: abs(node.y - y_pos))
        
        # Set node activation
        closest_node.activation = velocity / 127
        
        # Update node color in color mode
        if self.background_manager.bw_mode_bg.mode == 0:
            hue = int((note - 36) / (84 - 36) * 360) % 360
            closest_node.color.hsva = (hue, 100, 100, 100)
            closest_node.original_color = closest_node.color
        
        # Spread activation to connected nodes
        for connection in closest_node.connections:
            connection.activation = min(
                connection.activation + 
                closest_node.activation * 
                self.param_manager.get_value('activation_spread'),
                1.0
            )
            
            # Update connection color in color mode
            if self.background_manager.bw_mode_bg.mode == 0:
                new_hue = int((hue + random.uniform(-30, 30)) % 360)
                connection.color.hsva = (new_hue, 100, 100, 100)
                connection.original_color = connection.color

        # Randomize node directions
        speed_factor = 1 + (velocity / 127)
        for node in self.nodes:
            node.randomize_direction()
            node.vx *= speed_factor
            node.vy *= speed_factor

    def handle_cc(self, cc_number: int, cc_value: int) -> None:
        """Handle MIDI CC input."""
        normalized_value = cc_value / 127
        
        # Update parameters based on CC number
        if cc_number == 1:
            self.param_manager.set_value(
                'connection_distance',
                50 + normalized_value * 250
            )
            self.update_connections()
            
        elif cc_number == 2:
            self.param_manager.set_value(
                'node_speed',
                0.1 + normalized_value * 3.9
            )
            for node in self.nodes:
                speed = random.uniform(0, self.param_manager.get_value('node_speed'))
                node.randomize_direction(False)
                
        elif cc_number == 3:
            self.param_manager.set_value('activation_spread', normalized_value)
            
        elif cc_number == 4:
            self.param_manager.set_value(
                'decay_rate',
                0.99 + normalized_value * 0.009
            )

    # patterns/pattern_00.py (continued)

    def cycle_shape_mode(self) -> None:
        """Cycle through available shape modes."""
        self.shape_mode = (self.shape_mode + 1) % 8  # 0-7 for all shape types
        shape_modes = [
            "Mixed", "Circles", "Triangles", "Squares", 
            "Pentagrams", "Inverted Pentagrams", "Chaos Stars", "Stars"
        ]
        print(f"Shape mode changed to: {shape_modes[self.shape_mode]}")

    def resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        super().resize(width, height)
        # Adjust node positions to new dimensions
        for node in self.nodes:
            node.x = (node.x / self.width) * width
            node.y = (node.y / self.height) * height
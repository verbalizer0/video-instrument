# core/parameter_manager.py

from typing import Any, Dict, Optional
import json

class Parameter:
    """
    Represents a single controllable parameter in the system.
    """
    def __init__(self, 
                 name: str,
                 default_value: Any,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None,
                 value_type: type = float,
                 category: str = "misc"):
        self.name = name
        self.value = default_value
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.value_type = value_type
        self.category = category
        self.midi_cc = None
        self.lfo_id = None
        
    def set_value(self, value: Any) -> None:
        """Set parameter value with type and range checking."""
        if self.value_type == float:
            value = float(value)
            if self.min_value is not None:
                value = max(self.min_value, value)
            if self.max_value is not None:
                value = min(self.max_value, value)
        elif self.value_type == int:
            value = int(value)
            if self.min_value is not None:
                value = max(self.min_value, value)
            if self.max_value is not None:
                value = min(self.max_value, value)
        self.value = value

class ParameterManager:
    """
    Manages all controllable parameters in the video instrument system.
    """
    def __init__(self):
        self.parameters: Dict[str, Parameter] = {}
        self.cc_mappings: Dict[int, str] = {}  # CC number -> parameter name
        self.lfo_mappings: Dict[int, str] = {}  # LFO ID -> parameter name
        
        # Initialize with default parameters
        self._init_default_parameters()

    def _init_default_parameters(self):
        """Initialize default system parameters."""
        # Global parameters
        self.add_parameter("bpm", 120, 30, 300, int, "global")
        self.add_parameter("bg_color_cycle_ratio", 1.0, 0.0, 16.0, float, "global")
        self.add_parameter("beat_position", 0.0, 0.0, None, float, "global")
        
        # Visual parameters
        self.add_parameter("trail_length", 0, 0, 100, int, "visual")
        self.add_parameter("trail_opacity", 1.0, 0.0, 1.0, float, "visual")
        
        # Motion parameters
        self.add_parameter("node_speed", 0.5, 0.1, 4.0, float, "motion")
        self.add_parameter("connection_distance", 100, 50, 300, float, "motion")
        self.add_parameter("activation_spread", 0.5, 0.0, 1.0, float, "motion")
        self.add_parameter("decay_rate", 0.99, 0.9, 0.999, float, "motion")

        # Shape parameters
        self.add_parameter("shape_mode", 0, 0, 7, int, "visual")

    def add_parameter(self, name: str, default_value: Any, 
                     min_value: Optional[float] = None, 
                     max_value: Optional[float] = None,
                     value_type: type = float,
                     category: str = "misc") -> None:
        """Add a new parameter to the manager."""
        self.parameters[name] = Parameter(
            name, default_value, min_value, max_value, value_type, category
        )

    def get_value(self, name: str) -> Any:
        """Get the current value of a parameter."""
        return self.parameters[name].value if name in self.parameters else None

    def set_value(self, name: str, value: Any) -> None:
        """Set the value of a parameter."""
        if name in self.parameters:
            self.parameters[name].set_value(value)

    def map_cc(self, cc_number: int, parameter_name: str) -> None:
        """Map a MIDI CC number to a parameter."""
        if parameter_name in self.parameters:
            self.cc_mappings[cc_number] = parameter_name
            self.parameters[parameter_name].midi_cc = cc_number

    def unmap_cc(self, cc_number: int) -> None:
        """Remove a MIDI CC mapping."""
        if cc_number in self.cc_mappings:
            param_name = self.cc_mappings[cc_number]
            self.parameters[param_name].midi_cc = None
            del self.cc_mappings[cc_number]

    def handle_cc(self, cc_number: int, value: int) -> None:
        """Handle incoming MIDI CC messages."""
        if cc_number in self.cc_mappings:
            param_name = self.cc_mappings[cc_number]
            param = self.parameters[param_name]
            normalized_value = value / 127.0
            
            # Scale the normalized value to the parameter's range
            if param.min_value is not None and param.max_value is not None:
                scaled_value = param.min_value + normalized_value * (param.max_value - param.min_value)
                self.set_value(param_name, scaled_value)

    def save_mappings(self, filename: str) -> None:
        """Save MIDI CC and LFO mappings to a file."""
        mappings = {
            'cc_mappings': self.cc_mappings,
            'lfo_mappings': self.lfo_mappings
        }
        with open(filename, 'w') as f:
            json.dump(mappings, f, indent=2)

    def load_mappings(self, filename: str) -> None:
        """Load MIDI CC and LFO mappings from a file."""
        try:
            with open(filename, 'r') as f:
                mappings = json.load(f)
                self.cc_mappings = mappings.get('cc_mappings', {})
                self.lfo_mappings = mappings.get('lfo_mappings', {})
        except FileNotFoundError:
            print(f"No mappings file found at {filename}")

    def get_parameters_by_category(self, category: str) -> Dict[str, Parameter]:
        """Get all parameters in a specific category."""
        return {name: param for name, param in self.parameters.items() 
                if param.category == category}

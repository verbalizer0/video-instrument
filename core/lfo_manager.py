# core/lfo_manager.py

import math
import random
from enum import Enum
from typing import Dict, Optional, Callable

class WaveformType(Enum):
    SINE = "sine"
    TRIANGLE = "triangle"
    SQUARE = "square"
    SAW = "saw"
    RANDOM = "random"

class LFO:
    """
    Low Frequency Oscillator for parameter modulation.
    """
    def __init__(self, wave_type: WaveformType = WaveformType.SINE):
        self.wave_type = wave_type
        self.frequency = 1.0  # Cycles per beat
        self.amplitude = 1.0
        self.phase = 0.0
        self.offset = 0.0  # Center point offset (-1 to 1)
        self.active = True
        self.sync_to_bpm = True
        self._last_random = 0.0  # For random waveform
        self._last_phase = 0.0

    def _sine(self, phase: float) -> float:
        return math.sin(2 * math.pi * phase)

    def _triangle(self, phase: float) -> float:
        phase = phase % 1.0
        if phase < 0.25:
            return 4 * phase
        elif phase < 0.75:
            return 2 - 4 * phase
        else:
            return -4 + 4 * phase

    def _square(self, phase: float) -> float:
        return 1.0 if (phase % 1.0) < 0.5 else -1.0

    def _saw(self, phase: float) -> float:
        phase = phase % 1.0
        return 2.0 * phase - 1.0

    def _random(self, phase: float) -> float:
        phase = phase % 1.0
        if phase < self._last_phase:
            self._last_random = random.uniform(-1, 1)
        self._last_phase = phase
        return self._last_random

    def get_value(self, beat_position: float) -> float:
        """Calculate the current LFO value based on beat position."""
        if not self.active:
            return 0.0

        phase = (beat_position * self.frequency + self.phase) % 1.0
        
        wave_functions = {
            WaveformType.SINE: self._sine,
            WaveformType.TRIANGLE: self._triangle,
            WaveformType.SQUARE: self._square,
            WaveformType.SAW: self._saw,
            WaveformType.RANDOM: self._random
        }
        
        base_value = wave_functions[self.wave_type](phase)
        return (base_value * self.amplitude + self.offset)

class LFOManager:
    """
    Manages multiple LFOs and their parameter assignments.
    """
    def __init__(self, parameter_manager):
        self.parameter_manager = parameter_manager
        self.lfos: Dict[int, LFO] = {}
        self.assignments: Dict[int, str] = {}  # LFO ID -> parameter name
        self.beat_position = 0.0
        self._next_id = 0

    def create_lfo(self, wave_type: WaveformType = WaveformType.SINE) -> int:
        """Create a new LFO and return its ID."""
        lfo_id = self._next_id
        self.lfos[lfo_id] = LFO(wave_type)
        self._next_id += 1
        return lfo_id

    def assign_lfo(self, lfo_id: int, parameter_name: str) -> None:
        """Assign an LFO to modulate a parameter."""
        if lfo_id in self.lfos and parameter_name in self.parameter_manager.parameters:
            self.assignments[lfo_id] = parameter_name
            param = self.parameter_manager.parameters[parameter_name]
            param.lfo_id = lfo_id

    def unassign_lfo(self, lfo_id: int) -> None:
        """Remove LFO assignment from a parameter."""
        if lfo_id in self.assignments:
            param_name = self.assignments[lfo_id]
            self.parameter_manager.parameters[param_name].lfo_id = None
            del self.assignments[lfo_id]

    def update(self, beat_position: float) -> None:
        """Update all active LFOs and their assigned parameters."""
        self.beat_position = beat_position
        
        for lfo_id, param_name in self.assignments.items():
            lfo = self.lfos[lfo_id]
            if not lfo.active:
                continue

            param = self.parameter_manager.parameters[param_name]
            if param.min_value is not None and param.max_value is not None:
                # Scale LFO output to parameter range
                lfo_value = lfo.get_value(beat_position)
                param_range = param.max_value - param.min_value
                center = param.min_value + param_range / 2
                scaled_value = center + (lfo_value * param_range / 2)
                self.parameter_manager.set_value(param_name, scaled_value)

    def configure_lfo(self, lfo_id: int, **kwargs) -> None:
        """Configure LFO parameters."""
        if lfo_id not in self.lfos:
            return

        lfo = self.lfos[lfo_id]
        if 'wave_type' in kwargs:
            lfo.wave_type = WaveformType(kwargs['wave_type'])
        if 'frequency' in kwargs:
            lfo.frequency = kwargs['frequency']
        if 'amplitude' in kwargs:
            lfo.amplitude = kwargs['amplitude']
        if 'phase' in kwargs:
            lfo.phase = kwargs['phase']
        if 'offset' in kwargs:
            lfo.offset = kwargs['offset']
        if 'active' in kwargs:
            lfo.active = kwargs['active']

    def save_state(self) -> dict:
        """Save current LFO configurations and assignments."""
        state = {
            'lfos': {},
            'assignments': self.assignments.copy()
        }
        for lfo_id, lfo in self.lfos.items():
            state['lfos'][lfo_id] = {
                'wave_type': lfo.wave_type.value,
                'frequency': lfo.frequency,
                'amplitude': lfo.amplitude,
                'phase': lfo.phase,
                'offset': lfo.offset,
                'active': lfo.active
            }
        return state

    def load_state(self, state: dict) -> None:
        """Load LFO configurations and assignments."""
        self.lfos.clear()
        self.assignments.clear()
        
        for lfo_id, lfo_state in state['lfos'].items():
            lfo = LFO(WaveformType(lfo_state['wave_type']))
            lfo.frequency = lfo_state['frequency']
            lfo.amplitude = lfo_state['amplitude']
            lfo.phase = lfo_state['phase']
            lfo.offset = lfo_state['offset']
            lfo.active = lfo_state['active']
            self.lfos[int(lfo_id)] = lfo

        self.assignments.update(state['assignments'])
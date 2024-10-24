import time
import random
from collections import deque
from threading import Lock

class MIDIEmulator:
    """
    MIDI emulator for testing without hardware MIDI devices.
    Simulates MIDI clock, notes, and CC messages.
    """
    def __init__(self):
        self.messages = deque()
        self.lock = Lock()
        self.last_clock = time.time()
        self.clock_interval = 60.0 / (120 * 24)  # 120 BPM, 24 PPQN
        
    def get_midi_messages(self):
        """Get all pending MIDI messages."""
        with self.lock:
            # Add clock messages based on time
            current_time = time.time()
            while current_time - self.last_clock >= self.clock_interval:
                self.messages.append(([0xF8], 0))  # MIDI clock message
                self.last_clock += self.clock_interval
            
            # Return all pending messages
            messages = list(self.messages)
            self.messages.clear()
            return messages
            
    def trigger_random_note(self):
        """Generate a random MIDI note message."""
        with self.lock:
            note = random.randint(36, 96)  # Random note between C2 and C7
            velocity = random.randint(64, 127)  # Random velocity (medium to high)
            self.messages.append(([0x90, note, velocity], 0))  # Note On
            
    def send_cc(self, cc_num, value):
        """Send a MIDI CC message."""
        with self.lock:
            self.messages.append(([0xB0, cc_num, value], 0))
            
    def change_program(self, program):
        """Send a program change message."""
        with self.lock:
            self.messages.append(([0xC0, program], 0))

def init():
    """Initialize and return a MIDI emulator instance."""
    return MIDIEmulator()
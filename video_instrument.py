# video_instrument.py

import os
import sys
import pygame
import rtmidi
import importlib
from typing import Dict, Optional, List

from core.systems import CoreSystems
from core.config import *
from visuals.sprites.sprite_manager import SpriteManager
from visuals.effects.trail_manager import TrailManager
from visuals.backgrounds.original_modes import BackgroundManagerExtended
import midi_emulator

class VideoInstrument:
    """
    Main application class for the video instrument.
    Handles initialization, user input, and system coordination.
    """
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Initialize core systems
        self.core_systems = CoreSystems()
        
        # Initialize sprite system
        self.sprite_manager = SpriteManager()
        self._load_sprites()
        
        # Initialize MIDI
        self.midi_in = rtmidi.MidiIn()
        ports = self.midi_in.get_ports()
        if ports:
            self.midi_in.open_port(0)
            self.use_midi_emulator = False
            print("Using hardware MIDI input")
        else:
            self.use_midi_emulator = True
            self.midi_emulator_instance = midi_emulator.init()
            print("Using MIDI emulator")

        # MIDI timing
        self.ppq = MIDI_PPQ
        self.clock_counter = 0
        self.beat_counter = 0
        self.last_beat_time = pygame.time.get_ticks()
        self.beat_duration = 60.0 / DEFAULT_BPM
        
        # Pattern management
        self.current_script = None
        self.script_modules: Dict[str, Any] = {}
        self.bpm_ratio_power = 0  # For background color cycling
        
        # Performance monitoring
        self.frame_count = 0
        self.last_time = pygame.time.get_ticks()
        self.fps = 0
        
        # Create font for debug info
        self.debug_font = pygame.font.Font(None, UI_FONT_SIZE)
        self.show_debug = False
        
        # State flags
        self.running = True
        self.paused = False

    def _load_sprites(self):
        """Load all sprite resources."""
        # Ensure resource directories exist
        os.makedirs(SPRITE_PATH, exist_ok=True)
        os.makedirs(GIF_PATH, exist_ok=True)
        os.makedirs(SEQUENCE_PATH, exist_ok=True)

        # Load GIFs
        self.sprite_manager.load_gifs_from_directory(GIF_PATH)
        
        # Load sprite sequences
        if os.path.exists(SEQUENCE_PATH):
            for sequence_folder in os.listdir(SEQUENCE_PATH):
                folder_path = os.path.join(SEQUENCE_PATH, sequence_folder)
                if os.path.isdir(folder_path):
                    self.sprite_manager.load_sprite_sequence(
                        sequence_folder, folder_path
                    )

    def load_scripts(self):
        """Load all pattern scripts."""
        patterns_dir = os.path.join(os.path.dirname(__file__), 'patterns')
        script_files = [f for f in os.listdir(patterns_dir)
                       if f.startswith(PATTERN_PREFIX) and f.endswith('.py')]
        
        for script in script_files:
            module_name = f"patterns.{script[:-3]}"  # Convert filename to module path
            try:
                self.script_modules[script[:-3]] = importlib.import_module(module_name)
                print(f"Loaded pattern: {script[:-3]}")
            except Exception as e:
                print(f"Error loading pattern {script[:-3]}: {e}")

        print(f"\nLoaded {len(self.script_modules)} pattern scripts")

    def switch_script(self, script_name: str):
        """Switch to a different pattern."""
        if script_name in self.script_modules:
            if self.current_script:
                self.current_script.cleanup()
            try:
                self.current_script = self.script_modules[script_name].PatternGenerator(
                    self.screen,
                    self.core_systems,
                    self.sprite_manager
                )
                print(f"Switched to pattern: {script_name}")
                
                # List available patterns
                pattern_list = sorted(self.script_modules.keys())
                current_index = pattern_list.index(script_name)
                print("\nAvailable patterns:")
                for i, name in enumerate(pattern_list):
                    prefix = ">" if i == current_index else " "
                    print(f"{prefix} {i}: {name}")
                print()
                
            except Exception as e:
                print(f"Error initializing pattern {script_name}: {e}")
        else:
            print(f"Pattern not found: {script_name}")

    def handle_midi_message(self, message):
        """Handle incoming MIDI messages."""
        message, delta_time = message

        if message[0] == 0xF8:  # MIDI Clock
            self.clock_counter += 1
            if self.clock_counter >= self.ppq:
                self.clock_counter = 0
                self.beat_counter += 1
                current_time = pygame.time.get_ticks()
                self.beat_duration = (current_time - self.last_beat_time) / 1000.0
                self.last_beat_time = current_time
                
                if self.beat_duration > 0:
                    bpm = 60.0 / self.beat_duration
                    self.core_systems.parameter_manager.set_value('bpm', int(bpm))
                
        elif message[0] == 0x90:  # Note On
            note, velocity = message[1], message[2]
            print(f"Note On: note={note}, velocity={velocity}")
            if self.current_script:
                self.current_script.handle_note(note, velocity)
                
        elif message[0] == 0xB0:  # Control Change
            cc_number, cc_value = message[1], message[2]
            print(f"Control Change: cc={cc_number}, value={cc_value}")
            if self.current_script:
                self.current_script.handle_cc(cc_number, cc_value)
                
        elif message[0] == 0xC0:  # Program Change
            program = message[1]
            print(f"Program Change: program={program}")
            script_name = f"{PATTERN_PREFIX}{program:02d}"
            if script_name in self.script_modules:
                self.switch_script(script_name)

    def handle_keyboard_input(self, event):
        """Handle keyboard input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return
                
            elif event.key == pygame.K_SPACE and self.use_midi_emulator:
                self.midi_emulator_instance.trigger_random_note()
                
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                # Switch pattern using number keys (1-9)
                pattern_num = event.key - pygame.K_1
                pattern_name = f"{PATTERN_PREFIX}{pattern_num:02d}"
                self.switch_script(pattern_name)
                
            elif event.key == pygame.K_0:
                # 0 key maps to pattern 09
                self.switch_script(f"{PATTERN_PREFIX}09")
                
            elif event.key == pygame.K_LEFTBRACKET:
                # Previous pattern
                if self.current_script:
                    current_num = int(self.current_script.__class__.__module__.split('_')[1])
                    next_num = (current_num - 1) % len(self.script_modules)
                    self.switch_script(f"{PATTERN_PREFIX}{next_num:02d}")
                    
            elif event.key == pygame.K_RIGHTBRACKET:
                # Next pattern
                if self.current_script:
                    current_num = int(self.current_script.__class__.__module__.split('_')[1])
                    next_num = (current_num + 1) % len(self.script_modules)
                    self.switch_script(f"{PATTERN_PREFIX}{next_num:02d}")
                    
            elif event.key == pygame.K_b and self.current_script:
                self.current_script.toggle_black_and_white_mode()
                
            elif event.key == pygame.K_n and self.current_script:
                self.current_script.change_background_color()
                
            elif event.key == pygame.K_m and self.current_script:
                self.current_script.cycle_shape_mode()
                
            elif event.key == pygame.K_t and self.current_script:
                self.current_script.trail_manager.toggle_ui()
                
            elif event.key == pygame.K_d:
                self.show_debug = not self.show_debug
                
            elif event.key == pygame.K_p:
                self.paused = not self.paused
                print(f"{'Paused' if self.paused else 'Resumed'}")
                
            # Background color cycle ratio controls
            elif event.key == pygame.K_COMMA and self.current_script:
                self.bpm_ratio_power = min(self.bpm_ratio_power + 1, 10)
                self.current_script.set_background_cycle_ratio(1 / (2 ** self.bpm_ratio_power))
                print(f"Background color cycle ratio set to 1:{2 ** self.bpm_ratio_power}")
                
            elif event.key == pygame.K_PERIOD and self.current_script:
                self.bpm_ratio_power = max(self.bpm_ratio_power - 1, -10)
                self.current_script.set_background_cycle_ratio(1 / (2 ** self.bpm_ratio_power))
                print(f"Background color cycle ratio set to 1:{2 ** self.bpm_ratio_power}")

            # Pass keyboard event to core systems
            self.core_systems.handle_key(event)

    def handle_continuous_input(self):
        """Handle continuous input (held keys)."""
        keys = pygame.key.get_pressed()
        
        if self.current_script:
            # Handle CC3 with up/down arrows
            if keys[pygame.K_UP]:
                self.current_script.handle_cc(3, min(127, int(
                    self.core_systems.parameter_manager.get_value('activation_spread') * 127 + 1)))
            elif keys[pygame.K_DOWN]:
                self.current_script.handle_cc(3, max(0, int(
                    self.core_systems.parameter_manager.get_value('activation_spread') * 127 - 1)))
                    
            # Handle CC4 with left/right arrows
            if keys[pygame.K_RIGHT]:
                self.current_script.handle_cc(4, min(127, int(
                    (self.core_systems.parameter_manager.get_value('decay_rate') - 0.99) / 0.009 * 127 + 1)))
            elif keys[pygame.K_LEFT]:
                self.current_script.handle_cc(4, max(0, int(
                    (self.core_systems.parameter_manager.get_value('decay_rate') - 0.99) / 0.009 * 127 - 1)))

    def draw_debug_info(self):
        """Draw debug information."""
        if not self.show_debug:
            return
            
        debug_info = [
            f"FPS: {self.fps:.1f}",
            f"BPM: {self.core_systems.parameter_manager.get_value('bpm')}",
            f"Beat: {self.beat_counter}",
            f"Pattern: {self.current_script.__class__.__name__ if self.current_script else 'None'}",
            f"Sprites loaded: {len(self.sprite_manager.sprites)}",
        ]
        
        y = 10
        for info in debug_info:
            surface = self.debug_font.render(info, True, UI_COLORS['text'])
            self.screen.blit(surface, (10, y))
            y += 20

    def update(self):
        """Update game state."""
        if self.paused:
            return
            
        # Update current pattern
        if self.current_script:
            self.current_script.update()
        
        # Update core systems
        self.core_systems.update(self.beat_counter + self.clock_counter / self.ppq)
        
        # Update FPS
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time > 1000:
            self.fps = self.frame_count * 1000 / (current_time - self.last_time)
            self.frame_count = 0
            self.last_time = current_time

    def draw(self):
        """Draw the current frame."""
        # Draw current pattern
        if self.current_script:
            self.current_script.draw()
        
        # Draw UI elements
        self.core_systems.draw_ui(self.screen)
        self.draw_debug_info()
        
        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keyboard_input(event)
                elif event.type == pygame.VIDEORESIZE:
                    if self.current_script:
                        self.current_script.resize(event.w, event.h)

            # Handle continuous input
            self.handle_continuous_input()

            # Handle MIDI input
            if self.use_midi_emulator:
                messages = self.midi_emulator_instance.get_midi_messages()
                for message in messages:
                    self.handle_midi_message(message)
            else:
                message = self.midi_in.get_message()
                while message:
                    self.handle_midi_message(message)
                    message = self.midi_in.get_message()

            # Update and draw
            self.update()
            self.draw()
            
            # Maintain frame rate
            clock.tick(FPS)
            self.frame_count += 1

        # Cleanup
        self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.current_script:
            self.current_script.cleanup()
        self.core_systems.cleanup()
        pygame.quit()
        if not self.use_midi_emulator:
            self.midi_in.close_port()

if __name__ == "__main__":
    app = VideoInstrument()
    try:
        app.load_scripts()
        app.switch_script(DEFAULT_PATTERN)
        print("Starting Video Instrument...")
        app.run()
    except Exception as e:
        print(f"Error running Video Instrument: {e}")
    finally:
        print("Video Instrument closed")
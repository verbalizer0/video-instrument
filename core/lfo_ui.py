# core/lfo_ui.py

import pygame
from typing import Dict, Tuple, Optional
from .lfo_manager import LFOManager, WaveformType

class LFOControlUI:
    """
    User interface for controlling LFOs.
    """
    def __init__(self, lfo_manager: LFOManager):
        self.lfo_manager = lfo_manager
        self.font = pygame.font.Font(None, 24)
        self.active_lfo: Optional[int] = None
        self.visible = False
        self.position = (10, 10)
        self.spacing = 25
        self.colors = {
            'text': (255, 255, 255),
            'highlight': (255, 255, 0),
            'background': (0, 0, 0, 128)
        }

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the LFO control interface."""
        if not self.visible:
            return

        x, y = self.position
        current_y = y

        # Draw semi-transparent background
        panel_height = len(self.lfo_manager.lfos) * self.spacing + 40
        panel_width = 300
        background = pygame.Surface((panel_width, panel_height))
        background.fill(self.colors['background'][:3])
        background.set_alpha(self.colors['background'][3])
        surface.blit(background, (x-5, y-5))

        # Draw title
        title = "LFO Control (TAB to hide)"
        title_surface = self.font.render(title, True, self.colors['text'])
        surface.blit(title_surface, (x, current_y))
        current_y += self.spacing * 1.5

        # Draw LFO list
        for lfo_id, lfo in self.lfo_manager.lfos.items():
            color = self.colors['highlight'] if lfo_id == self.active_lfo else self.colors['text']
            
            # Build LFO info string
            text = f"LFO {lfo_id}: {lfo.wave_type.value} ({lfo.frequency:.1f}Hz)"
            if lfo_id in self.lfo_manager.assignments:
                text += f" -> {self.lfo_manager.assignments[lfo_id]}"
            if not lfo.active:
                text += " [DISABLED]"
            
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (x, current_y))
            current_y += self.spacing

    def handle_key(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for LFO control."""
        if event.key == pygame.K_TAB:
            self.visible = not self.visible
        elif not self.visible:
            return

        if event.key == pygame.K_UP:
            self._select_prev_lfo()
        elif event.key == pygame.K_DOWN:
            self._select_next_lfo()
        elif event.key == pygame.K_w:
            self._cycle_waveform()
        elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            self._adjust_frequency(event.key == pygame.K_RIGHT)
        elif event.key == pygame.K_SPACE:
            self._toggle_active()
        elif event.key == pygame.K_DELETE:
            self._delete_current_lfo()

    def _select_prev_lfo(self) -> None:
        """Select the previous LFO in the list."""
        if not self.lfo_manager.lfos:
            return
        if self.active_lfo is None:
            self.active_lfo = max(self.lfo_manager.lfos.keys())
        else:
            lfo_ids = sorted(self.lfo_manager.lfos.keys())
            idx = lfo_ids.index(self.active_lfo)
            self.active_lfo = lfo_ids[idx - 1]

    def _select_next_lfo(self) -> None:
        """Select the next LFO in the list."""
        if not self.lfo_manager.lfos:
            return
        if self.active_lfo is None:
            self.active_lfo = min(self.lfo_manager.lfos.keys())
        else:
            lfo_ids = sorted(self.lfo_manager.lfos.keys())
            idx = (lfo_ids.index(self.active_lfo) + 1) % len(lfo_ids)
            self.active_lfo = lfo_ids[idx]

    def _cycle_waveform(self) -> None:
        """Cycle through available waveform types for the selected LFO."""
        if self.active_lfo is None:
            return
        lfo = self.lfo_manager.lfos[self.active_lfo]
        wave_types = list(WaveformType)
        current_idx = wave_types.index(lfo.wave_type)
        next_idx = (current_idx + 1) % len(wave_types)
        lfo.wave_type = wave_types[next_idx]

    def _adjust_frequency(self, increase: bool) -> None:
        """Adjust the frequency of the selected LFO."""
        if self.active_lfo is None:
            return
        lfo = self.lfo_manager.lfos[self.active_lfo]
        if increase:
            lfo.frequency *= 1.1
        else:
            lfo.frequency /= 1.1

    def _toggle_active(self) -> None:
        """Toggle the active state of the selected LFO."""
        if self.active_lfo is None:
            return
        lfo = self.lfo_manager.lfos[self.active_lfo]
        lfo.active = not lfo.active

    def _delete_current_lfo(self) -> None:
        """Delete the currently selected LFO."""
        if self.active_lfo is None:
            return
        if self.active_lfo in self.lfo_manager.assignments:
            self.lfo_manager.unassign_lfo(self.active_lfo)
        del self.lfo_manager.lfos[self.active_lfo]
        self.active_lfo = None
"""
Custom Audio Device Selector Widget for Qtile
Displays current audio output device and launches pavucontrol on click
"""

import subprocess
from libqtile.widget import base
from libqtile.log_utils import logger


class AudioDeviceSelector(base.InLoopPollText):
    """
    A widget that displays the current audio output device
    and launches pavucontrol when clicked.

    Left click: Launch pavucontrol
    """

    defaults = [
        ("update_interval", 2, "Update interval in seconds"),
        ("format", "🔊 {device}", "Display format. {device} shows device name"),
        ("max_chars", 25, "Maximum characters to display for device name"),
        ("audio_control_cmd", "pavucontrol", "Command to launch audio control app"),
    ]

    def __init__(self, **config):
        base.InLoopPollText.__init__(self, **config)
        self.add_defaults(AudioDeviceSelector.defaults)

    def poll(self):
        """Poll current audio device"""
        try:
            device_name = self._get_current_sink_name()
            if not device_name:
                return "🔊 No device"

            # Shorten device name if too long
            if len(device_name) > self.max_chars:
                device_name = device_name[:self.max_chars-3] + "..."

            return self.format.format(device=device_name)
        except Exception as e:
            logger.exception(f"AudioDeviceSelector error: {e}")
            return "🔊 Error"

    def _get_current_sink_name(self):
        """Get the name of the current default sink"""
        try:
            # Get default sink
            result = subprocess.run(
                ["pactl", "get-default-sink"],
                capture_output=True,
                text=True,
                timeout=1
            )

            if result.returncode != 0:
                return None

            self.current_sink = result.stdout.strip()

            # Get sink description
            result = subprocess.run(
                ["pactl", "list", "sinks"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0:
                return self.current_sink

            # Parse output to find the description of current sink
            lines = result.stdout.split('\n')
            current_sink_section = False

            for i, line in enumerate(lines):
                if "Name:" in line and self.current_sink in line:
                    current_sink_section = True
                elif current_sink_section and "Description:" in line:
                    description = line.split("Description:", 1)[1].strip()
                    return description
                elif current_sink_section and line.startswith("Sink #"):
                    # Moved to next sink, stop searching
                    break

            return self.current_sink

        except Exception as e:
            logger.exception(f"Error getting sink name: {e}")
            return None

    def button_press(self, x, y, button):
        """Handle mouse clicks - launch pavucontrol"""
        if button == 1:  # Left click
            try:
                subprocess.Popen(
                    [self.audio_control_cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                logger.exception(f"Failed to launch {self.audio_control_cmd}: {e}")

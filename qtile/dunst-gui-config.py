#!/home/sen10/.local/share/pipx/venvs/qtile/bin/python3
"""
Dunst GUI Configurator - Simple color and transparency editor
Uses DearPyGUI 2.0.0 for Catppuccin Mocha themed dunst notifications
"""

import dearpygui.dearpygui as dpg
import re
import os
import subprocess
from pathlib import Path

DUNSTRC_PATH = Path.home() / ".config" / "dunst" / "dunstrc"

class DunstConfig:
    """Simple parser and writer for dunst config (colors and transparency only)"""

    def __init__(self):
        self.config_lines = []
        self.settings = {
            'urgency_low': {
                'background': '#1e1e2e',
                'foreground': '#cdd6f4',
                'frame_color': '#89b4fa',
            },
            'urgency_normal': {
                'background': '#1e1e2e',
                'foreground': '#cdd6f4',
                'frame_color': '#fab387',
            },
            'urgency_critical': {
                'background': '#1e1e2e',
                'foreground': '#cdd6f4',
                'frame_color': '#f38ba8',
            }
        }

    def load(self):
        """Load dunstrc configuration"""
        if not DUNSTRC_PATH.exists():
            return

        with open(DUNSTRC_PATH, 'r') as f:
            self.config_lines = f.readlines()

        # Parse color settings
        current_section = None
        for line in self.config_lines:
            # Check for section headers
            section_match = re.match(r'^\[urgency_(low|normal|critical)\]', line)
            if section_match:
                current_section = f'urgency_{section_match.group(1)}'
                continue

            # Parse color settings
            if current_section and current_section in self.settings:
                for key in ['background', 'foreground', 'frame_color']:
                    match = re.match(rf'^\s*{key}\s*=\s*"?([#\w]+)"?', line)
                    if match:
                        self.settings[current_section][key] = match.group(1)

    def save(self):
        """Save dunstrc configuration"""
        # Update config lines with new values
        current_section = None
        new_lines = []

        for line in self.config_lines:
            # Check for section headers
            section_match = re.match(r'^\[urgency_(low|normal|critical)\]', line)
            if section_match:
                current_section = f'urgency_{section_match.group(1)}'
                new_lines.append(line)
                continue

            # Update color settings
            if current_section and current_section in self.settings:
                updated = False
                for key in ['background', 'foreground', 'frame_color']:
                    match = re.match(rf'^(\s*{key}\s*=\s*)"?[#\w]+"?(.*)$', line)
                    if match:
                        new_value = self.settings[current_section][key]
                        new_lines.append(f'{match.group(1)}"{new_value}"{match.group(2)}\n')
                        updated = True
                        break
                if not updated:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Write back to file
        with open(DUNSTRC_PATH, 'w') as f:
            f.writelines(new_lines)

    def restart_dunst(self):
        """Restart dunst to apply changes"""
        subprocess.run(['killall', 'dunst'], stderr=subprocess.DEVNULL)
        subprocess.Popen(['dunst'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class DunstGUI:
    """DearPyGUI interface for dunst configuration"""

    def __init__(self):
        self.config = DunstConfig()
        self.config.load()

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
            return (r, g, b, 1.0)
        return (1.0, 1.0, 1.0, 1.0)

    def rgb_to_hex(self, rgb):
        """Convert RGB tuple (0-1 range) to hex color"""
        r, g, b = [int(c * 255) for c in rgb[:3]]
        return f'#{r:02x}{g:02x}{b:02x}'

    def get_alpha_from_hex(self, hex_color):
        """Extract alpha from hex color (simulated from color darkness)"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            # Use perceived brightness as proxy for transparency
            brightness = (r + g + b) / 3
            return brightness / 255.0
        return 1.0

    def update_color(self, sender, app_data, user_data):
        """Callback when color is changed"""
        urgency, color_type = user_data
        color = app_data
        hex_color = self.rgb_to_hex(color)
        self.config.settings[urgency][color_type] = hex_color

        # Update preview
        self.update_preview(urgency)

    def update_preview(self, urgency):
        """Update the preview box for a specific urgency level"""
        settings = self.config.settings[urgency]

        # Convert hex to rgba tuples (0-255 range)
        bg_rgb = [int(settings['background'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
        fg_rgb = [int(settings['foreground'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
        frame_rgb = [int(settings['frame_color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]

        # Update preview rectangle
        rect_tag = f"preview_rect_{urgency}"
        if dpg.does_item_exist(rect_tag):
            dpg.configure_item(rect_tag,
                fill=(*bg_rgb, 255),
                color=(*frame_rgb, 255)
            )

        # Update text colors
        title_tag = f"preview_title_{urgency}"
        body_tag = f"preview_body_{urgency}"

        fg_color = (*fg_rgb, 255)
        if dpg.does_item_exist(title_tag):
            dpg.configure_item(title_tag, color=fg_color)
        if dpg.does_item_exist(body_tag):
            dpg.configure_item(body_tag, color=fg_color)

    def send_preview(self, sender, app_data, user_data):
        """Send a test notification"""
        urgency = user_data
        urgency_flag = {
            'urgency_low': 'low',
            'urgency_normal': 'normal',
            'urgency_critical': 'critical'
        }[urgency]

        titles = {
            'urgency_low': '低優先度通知',
            'urgency_normal': '通常通知',
            'urgency_critical': '重要通知'
        }

        subprocess.run([
            'notify-send',
            titles[urgency],
            f'これは{titles[urgency]}のプレビューです',
            '-u', urgency_flag
        ])

    def save_and_restart(self):
        """Save configuration and restart dunst"""
        self.config.save()
        self.config.restart_dunst()

        # Show confirmation notification
        subprocess.run([
            'notify-send',
            '設定を保存しました',
            'Dunstが再起動されました',
            '-u', 'normal'
        ])

    def create_urgency_section(self, urgency, title):
        """Create a collapsing header for each urgency level"""
        settings = self.config.settings[urgency]

        with dpg.collapsing_header(label=title, default_open=True):
            # Color pickers in horizontal layout
            with dpg.group(horizontal=True):
                # Background color
                with dpg.group():
                    dpg.add_text("背景色:")
                    dpg.add_color_picker(
                        default_value=self.hex_to_rgb(settings['background']),
                        no_alpha=False,
                        width=200,
                        callback=self.update_color,
                        user_data=(urgency, 'background')
                    )

                dpg.add_spacer(width=10)

                # Foreground color
                with dpg.group():
                    dpg.add_text("文字色:")
                    dpg.add_color_picker(
                        default_value=self.hex_to_rgb(settings['foreground']),
                        no_alpha=False,
                        width=200,
                        callback=self.update_color,
                        user_data=(urgency, 'foreground')
                    )

                dpg.add_spacer(width=10)

                # Frame color
                with dpg.group():
                    dpg.add_text("枠線色:")
                    dpg.add_color_picker(
                        default_value=self.hex_to_rgb(settings['frame_color']),
                        no_alpha=False,
                        width=200,
                        callback=self.update_color,
                        user_data=(urgency, 'frame_color')
                    )

            dpg.add_spacer(height=15)

            # Preview section
            dpg.add_text("プレビュー:")
            with dpg.drawlist(width=950, height=100, tag=f"preview_drawlist_{urgency}"):
                # Draw background rectangle
                bg_rgb = [int(settings['background'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
                frame_rgb = [int(settings['frame_color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]

                dpg.draw_rectangle(
                    (5, 5), (945, 95),
                    fill=(*bg_rgb, 255),
                    color=(*frame_rgb, 255),
                    thickness=2,
                    rounding=10,
                    tag=f"preview_rect_{urgency}"
                )

            # Text overlay on preview (positioned absolutely)
            with dpg.group(tag=f"preview_{urgency}"):
                dpg.add_text(
                    "通知タイトル",
                    tag=f"preview_title_{urgency}",
                    color=self.hex_to_rgb(settings['foreground'])
                )
                dpg.add_text(
                    "これは通知の本文テキストです。カラーがリアルタイムで反映されます。",
                    tag=f"preview_body_{urgency}",
                    color=self.hex_to_rgb(settings['foreground']),
                    wrap=900
                )

            dpg.add_spacer(height=10)

            # Preview button (for external notification)
            dpg.add_button(
                label=f"システム通知でプレビュー",
                callback=self.send_preview,
                user_data=urgency,
                width=250
            )
            dpg.add_spacer(height=20)

    def run(self):
        """Create and run the GUI"""
        dpg.create_context()

        # Theme setup - Catppuccin Mocha inspired
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 46, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (24, 24, 37, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (17, 17, 27, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (49, 50, 68, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (88, 91, 112, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (108, 112, 134, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (127, 132, 156, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (49, 50, 68, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (69, 71, 90, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (88, 91, 112, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (205, 214, 244, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (69, 71, 90, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (88, 91, 112, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (108, 112, 134, 255))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)

        dpg.bind_theme(global_theme)

        # Setup Japanese font
        with dpg.font_registry():
            # Load Noto Sans CJK JP font with Japanese glyphs
            with dpg.font("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 16) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.bind_font(default_font)

        # Main window
        with dpg.window(label="Dunst通知設定", tag="main_window", width=1000, height=800):
            dpg.add_text("Dunst通知のカラーテーマ設定", color=(180, 190, 254))
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Create sections for each urgency level
            self.create_urgency_section('urgency_low', '低優先度通知')
            self.create_urgency_section('urgency_normal', '通常通知')
            self.create_urgency_section('urgency_critical', '重要通知')

            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Save button
            dpg.add_button(
                label="保存してDunstを再起動",
                callback=lambda: self.save_and_restart(),
                width=300,
                height=40
            )

        # Setup and show
        dpg.create_viewport(
            title="Dunst GUI Configurator",
            width=1020,
            height=850
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()


if __name__ == "__main__":
    app = DunstGUI()
    app.run()

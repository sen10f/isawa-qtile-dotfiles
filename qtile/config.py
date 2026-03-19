"""
Qtile Configuration - Modular Setup
Main configuration file that imports settings from the settings/ directory
"""

import json
from pathlib import Path

from libqtile import qtile
from libqtile.config import Click, Drag, Match
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

# Import modular settings
from settings.colors import colors

_theme_cfg = json.loads((Path(__file__).parent / "theme.json").read_text())
from settings.groups import init_groups
from settings.keys import init_keys
from settings.layouts import init_layouts
from settings.widgets import init_widgets, create_bar
from settings.screens import init_screens
from settings.hooks import setup_environment, init_hooks

# Setup environment variables for dark theme
setup_environment()

# Define mod key and terminal
mod = "mod4"
terminal = _theme_cfg.get("apps", {}).get("terminal") or guess_terminal()

# Initialize groups and workspace management
groups, go_to_group = init_groups(terminal)

# Initialize keyboard shortcuts
keys = init_keys(mod, terminal, go_to_group, groups)

# Initialize layouts
layouts, floating_layout = init_layouts(colors)

# Initialize widget defaults
widget_defaults = init_widgets(colors)
extension_defaults = widget_defaults.copy()

# Initialize screens (pass go_to_group so GroupBox uses it)
screens = init_screens(colors, create_bar, go_to_group)

# Mouse bindings
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

# Qtile configuration variables
dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus          = _theme_cfg.get("follow_mouse_focus",          True)
bring_front_click           = _theme_cfg.get("bring_front_click",           False)
floats_kept_above           = _theme_cfg.get("floats_kept_above",           True)
cursor_warp                 = _theme_cfg.get("cursor_warp",                 False)
auto_fullscreen             = _theme_cfg.get("auto_fullscreen",             True)
focus_on_window_activation  = "smart"
focus_previous_on_window_remove = False
reconfigure_screens         = True
auto_minimize               = _theme_cfg.get("auto_minimize",               True)

# Wayland backend configuration
wl_input_rules = None
wl_xcursor_theme = None
wl_xcursor_size = 24

# Java UI compatibility
wmname = "LG3D"

# Initialize hooks and autostart
init_hooks()

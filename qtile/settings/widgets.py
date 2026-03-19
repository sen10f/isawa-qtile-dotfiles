"""
Bar and widgets configuration
"""

import json
import subprocess
from pathlib import Path
from libqtile import bar, widget
from settings.audio_device import AudioDeviceSelector

_theme = json.loads((Path(__file__).parent.parent / "theme.json").read_text())
_bar_cfg = _theme["bar"]
_wc     = _theme.get("widget_colors", {})


def init_widgets(colors):
    """Initialize widgets for the bar"""
    widget_defaults = dict(
        font="sans",
        fontsize=_bar_cfg["fontsize"],
        padding=_bar_cfg["padding"],
        background=colors["base"],
        foreground=colors["text"],
    )

    return widget_defaults


def create_bar(colors, primary=True, go_to_group_func=None):
    """Create a bar with widgets"""

    # Create GroupBox configuration
    groupbox_config = {
        "active":                      colors[_wc.get("group_active",               "text")],
        "inactive":                    colors[_wc.get("group_inactive",             "surface1")],
        "highlight_method":            "line",
        "highlight_color":             colors[_wc.get("group_highlight_bg",         "base")],
        "this_current_screen_border":  colors[_wc.get("group_this_screen",          "mauve")],
        "this_screen_border":          colors[_wc.get("group_other_screen",         "blue")],
        "other_current_screen_border": colors[_wc.get("group_other_current_screen", "pink")],
        "other_screen_border":         colors[_wc.get("group_other_screen_border",  "surface2")],
        "urgent_alert_method":         "line",
        "urgent_border":               colors[_wc.get("group_urgent",               "red")],
        "disable_drag":                True,
        "padding":                     5,
    }

    # If custom go_to_group function provided, use it for clicks
    if go_to_group_func:
        from functools import partial
        # Override the default function with our custom one
        groupbox_config["func"] = lambda qtile, name: go_to_group_func(name)()

    try:
        import psutil  # noqa: F401
        psutil_available = True
    except ImportError:
        psutil_available = False

    widgets = [
        widget.CurrentLayout(
            foreground=colors[_wc.get("current_layout", "mauve")],
            padding=10,
        ),
        widget.GroupBox(**groupbox_config),
        widget.Prompt(
            foreground=colors[_wc.get("prompt", "green")],
            prompt="run: ",
        ),
        widget.WindowName(
            foreground=colors[_wc.get("window_name", "lavender")],
            max_chars=50,
        ),
        widget.Chord(
            chords_colors={
                "launch": (colors["red"], colors["text"]),
            },
            name_transform=lambda name: name.upper(),
        ),
        widget.Sep(
            linewidth=1,
            padding=10,
            foreground=colors[_wc.get("separator", "surface0")],
        ),
        widget.Mpris2(
            name="mpris",
            objname="org.mpris.MediaPlayer2.playerctld",
            display_metadata=["xesam:title", "xesam:artist"],
            scroll_chars=50,
            scroll_interval=0.5,
            scroll_wait_intervals=4,
            stop_pause_text="⏹ No media playing",
            foreground=colors[_wc.get("media", "peach")],
            padding=5,
        ),
    ]

    # System information widgets
    widgets.extend([
        widget.Sep(
            linewidth=1,
            padding=10,
            foreground=colors[_wc.get("separator", "surface0")],
        ),
        AudioDeviceSelector(
            foreground=colors[_wc.get("audio_device", "green")],
            update_interval=2,
            max_chars=25,
        ),
        widget.Sep(
            linewidth=1,
            padding=10,
            foreground=colors[_wc.get("separator", "surface0")],
        ),
        widget.Volume(
            foreground=colors[_wc.get("volume", "mauve")],
            fmt=" {}",
            padding=5,
        ),
    ])

    if psutil_available:
        widgets.insert(
            -1,
            widget.CPU(
                format=" {load_percent}%",
                foreground=colors[_wc.get("cpu", "green")],
                padding=5,
            ),
        )
    else:
        widgets.insert(
            -1,
            widget.TextBox(
                text=" install psutil for CPU",
                foreground=colors["overlay1"],
                padding=5,
            ),
        )

    # Only show systray on primary monitor
    if primary:
        widgets.append(widget.Systray(padding=10))

    widgets.extend([
        widget.Clock(
            format="%Y-%m-%d %a %I:%M %p",
            foreground=colors[_wc.get("clock", "blue")],
            padding=10,
        ),
        widget.TextBox(
            text="⏻",
            foreground=colors[_wc.get("power_button", "red")],
            fontsize=16,
            padding=10,
            mouse_callbacks={
                'Button1': lambda: subprocess.Popen(['/home/sen10/.config/qtile/power-menu.sh'])
            },
        ),
    ])

    return bar.Bar(
        widgets,
        _bar_cfg["height"],
        background=colors["base"],
        border_width=[0, 0, _bar_cfg["border_bottom"], 0],
        border_color=colors[_wc.get("bar_border", "mauve")],
    )

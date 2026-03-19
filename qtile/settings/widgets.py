"""
Bar and widgets configuration
"""

import subprocess
from libqtile import bar, widget
from settings.audio_device import AudioDeviceSelector


def init_widgets(colors):
    """Initialize widgets for the bar"""
    widget_defaults = dict(
        font="sans",
        fontsize=12,
        padding=3,
        background=colors["base"],
        foreground=colors["text"],
    )

    return widget_defaults


def create_bar(colors, primary=True, go_to_group_func=None):
    """Create a bar with widgets"""

    # Create GroupBox configuration
    groupbox_config = {
        "active": colors["text"],
        "inactive": colors["surface1"],
        "highlight_method": "line",
        "highlight_color": colors["base"],
        "this_current_screen_border": colors["mauve"],
        "this_screen_border": colors["blue"],
        "other_current_screen_border": colors["pink"],
        "other_screen_border": colors["surface2"],
        "urgent_alert_method": "line",
        "urgent_border": colors["red"],
        "disable_drag": True,
        "padding": 5,
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
            foreground=colors["mauve"],
            padding=10,
        ),
        widget.GroupBox(**groupbox_config),
        widget.Prompt(
            foreground=colors["green"],
            prompt="run: ",
        ),
        widget.WindowName(
            foreground=colors["lavender"],
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
            foreground=colors["surface0"],
        ),
        widget.Mpris2(
            name="mpris",
            objname="org.mpris.MediaPlayer2.playerctld",
            display_metadata=["xesam:title", "xesam:artist"],
            scroll_chars=50,
            scroll_interval=0.5,
            scroll_wait_intervals=4,
            stop_pause_text="⏹ No media playing",
            foreground=colors["peach"],
            padding=5,
        ),
    ]

    # System information widgets
    widgets.extend([
        widget.Sep(
            linewidth=1,
            padding=10,
            foreground=colors["surface0"],
        ),
        AudioDeviceSelector(
            foreground=colors["green"],
            update_interval=2,
            max_chars=25,
        ),
        widget.Sep(
            linewidth=1,
            padding=10,
            foreground=colors["surface0"],
        ),
        widget.Volume(
            foreground=colors["mauve"],
            fmt=" {}",
            padding=5,
        ),
    ])

    if psutil_available:
        widgets.insert(
            -1,
            widget.CPU(
                format=" {load_percent}%",
                foreground=colors["green"],
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
            foreground=colors["blue"],
            padding=10,
        ),
        widget.TextBox(
            text="⏻",
            foreground=colors["red"],
            fontsize=16,
            padding=10,
            mouse_callbacks={
                'Button1': lambda: subprocess.Popen(['/home/sen10/.config/qtile/power-menu.sh'])
            },
        ),
    ])

    return bar.Bar(
        widgets,
        28,
        background=colors["base"],
        border_width=[0, 0, 2, 0],
        border_color=colors["mauve"],
    )

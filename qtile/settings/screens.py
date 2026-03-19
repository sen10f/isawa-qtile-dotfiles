"""
Screens configuration
"""

from libqtile.config import Screen


def init_screens(colors, create_bar, go_to_group=None):
    """Initialize screens for each monitor"""

    screens = [
        Screen(
            top=create_bar(colors, primary=True, go_to_group_func=go_to_group),
            x11_drag_polling_rate=60,
        ),
        # Secondary monitor
        Screen(
            top=create_bar(colors, primary=False, go_to_group_func=go_to_group),
            x11_drag_polling_rate=60,
        ),
    ]

    return screens

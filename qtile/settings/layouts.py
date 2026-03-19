"""
Window layouts configuration
"""

from libqtile import layout
from libqtile.config import Match


def init_layouts(colors):
    """Initialize window layouts"""
    layouts = [
        layout.Columns(
            border_focus=colors["mauve"],
            border_focus_stack=colors["lavender"],
            border_normal=colors["surface0"],
            border_normal_stack=colors["surface0"],
            border_width=2,
            margin=8,
        ),
        layout.Max(
            border_focus=colors["mauve"],
            border_normal=colors["surface0"],
            border_width=2,
            margin=8,
        ),
        # Try more layouts by unleashing below layouts.
        # layout.Stack(num_stacks=2),
        # layout.Bsp(),
        # layout.Matrix(),
        # layout.MonadTall(),
        # layout.MonadWide(),
        # layout.RatioTile(),
        # layout.Tile(),
        # layout.TreeTab(),
        # layout.VerticalTile(),
        # layout.Zoomy(),
    ]

    floating_layout = layout.Floating(
        border_focus=colors["mauve"],
        border_normal=colors["surface0"],
        border_width=2,
        float_rules=[
            # Run the utility of `xprop` to see the wm class and name of an X client.
            *layout.Floating.default_float_rules,
            Match(wm_class="confirmreset"),  # gitk
            Match(wm_class="makebranch"),  # gitk
            Match(wm_class="maketag"),  # gitk
            Match(wm_class="ssh-askpass"),  # ssh-askpass
            Match(title="branchdialog"),  # gitk
            Match(title="pinentry"),  # GPG key password entry
        ]
    )

    return layouts, floating_layout

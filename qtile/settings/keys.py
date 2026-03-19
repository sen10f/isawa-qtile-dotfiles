"""
Keyboard shortcuts configuration
"""

import os
from libqtile.config import Key
from libqtile.lazy import lazy


def init_keys(mod, terminal, go_to_group, groups):
    """Initialize keyboard shortcuts"""
    keys = [
        # Sway-like keybindings
        # Window focus (Sway uses arrow keys and vim keys)
        Key([mod], "Left", lazy.layout.left(), desc="Move focus to left"),
        Key([mod], "Down", lazy.layout.down(), desc="Move focus down"),
        Key([mod], "Up", lazy.layout.up(), desc="Move focus up"),
        Key([mod], "Right", lazy.layout.right(), desc="Move focus to right"),
        Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
        Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
        Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
        Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),

        # Move windows (Sway: Mod+Shift+arrows or Mod+Shift+hjkl)
        Key([mod, "shift"], "Left", lazy.layout.shuffle_left(), desc="Move window to the left"),
        Key([mod, "shift"], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
        Key([mod, "shift"], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
        Key([mod, "shift"], "Right", lazy.layout.shuffle_right(), desc="Move window to the right"),
        Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
        Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
        Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
        Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),

        # Terminal (Sway: Mod+Return)
        Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),

        # Kill focused window (Sway: Mod+Shift+q)
        Key([mod, "shift"], "q", lazy.window.kill(), desc="Kill focused window"),

        # Reload config (Sway: Mod+Shift+c)
        Key([mod, "shift"], "c", lazy.reload_config(), desc="Reload the config"),

        # Exit (Sway: Mod+Shift+e)
        Key([mod, "shift"], "e", lazy.shutdown(), desc="Exit Qtile"),

        # Application launcher (Sway: Mod+d for dmenu/rofi)
        Key([mod], "d", lazy.spawn("rofi -show drun"), desc="Launch application launcher"),

        # Qtile メインメニュー - すべての機能にアクセス
        Key([mod], "space", lazy.spawn(os.path.expanduser("~/.config/qtile/qtile-menu.sh")), desc="Show Qtile menu"),

        # Workspace preview (Mod+Tab) - Rofi integration
        Key([mod], "Tab", lazy.spawn("python3 " + os.path.expanduser("~/.config/qtile/workspace-preview.py")), desc="Show workspace preview"),

        # Floating toggle (Sway: Mod+Shift+Space)
        Key([mod, "shift"], "space", lazy.window.toggle_floating(), desc="Toggle floating"),

        # Fullscreen (Sway: Mod+f)
        Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),

        # Layout modes (Sway uses: Mod+e for split, Mod+s for stacking, Mod+w for tabbed)
        # In Qtile we cycle through layouts
        Key([mod], "e", lazy.next_layout(), desc="Toggle to next layout"),

        # Split orientation (Sway: Mod+b for horizontal, Mod+v for vertical)
        Key([mod], "b", lazy.layout.toggle_split(), desc="Toggle split orientation"),
        Key([mod], "v", lazy.layout.toggle_split(), desc="Toggle split orientation"),

        # Resize mode is typically Mod+r in Sway, but here we use direct resize
        # Resize windows (Sway uses a resize mode, here we bind directly)
        Key([mod, "control"], "Left", lazy.layout.grow_left(), desc="Grow window to the left"),
        Key([mod, "control"], "Down", lazy.layout.grow_down(), desc="Grow window down"),
        Key([mod, "control"], "Up", lazy.layout.grow_up(), desc="Grow window up"),
        Key([mod, "control"], "Right", lazy.layout.grow_right(), desc="Grow window to the right"),
        Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
        Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
        Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
        Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),

        # Focus parent (Sway: Mod+a)
        Key([mod], "a", lazy.layout.up(), desc="Move focus to parent"),

        # Move focus between screens/monitors
        Key([mod], "comma", lazy.prev_screen(), desc="Focus previous monitor"),
        Key([mod], "period", lazy.next_screen(), desc="Focus next monitor"),

        # Display settings (GUI tool - requires arandr)
        Key([mod, "control"], "d", lazy.spawn("arandr"), desc="Display settings (ARandR)"),

        # Wallpaper settings (requires nitrogen)
        Key([mod, "control"], "w", lazy.spawn("nitrogen"), desc="Wallpaper settings (Nitrogen)"),

        # Audio settings (GUI tool - requires pavucontrol)
        Key([mod, "control"], "a", lazy.spawn("pavucontrol"), desc="Audio settings (PavuControl)"),

        # Volume control
        Key([], "XF86AudioRaiseVolume", lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"), desc="Increase volume"),
        Key([], "XF86AudioLowerVolume", lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), desc="Decrease volume"),
        Key([], "XF86AudioMute", lazy.spawn("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), desc="Mute/unmute"),
        Key([], "XF86AudioMicMute", lazy.spawn("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), desc="Mute/unmute mic"),

        # Media control (Media keys)
        Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause"), desc="Play/Pause media"),
        Key([], "XF86AudioNext", lazy.spawn("playerctl next"), desc="Next track"),
        Key([], "XF86AudioPrev", lazy.spawn("playerctl previous"), desc="Previous track"),
        Key([], "XF86AudioStop", lazy.spawn("playerctl stop"), desc="Stop media"),

        # Media control (Keyboard shortcuts)
        Key([mod], "m", lazy.spawn("playerctl play-pause"), desc="Play/Pause media"),
        Key([mod], "n", lazy.spawn("playerctl next"), desc="Next track"),
        Key([mod, "shift"], "n", lazy.spawn("playerctl previous"), desc="Previous track"),

        # Brightness control
        Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl set +5%"), desc="Increase brightness"),
        Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 5%-"), desc="Decrease brightness"),

        # Screenshot
        Key([], "Print", lazy.spawn("sh -c 'import png:- | tee ~/Pictures/screenshot-$(date +%Y%m%d-%H%M%S).png | xclip -selection clipboard -t image/png'"), desc="Screenshot selection"),
        Key([mod], "Print", lazy.spawn("sh -c 'import -window root png:- | tee ~/Pictures/screenshot-$(date +%Y%m%d-%H%M%S).png | xclip -selection clipboard -t image/png'"), desc="Screenshot fullscreen"),
        Key([mod, "shift"], "s", lazy.spawn("sh -c 'import png:- | tee ~/Pictures/screenshot-$(date +%Y%m%d-%H%M%S).png | xclip -selection clipboard -t image/png'"), desc="Screenshot selection (Sway-like)"),

        # Screen lock
        Key([mod, "shift"], "x", lazy.spawn("i3lock -c 000000"), desc="Lock screen"),

        # System power menu
        Key([mod, "shift"], "p", lazy.spawn("rofi -show power-menu -modi power-menu:~/.local/bin/rofi-power-menu"), desc="Power menu"),

        # Clipboard manager
        Key([mod], "c", lazy.spawn("copyq show"), desc="Clipboard history"),

        # Cheatsheet
        Key([mod], "slash", lazy.spawn(terminal + " -e less " + os.path.expanduser("~/.config/qtile/cheatsheet.txt")), desc="Show cheatsheet"),

        # Scratchpad toggles
        Key([mod], "grave", lazy.group["scratchpad"].dropdown_toggle("term"), desc="Toggle dropdown terminal"),
        Key([mod, "shift"], "grave", lazy.group["scratchpad"].dropdown_toggle("calc"), desc="Toggle calculator"),
        Key([mod, "control"], "grave", lazy.group["scratchpad"].dropdown_toggle("files"), desc="Toggle file manager"),

        # Reset current workspace layout (fixes buggy workspace states)
        Key([mod, "shift"], "r", lazy.layout.normalize(), desc="Normalize current layout"),
        Key([mod, "control", "shift"], "r", lazy.group.setlayout(0), desc="Reset to first layout"),
    ]

    # Add key bindings to switch VTs in Wayland
    for vt in range(1, 8):
        keys.append(
            Key(
                ["control", "mod1"],
                f"f{vt}",
                lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
                desc=f"Switch to VT{vt}",
            )
        )

    # Workspace switching keys
    for i in groups[:9]:  # Only for numbered groups, not scratchpad
        keys.extend(
            [
                # mod + group number = switch to group (with auto-swap)
                Key(
                    [mod],
                    i.name,
                    go_to_group(i.name),
                    desc=f"Switch to group {i.name}",
                ),
                # mod + shift + group number = move focused window to group
                Key(
                    [mod, "shift"],
                    i.name,
                    lazy.window.togroup(i.name),
                    desc=f"Move focused window to group {i.name}",
                ),
            ]
        )

    return keys

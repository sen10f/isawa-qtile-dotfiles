"""
Keyboard shortcuts configuration
"""

import json
import os
from pathlib import Path
from libqtile.config import Key
from libqtile.lazy import lazy

_theme = json.loads((Path(__file__).parent.parent / "theme.json").read_text())
_apps  = _theme.get("apps", {})
_kb    = _theme.get("keybindings", {})


def init_keys(mod, terminal, go_to_group, groups):
    """Initialize keyboard shortcuts"""

    def _get_kb(action, default_mods_tokens, default_key):
        """Return (mods_list, key) from theme.json keybindings."""
        entry = _kb.get(action)
        if isinstance(entry, dict):
            mods_tokens = entry.get("mods", default_mods_tokens)
            key = entry.get("key", default_key)
        else:
            mods_tokens = default_mods_tokens
            key = default_key
        mods = [mod if t == "mod" else t for t in mods_tokens]
        return mods, key

    keys = [
        # Sway-like keybindings
        # Window focus (Sway uses arrow keys and vim keys)
        Key([mod], "Left",  lazy.layout.left(),  desc="Move focus to left"),
        Key([mod], "Down",  lazy.layout.down(),  desc="Move focus down"),
        Key([mod], "Up",    lazy.layout.up(),    desc="Move focus up"),
        Key([mod], "Right", lazy.layout.right(), desc="Move focus to right"),
        Key([mod], "h",     lazy.layout.left(),  desc="Move focus to left"),
        Key([mod], "j",     lazy.layout.down(),  desc="Move focus down"),
        Key([mod], "k",     lazy.layout.up(),    desc="Move focus up"),
        Key([mod], "l",     lazy.layout.right(), desc="Move focus to right"),

        # Move windows (Sway: Mod+Shift+arrows or Mod+Shift+hjkl)
        Key([mod, "shift"], "Left",  lazy.layout.shuffle_left(),  desc="Move window to the left"),
        Key([mod, "shift"], "Down",  lazy.layout.shuffle_down(),  desc="Move window down"),
        Key([mod, "shift"], "Up",    lazy.layout.shuffle_up(),    desc="Move window up"),
        Key([mod, "shift"], "Right", lazy.layout.shuffle_right(), desc="Move window to the right"),
        Key([mod, "shift"], "h",     lazy.layout.shuffle_left(),  desc="Move window to the left"),
        Key([mod, "shift"], "j",     lazy.layout.shuffle_down(),  desc="Move window down"),
        Key([mod, "shift"], "k",     lazy.layout.shuffle_up(),    desc="Move window up"),
        Key([mod, "shift"], "l",     lazy.layout.shuffle_right(), desc="Move window to the right"),

        # Resize windows
        Key([mod, "control"], "Left",  lazy.layout.grow_left(),  desc="Grow window to the left"),
        Key([mod, "control"], "Down",  lazy.layout.grow_down(),  desc="Grow window down"),
        Key([mod, "control"], "Up",    lazy.layout.grow_up(),    desc="Grow window up"),
        Key([mod, "control"], "Right", lazy.layout.grow_right(), desc="Grow window to the right"),
        Key([mod, "control"], "h",     lazy.layout.grow_left(),  desc="Grow window to the left"),
        Key([mod, "control"], "j",     lazy.layout.grow_down(),  desc="Grow window down"),
        Key([mod, "control"], "k",     lazy.layout.grow_up(),    desc="Grow window up"),
        Key([mod, "control"], "l",     lazy.layout.grow_right(), desc="Grow window to the right"),

        # Split orientation
        Key([mod], "b", lazy.layout.toggle_split(), desc="Toggle split orientation"),
        Key([mod], "v", lazy.layout.toggle_split(), desc="Toggle split orientation"),

        # Focus parent
        Key([mod], "a", lazy.layout.up(), desc="Move focus to parent"),

        # Move focus between screens/monitors
        Key([mod], "comma",  lazy.prev_screen(), desc="Focus previous monitor"),
        Key([mod], "period", lazy.next_screen(), desc="Focus next monitor"),

        # Reset layout
        Key([mod, "shift"],           "r", lazy.layout.normalize(),   desc="Normalize current layout"),
        Key([mod, "control", "shift"], "r", lazy.group.setlayout(0), desc="Reset to first layout"),

        # Volume control
        Key([], "XF86AudioRaiseVolume", lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"), desc="Increase volume"),
        Key([], "XF86AudioLowerVolume", lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), desc="Decrease volume"),
        Key([], "XF86AudioMute",        lazy.spawn("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),   desc="Mute/unmute"),
        Key([], "XF86AudioMicMute",     lazy.spawn("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), desc="Mute/unmute mic"),

        # Media control (Media keys)
        Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause"), desc="Play/Pause media"),
        Key([], "XF86AudioNext", lazy.spawn("playerctl next"),        desc="Next track"),
        Key([], "XF86AudioPrev", lazy.spawn("playerctl previous"),    desc="Previous track"),
        Key([], "XF86AudioStop", lazy.spawn("playerctl stop"),        desc="Stop media"),

        # Media control (keyboard)
        Key([mod], "m",          lazy.spawn("playerctl play-pause"), desc="Play/Pause media"),
        Key([mod], "n",          lazy.spawn("playerctl next"),        desc="Next track"),
        Key([mod, "shift"], "n", lazy.spawn("playerctl previous"),    desc="Previous track"),

        # Brightness control
        Key([], "XF86MonBrightnessUp",   lazy.spawn("brightnessctl set +5%"), desc="Increase brightness"),
        Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 5%-"), desc="Decrease brightness"),

        # Exit (hardcoded - safety key)
        Key([mod, "shift"], "e", lazy.shutdown(), desc="Exit Qtile"),
    ]

    # -----------------------------------------------------------------------
    # Configurable keybindings from theme.json
    # -----------------------------------------------------------------------

    # Terminal
    _mods, _key = _get_kb("terminal", ["mod"], "Return")
    keys.append(Key(_mods, _key, lazy.spawn(terminal), desc="Launch terminal"))

    # Application launcher
    _mods, _key = _get_kb("launcher", ["mod"], "d")
    keys.append(Key(_mods, _key, lazy.spawn("rofi -show drun"), desc="Launch application launcher"))

    # Qtile main menu
    _mods, _key = _get_kb("menu", ["mod"], "space")
    keys.append(Key(_mods, _key, lazy.spawn(os.path.expanduser("~/.config/qtile/qtile-menu.sh")), desc="Show Qtile menu"))

    # Workspace preview
    _mods, _key = _get_kb("workspace_preview", ["mod"], "Tab")
    keys.append(Key(_mods, _key, lazy.spawn("python3 " + os.path.expanduser("~/.config/qtile/workspace-preview.py")), desc="Show workspace preview"))

    # Close window
    _mods, _key = _get_kb("close_window", ["mod", "shift"], "q")
    keys.append(Key(_mods, _key, lazy.window.kill(), desc="Kill focused window"))

    # Toggle floating
    _mods, _key = _get_kb("toggle_floating", ["mod", "shift"], "space")
    keys.append(Key(_mods, _key, lazy.window.toggle_floating(), desc="Toggle floating"))

    # Toggle fullscreen
    _mods, _key = _get_kb("toggle_fullscreen", ["mod"], "f")
    keys.append(Key(_mods, _key, lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"))

    # Next layout
    _mods, _key = _get_kb("next_layout", ["mod"], "e")
    keys.append(Key(_mods, _key, lazy.next_layout(), desc="Toggle to next layout"))

    # Reload config
    _mods, _key = _get_kb("reload_config", ["mod", "shift"], "c")
    keys.append(Key(_mods, _key, lazy.reload_config(), desc="Reload the config"))

    # Lock screen
    _mods, _key = _get_kb("lock_screen", ["mod", "shift"], "x")
    keys.append(Key(_mods, _key, lazy.spawn("i3lock -c 000000"), desc="Lock screen"))

    # Power menu
    _mods, _key = _get_kb("power_menu", ["mod", "shift"], "p")
    keys.append(Key(_mods, _key, lazy.spawn("rofi -show power-menu -modi power-menu:~/.local/bin/rofi-power-menu"), desc="Power menu"))

    # Screenshot (selection)
    _mods, _key = _get_kb("screenshot_select", [], "Print")
    keys.append(Key(_mods, _key,
        lazy.spawn("sh -c 'import png:- | tee ~/Pictures/screenshot-$(date +%Y%m%d-%H%M%S).png | xclip -selection clipboard -t image/png'"),
        desc="Screenshot selection"))

    # Screenshot (fullscreen)
    _mods, _key = _get_kb("screenshot_full", ["mod"], "Print")
    keys.append(Key(_mods, _key,
        lazy.spawn("sh -c 'import -window root png:- | tee ~/Pictures/screenshot-$(date +%Y%m%d-%H%M%S).png | xclip -selection clipboard -t image/png'"),
        desc="Screenshot fullscreen"))

    # Clipboard manager
    _mods, _key = _get_kb("clipboard", ["mod"], "c")
    keys.append(Key(_mods, _key, lazy.spawn("copyq show"), desc="Clipboard history"))

    # Display settings
    _mods, _key = _get_kb("display", ["mod", "control"], "d")
    keys.append(Key(_mods, _key, lazy.spawn("arandr"), desc="Display settings (ARandR)"))

    # Wallpaper settings
    _mods, _key = _get_kb("wallpaper", ["mod", "control"], "w")
    keys.append(Key(_mods, _key, lazy.spawn("nitrogen"), desc="Wallpaper settings (Nitrogen)"))

    # Audio settings
    _mods, _key = _get_kb("audio", ["mod", "control"], "a")
    keys.append(Key(_mods, _key, lazy.spawn("pavucontrol"), desc="Audio settings (PavuControl)"))

    # Cheatsheet
    _mods, _key = _get_kb("cheatsheet", ["mod"], "slash")
    keys.append(Key(_mods, _key, lazy.spawn(terminal + " -e less " + os.path.expanduser("~/.config/qtile/cheatsheet.txt")), desc="Show cheatsheet"))

    # Scratchpad toggles
    _mods, _key = _get_kb("scratchpad_term", ["mod"], "grave")
    keys.append(Key(_mods, _key, lazy.group["scratchpad"].dropdown_toggle("term"), desc="Toggle dropdown terminal"))

    _mods, _key = _get_kb("scratchpad_calc", ["mod", "shift"], "grave")
    keys.append(Key(_mods, _key, lazy.group["scratchpad"].dropdown_toggle("calc"), desc="Toggle calculator"))

    _mods, _key = _get_kb("scratchpad_files", ["mod", "control"], "grave")
    keys.append(Key(_mods, _key, lazy.group["scratchpad"].dropdown_toggle("files"), desc="Toggle file manager"))

    # Browser (optional - only if configured)
    if _apps.get("browser"):
        _mods, _key = _get_kb("browser", ["mod"], "w")
        keys.append(Key(_mods, _key, lazy.spawn(_apps["browser"]), desc="Launch browser"))

    # -----------------------------------------------------------------------
    # Add key bindings to switch VTs in Wayland
    # -----------------------------------------------------------------------
    from libqtile import qtile
    for vt in range(1, 8):
        keys.append(
            Key(
                ["control", "mod1"],
                f"f{vt}",
                lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
                desc=f"Switch to VT{vt}",
            )
        )

    # -----------------------------------------------------------------------
    # Workspace switching keys
    # -----------------------------------------------------------------------
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

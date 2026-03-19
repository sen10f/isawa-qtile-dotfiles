"""
Hooks and autostart configuration
"""

import os
import shutil
import subprocess
import configparser
from pathlib import Path
from libqtile import hook


def get_blurred_wallpaper():
    """Get or create a blurred version of the current wallpaper for lock screen"""
    home = Path.home()
    nitrogen_config = home / '.config' / 'nitrogen' / 'bg-saved.cfg'
    cache_dir = home / '.cache' / 'qtile'
    lockscreen_image = cache_dir / 'lockscreen.png'

    # Create cache directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Read current wallpaper from nitrogen config
    wallpaper_path = None
    if nitrogen_config.exists():
        config = configparser.ConfigParser()
        config.read(nitrogen_config)
        # Get wallpaper from first display
        if 'xin_0' in config and 'file' in config['xin_0']:
            wallpaper_path = Path(config['xin_0']['file'])

    # If no wallpaper found or wallpaper doesn't exist, return None
    if not wallpaper_path or not wallpaper_path.exists():
        return None

    # Check if lockscreen image is up-to-date
    if lockscreen_image.exists():
        wallpaper_mtime = wallpaper_path.stat().st_mtime
        lockscreen_mtime = lockscreen_image.stat().st_mtime
        if lockscreen_mtime > wallpaper_mtime:
            return str(lockscreen_image)

    # Create blurred version using ImageMagick
    try:
        subprocess.run([
            'convert',
            str(wallpaper_path),
            '-filter', 'Gaussian',
            '-blur', '0x8',
            str(lockscreen_image)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(lockscreen_image)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If blur fails, fall back to original wallpaper
        return str(wallpaper_path)


def setup_environment():
    """Set environment variables for dark theme"""
    # Set environment variables for dark theme
    os.environ['GTK_THEME'] = 'Yaru-bark-dark'
    os.environ['QT_QPA_PLATFORMTHEME'] = 'gtk3'
    os.environ['QT_STYLE_OVERRIDE'] = 'Adwaita-Dark'

    # Force dark mode for browsers and Electron apps
    os.environ['GTK_APPLICATION_PREFER_DARK_THEME'] = '1'
    # For Chromium-based browsers (Chrome, Vivaldi, Edge, etc.)
    os.environ['CHROME_ENABLE_DARK_MODE'] = '1'
    # For Electron apps (VS Code, Discord, etc.)
    os.environ['ELECTRON_ENABLE_DARK_MODE'] = '1'


def init_hooks():
    """Initialize hooks"""
    # Note: Workspace synchronization is now handled by the go_to_group function
    # which is used by both keyboard shortcuts and GroupBox clicks.
    # No need for aggressive hooks that interfere with normal operation.

    @hook.subscribe.startup_once
    def autostart():
        """Run autostart applications once when Qtile starts"""
        home = os.path.expanduser('~')

        # Set GTK and Qt theme to dark mode
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', 'prefer-dark'])
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', 'Yaru-bark-dark'])

        # Set cursor theme (fixes cursor disappearing issues)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'cursor-theme', 'Yaru'])
        subprocess.run(['xsetroot', '-cursor_name', 'left_ptr'])

        # Fix cursor size for HiDPI if needed
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'cursor-size', '24'])

        # Set display refresh rates
        # Adjust these values to match your monitors and desired refresh rates
        subprocess.run([
            'xrandr',
            '--output', 'DP-4', '--mode', '1920x1080', '--rate', '280', '--pos', '0x0', '--primary',
            '--output', 'HDMI-0', '--mode', '1920x1080', '--rate', '60', '--pos', '1920x0'
        ])

        # Kill existing picom process before starting new one
        subprocess.run(['pkill', 'picom'], stderr=subprocess.DEVNULL)

        start_picom()

        # Get blurred wallpaper for lock screen
        lockscreen_bg = get_blurred_wallpaper()
        if lockscreen_bg:
            lockscreen_cmd = f'xss-lock -- i3lock -i {lockscreen_bg}'
        else:
            # Fallback to dark gray if wallpaper not found
            lockscreen_cmd = 'xss-lock -- i3lock -c 2e3440'

        # List of applications to autostart
        autostart_apps = [
            # Input method
            'fcitx5 -d',

            # Theme and appearance
            '/usr/lib/x86_64-linux-gnu/xfce4/xfconf/xfconfd',  # XFCE settings daemon (for theme support)
            'xsettingsd',  # X settings daemon (alternative, lightweight)
            'nitrogen --restore',  # Restore wallpaper

            # System services
            '/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1',  # PolicyKit authentication agent
            lockscreen_cmd,  # Auto lock on suspend/idle with blurred wallpaper

            # Common autostart applications
            'nm-applet',  # Network Manager applet
            'blueman-applet',  # Bluetooth applet
            'dunst',  # Notification daemon
            'flameshot',  # Screenshot tool
            'xfce4-power-manager',  # Power management
            'copyq',  # Clipboard manager daemon
            'nextcloud',  # Nextcloud client
            '~/.config/qtile/amazon-music-mpris.py',  # Amazon Music MPRIS bridge

            # Run applications from ~/.config/autostart/ (requires dex package)
            # Uncomment after installing dex: sudo apt install dex
            'dex -a -s ~/.config/autostart',
        ]

        for app in autostart_apps:
            subprocess.Popen(app, shell=True)

    @hook.subscribe.startup
    def ensure_picom_running():
        """Start picom if it's not already running (e.g., after reload)"""
        start_picom()


def start_picom():
    """Start picom with user config if available and not already running"""
    if shutil.which('picom') is None:
        return

    # Avoid spawning multiple instances
    if subprocess.run(['pgrep', '-x', 'picom'], stdout=subprocess.DEVNULL).returncode == 0:
        return

    picom_config = os.path.expanduser('~/.config/picom/picom.conf')
    cmd = ['picom', '--config', picom_config]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

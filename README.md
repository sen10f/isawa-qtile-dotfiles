# isawa-qtile-dotfiles

Qtile and related desktop environment configuration files.

## Components

| Tool | Role |
|------|------|
| [Qtile](https://qtile.org/) | Tiling window manager |
| [Picom](https://github.com/yshui/picom) | Compositor (shadows, fading, transparency) |
| [Dunst](https://dunst-project.org/) | Notification daemon |
| [Rofi](https://github.com/davatorium/rofi) | Application launcher |
| [Nitrogen](https://github.com/l3ib/nitrogen) | Wallpaper manager |

## Color Scheme

[Catppuccin Mocha](https://github.com/catppuccin/catppuccin) — dark theme used consistently across all components.

## Setup

Install dependencies:

```bash
# Window manager
pipx install qtile

# Desktop environment tools
sudo apt install picom dunst rofi nitrogen \
  fcitx5 fcitx5-mozc \
  i3lock xss-lock dex \
  playerctl brightnessctl \
  nm-applet blueman \
  flameshot copyq \
  xfce4-power-manager
```

Copy configs:

```bash
cp -r qtile ~/.config/qtile
cp -r picom ~/.config/picom
cp -r dunst ~/.config/dunst
cp -r rofi ~/.config/rofi
cp -r nitrogen ~/.config/nitrogen
```

## Key Bindings

See [`qtile/cheatsheet.txt`](qtile/cheatsheet.txt) for a full list.

| Key | Action |
|-----|--------|
| `Mod + Return` | Terminal |
| `Mod + d` | Rofi launcher |
| `Mod + Space` | Qtile menu |
| `Mod + h/j/k/l` | Focus movement |
| `Mod + Shift + h/j/k/l` | Window movement |
| `Mod + 1~9` | Switch workspace |
| `` Mod + ` `` | Dropdown terminal |
| `Mod + Shift + c` | Reload config |
| `Mod + Shift + p` | Power menu |
| `Mod + Shift + x` | Lock screen |

## Structure

```
.
├── qtile/          # ~/.config/qtile/
│   ├── config.py
│   └── settings/
│       ├── colors.py
│       ├── keys.py
│       ├── layouts.py
│       ├── widgets.py
│       ├── screens.py
│       ├── groups.py
│       ├── hooks.py
│       └── audio_device.py
├── picom/          # ~/.config/picom/
├── dunst/          # ~/.config/dunst/
├── rofi/           # ~/.config/rofi/
└── nitrogen/       # ~/.config/nitrogen/
```

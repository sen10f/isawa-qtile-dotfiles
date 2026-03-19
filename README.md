# isawa-qtile-dotfiles

Qtile 入門者向けのデスクトップ環境設定ファイル一式。
**Ubuntu** を前提とし、インストールから日常操作まで迷わず始められることを目指した構成。
`theme.json` 一つで全ツールのカラー・レイアウト・キーバインドを一元管理する。

## コンポーネント

| ツール | 役割 |
|--------|------|
| [Qtile](https://qtile.org/) | タイル型ウィンドウマネージャー |
| [Picom](https://github.com/yshui/picom) | コンポジター（シャドウ・フェード・透明度） |
| [Dunst](https://dunst-project.org/) | 通知デーモン |
| [Rofi](https://github.com/davatorium/rofi) | アプリランチャー |
| [Nitrogen](https://github.com/l3ib/nitrogen) | 壁紙マネージャー |
| [fcitx5](https://fcitx-im.org/) | 日本語入力 (Mozc) |

## カラースキーム

[Catppuccin Mocha](https://github.com/catppuccin/catppuccin) を全ツールに統一適用。
Latte / Frappé / Macchiato のプリセットも GUI から切り替えられる。

## 動作環境

- **Ubuntu 22.04 / 24.04** (LTS 推奨)
- Python 3.10 以上
- X11 セッション

## セットアップ

```bash
git clone https://github.com/sen10f/isawa-qtile-dotfiles.git
cd isawa-qtile-dotfiles
bash setup.sh
```

スクリプトが以下を自動で実行する：

- 必要なシステムパッケージの一括インストール
- Qtile を pipx でインストール・ディスプレイマネージャーへ登録
- 設定ファイルを `~/.config/` 以下にコピー
- fcitx5 の環境変数設定
- picom / dunst / rofi へのテーマ適用

セットアップ完了後、ログアウトしてディスプレイマネージャーで **Qtile** セッションを選択してログインする。

> **要確認:** `settings/hooks.py` 内の xrandr 設定（ディスプレイ名・解像度）はマシン固有のため、
> セットアップ後に手動で編集する。
> `xrandr --listmonitors` で接続中のディスプレイ名を確認できる。

## GUI 設定ツール

`theme.json` をビジュアルに編集できる GUI アプリが付属している。コマンドラインの知識は不要。

```bash
python3 ~/.config/qtile/qtile-config-gui.py
# またはアプリランチャーから「Qtile Config」を検索
```

設定できる項目：

| タブ | 内容 |
|------|------|
| カラーテーマ | 26色のパレットをカラーピッカーで編集・プリセット切替 |
| レイアウト・バー | ウィンドウ枠の太さ・マージン・バー高さ・フォントサイズ |
| スクラッチパッド | ドロップダウン端末・電卓・ファイルマネージャーのサイズと位置 |
| Picom エフェクト | シャドウ・フェードアニメーション・背景ブラー |
| 通知 (Dunst) | 優先度別の背景色・枠色・表示時間 |
| ウィジェット配色 | バー上の各ウィジェットの色をパレットから選択 |
| キーバインド | 22項目を修飾キー（Mod / Mod+Shift / Mod+Ctrl 等）ごと変更 |

「保存して適用」ボタン一つで picom・dunst・rofi に即反映される。

## キーバインド

> Mod = Super (Windows) キー
> 全一覧は [`qtile/cheatsheet.txt`](qtile/cheatsheet.txt) を参照。

| キー | 動作 |
|------|------|
| `Mod + Return` | ターミナル起動 |
| `Mod + d` | アプリランチャー (Rofi) |
| `Mod + Space` | Qtile メニュー |
| `Mod + h/j/k/l` | ウィンドウフォーカス移動 |
| `Mod + Shift + h/j/k/l` | ウィンドウ移動 |
| `Mod + 1〜9` | ワークスペース切替 |
| `` Mod + ` `` | ドロップダウン端末 |
| `Mod + Shift + c` | 設定リロード |
| `Mod + Shift + p` | 電源メニュー |
| `Mod + Shift + x` | 画面ロック |
| `Mod + /` | キーバインド一覧 (チートシート) |

## ディレクトリ構成

```
.
├── setup.sh                 # セットアップスクリプト
├── qtile/                   # ~/.config/qtile/
│   ├── config.py
│   ├── theme.json           # 全設定の管理ファイル（唯一の編集対象）
│   ├── apply_theme.py       # テーマを picom/dunst/rofi に反映
│   ├── qtile-config-gui.py  # GUI 設定ツール
│   └── settings/
│       ├── colors.py
│       ├── keys.py
│       ├── layouts.py
│       ├── widgets.py
│       ├── screens.py
│       ├── groups.py
│       ├── hooks.py
│       └── audio_device.py
├── picom/                   # ~/.config/picom/
├── dunst/                   # ~/.config/dunst/
├── rofi/                    # ~/.config/rofi/
└── nitrogen/                # ~/.config/nitrogen/
```

---

# isawa-qtile-dotfiles (English)

A beginner-friendly Qtile desktop environment dotfiles collection.
Designed for **Ubuntu** users who want to start using a tiling window manager without the steep learning curve.
All colors, layouts, and keybindings are managed from a single `theme.json` file.

## Components

| Tool | Role |
|------|------|
| [Qtile](https://qtile.org/) | Tiling window manager |
| [Picom](https://github.com/yshui/picom) | Compositor (shadows, fading, transparency) |
| [Dunst](https://dunst-project.org/) | Notification daemon |
| [Rofi](https://github.com/davatorium/rofi) | Application launcher |
| [Nitrogen](https://github.com/l3ib/nitrogen) | Wallpaper manager |
| [fcitx5](https://fcitx-im.org/) | Japanese input (Mozc) |

## Color Scheme

[Catppuccin Mocha](https://github.com/catppuccin/catppuccin) applied consistently across all tools.
Latte, Frappé, and Macchiato presets are also available via the GUI.

## Requirements

- **Ubuntu 22.04 / 24.04** (LTS recommended)
- Python 3.10+
- X11 session

## Setup

```bash
git clone https://github.com/sen10f/isawa-qtile-dotfiles.git
cd isawa-qtile-dotfiles
bash setup.sh
```

The script handles everything automatically:

- Installs all required system packages
- Installs Qtile via pipx and registers it with the display manager
- Copies config files to `~/.config/`
- Configures fcitx5 environment variables
- Applies the theme to picom, dunst, and rofi

After setup, log out and select the **Qtile** session in the display manager.

> **Note:** The xrandr settings in `settings/hooks.py` (display names, resolutions) are machine-specific
> and need to be edited manually after setup.
> Run `xrandr --listmonitors` to check your connected display names.

## GUI Configuration Tool

A GUI app is included for editing `theme.json` visually — no command-line knowledge required.

```bash
python3 ~/.config/qtile/qtile-config-gui.py
# or search "Qtile Config" in the app launcher
```

| Tab | Settings |
|-----|----------|
| Color Theme | Edit 26-color palette with a color picker; switch presets |
| Layout & Bar | Window border width, margin, bar height, font size |
| Scratchpad | Size and position of dropdown terminal, calculator, file manager |
| Picom Effects | Shadow, fade animation, background blur |
| Notifications (Dunst) | Background/border color and timeout per urgency level |
| Widget Colors | Choose bar widget colors from the palette |
| Keybindings | Remap 22 actions with modifier key selection (Mod / Mod+Shift / Mod+Ctrl, etc.) |

Changes are applied instantly to picom, dunst, and rofi with a single click.

## Keybindings

> Mod = Super (Windows) key
> Full list: [`qtile/cheatsheet.txt`](qtile/cheatsheet.txt)

| Key | Action |
|-----|--------|
| `Mod + Return` | Launch terminal |
| `Mod + d` | App launcher (Rofi) |
| `Mod + Space` | Qtile menu |
| `Mod + h/j/k/l` | Move window focus |
| `Mod + Shift + h/j/k/l` | Move window |
| `Mod + 1–9` | Switch workspace |
| `` Mod + ` `` | Dropdown terminal |
| `Mod + Shift + c` | Reload config |
| `Mod + Shift + p` | Power menu |
| `Mod + Shift + x` | Lock screen |
| `Mod + /` | Show cheatsheet |

## Directory Structure

```
.
├── setup.sh                 # One-command setup script
├── qtile/                   # ~/.config/qtile/
│   ├── config.py
│   ├── theme.json           # Single source of truth for all settings
│   ├── apply_theme.py       # Applies theme to picom/dunst/rofi
│   ├── qtile-config-gui.py  # GUI configuration tool
│   └── settings/
│       ├── colors.py
│       ├── keys.py
│       ├── layouts.py
│       ├── widgets.py
│       ├── screens.py
│       ├── groups.py
│       ├── hooks.py
│       └── audio_device.py
├── picom/                   # ~/.config/picom/
├── dunst/                   # ~/.config/dunst/
├── rofi/                    # ~/.config/rofi/
└── nitrogen/                # ~/.config/nitrogen/
```

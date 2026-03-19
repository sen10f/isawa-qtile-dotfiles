#!/usr/bin/env python3
"""
apply_theme.py — theme.json の設定を各ツールの設定ファイルに反映する

使い方:
    python3 ~/.config/qtile/apply_theme.py
    python3 ~/.config/qtile/apply_theme.py --no-restart  # ファイル更新のみ
"""

import json
import re
import subprocess
import sys
from pathlib import Path

QTILE_DIR  = Path(__file__).parent
THEME_FILE = QTILE_DIR / "theme.json"

PICOM_CONF  = Path.home() / ".config/picom/picom.conf"
DUNST_CONF  = Path.home() / ".config/dunst/dunstrc"
ROFI_THEME  = Path.home() / ".config/rofi/catppuccin-mocha.rasi"


def load_theme() -> dict:
    return json.loads(THEME_FILE.read_text())


# ---------------------------------------------------------------------------
# picom.conf
# ---------------------------------------------------------------------------

def _picom_sub(text: str, key: str, value) -> str:
    """picom の `key = value;` 行を置換する"""
    pattern = rf"(^{re.escape(key)}\s*=\s*)[^;]+(;)"
    repl = rf"\g<1>{value}\2"
    new_text, n = re.subn(pattern, repl, text, flags=re.MULTILINE)
    if n == 0:
        print(f"  [警告] picom: '{key}' が見つかりませんでした")
    return new_text


def apply_picom(cfg: dict) -> None:
    text = PICOM_CONF.read_text()
    c = cfg["picom"]
    text = _picom_sub(text, "shadow-radius",   c["shadow_radius"])
    text = _picom_sub(text, "shadow-opacity",  c["shadow_opacity"])
    text = _picom_sub(text, "shadow-offset-x", c["shadow_offset_x"])
    text = _picom_sub(text, "shadow-offset-y", c["shadow_offset_y"])
    text = _picom_sub(text, "fade-in-step",    c["fade_in_step"])
    text = _picom_sub(text, "fade-out-step",   c["fade_out_step"])
    text = _picom_sub(text, "fade-delta",      c["fade_delta"])
    text = _picom_sub(text, "inactive-opacity", c["inactive_opacity"])
    text = _picom_sub(text, "blur-strength",   c["blur_strength"])
    blur_bg = "true" if c["blur_background"] else "false"
    text = _picom_sub(text, "blur-background", blur_bg)
    PICOM_CONF.write_text(text)
    print("  picom.conf を更新しました")


# ---------------------------------------------------------------------------
# dunstrc
# ---------------------------------------------------------------------------

def _dunst_sub_global(text: str, key: str, value) -> str:
    """dunstrc [global] セクション内の `key = value` を置換する"""
    # [global] から次のセクション開始までの範囲で置換
    pattern = rf"(^\s*{re.escape(key)}\s*=\s*).*"
    # 最初の1箇所だけ置換（globalセクションの値）
    new_text, n = re.subn(pattern, rf"\g<1>{value}", text, count=1, flags=re.MULTILINE)
    if n == 0:
        print(f"  [警告] dunst: '{key}' が見つかりませんでした")
    return new_text


def _dunst_sub_section(text: str, section: str, key: str, value) -> str:
    """dunstrc の特定セクション内の値を置換する"""
    # セクション見出しから次のセクション（または終端）までを切り出して置換
    sec_pattern = rf"(\[{re.escape(section)}\][^\[]*)"
    match = re.search(sec_pattern, text, re.DOTALL)
    if not match:
        print(f"  [警告] dunst: セクション '[{section}]' が見つかりませんでした")
        return text
    block = match.group(1)
    key_pattern = rf"(^\s*{re.escape(key)}\s*=\s*).*"
    new_block, n = re.subn(key_pattern, rf'\g<1>"{value}"', block, flags=re.MULTILINE)
    if n == 0:
        # 引用符なしの数値も試す
        new_block, n = re.subn(key_pattern, rf'\g<1>{value}', block, flags=re.MULTILINE)
    if n == 0:
        print(f"  [警告] dunst: '[{section}]' 内の '{key}' が見つかりませんでした")
        return text
    return text[:match.start()] + new_block + text[match.end():]


def apply_dunst(cfg: dict) -> None:
    text = DUNST_CONF.read_text()
    c = cfg["dunst"]

    # グローバル設定
    text = _dunst_sub_global(text, "corner_radius",      c["corner_radius"])
    text = _dunst_sub_global(text, "padding",            c["padding"])
    text = _dunst_sub_global(text, "horizontal_padding", c["horizontal_padding"])
    text = _dunst_sub_global(text, "frame_width",        c["frame_width"])
    text = _dunst_sub_global(text, "font",               c["font"])
    # global の frame_color は引用符付き
    text = re.sub(
        r'(^\s*frame_color\s*=\s*)"#[0-9a-fA-F]{6}"',
        rf'\g<1>"{c["frame_color"]}"',
        text, count=1, flags=re.MULTILINE
    )

    # urgency 別設定
    for urgency in ("urgency_low", "urgency_normal", "urgency_critical"):
        u = c[urgency]
        text = _dunst_sub_section(text, urgency, "background",  u["background"])
        text = _dunst_sub_section(text, urgency, "foreground",  u["foreground"])
        text = _dunst_sub_section(text, urgency, "frame_color", u["frame_color"])
        # timeout は数値（引用符なし）
        text = re.sub(
            rf'(\[{re.escape(urgency)}\][^\[]*?^\s*timeout\s*=\s*)\d+',
            rf'\g<1>{u["timeout"]}',
            text, flags=re.MULTILINE | re.DOTALL, count=1
        )

    DUNST_CONF.write_text(text)
    print("  dunstrc を更新しました")


# ---------------------------------------------------------------------------
# rofi/catppuccin-mocha.rasi
# ---------------------------------------------------------------------------

def apply_rofi(cfg: dict) -> None:
    text = ROFI_CONF = ROFI_THEME.read_text()
    colors = cfg["colors"]
    rofi   = cfg["rofi"]

    # * { } ブロック内のカラー変数を更新
    # パレット色: `    colorname: #hex;`
    for name, hex_val in colors.items():
        pattern = rf"(\s+{re.escape(name)}:\s*)#[0-9a-fA-F]{{6}}(;)"
        text, n = re.subn(pattern, rf"\g<1>{hex_val}\2", text)

    # bg / bg-alt / fg / fg-alt エイリアス（パレット由来）
    aliases = {
        "bg":     colors["base"],
        "bg-alt": colors["surface0"],
        "fg":     colors["text"],
        "fg-alt": colors["subtext1"],
    }
    for name, hex_val in aliases.items():
        pattern = rf"(\s+{re.escape(name)}:\s*)#[0-9a-fA-F]{{6}}(;)"
        text, n = re.subn(pattern, rf"\g<1>{hex_val}\2", text)

    # window ブロックの width と border-radius のみ置換
    def replace_window_block(m):
        block = m.group(0)
        block = re.sub(r"(width:\s*)[^;]+;", rf"\g<1>{rofi['window_width']};", block)
        block = re.sub(r"(border-radius:\s*)[^;]+;",
                       rf"\g<1>{rofi['window_border_radius']};", block)
        return block
    text = re.sub(r"window\s*\{[^}]+\}", replace_window_block, text)

    # listview の lines
    text = re.sub(r"(lines:\s*)\d+;", rf"\g<1>{rofi['listview_lines']};", text)

    ROFI_THEME.write_text(text)
    print("  catppuccin-mocha.rasi を更新しました")


# ---------------------------------------------------------------------------
# サービス再起動
# ---------------------------------------------------------------------------

def restart_services() -> None:
    print("サービスを再起動しています...")

    # Qtile 設定リロード
    result = subprocess.run(
        ["qtile", "cmd-obj", "-o", "cmd", "-f", "reload_config"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  Qtile: 設定をリロードしました")
    else:
        print(f"  [警告] Qtile リロード失敗: {result.stderr.strip()}")

    # Picom 再起動
    subprocess.run(["pkill", "-x", "picom"], capture_output=True)
    subprocess.Popen(["picom", "--daemon"])
    print("  Picom: 再起動しました")

    # Dunst 再起動
    subprocess.run(["pkill", "-x", "dunst"], capture_output=True)
    subprocess.Popen(["dunst"])
    print("  Dunst: 再起動しました")


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main() -> None:
    no_restart = "--no-restart" in sys.argv

    print(f"theme.json を読み込み中: {THEME_FILE}")
    cfg = load_theme()

    print("設定ファイルを更新しています...")
    apply_picom(cfg)
    apply_dunst(cfg)
    apply_rofi(cfg)

    if no_restart:
        print("完了（サービス再起動はスキップ）")
    else:
        restart_services()
        print("完了")


if __name__ == "__main__":
    main()

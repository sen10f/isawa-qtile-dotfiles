#!/usr/bin/env python3
"""
Qtile Config GUI
theme.json を編集して設定を視覚的に変更するツール
"""

import json
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget,
)

THEME_FILE   = Path(__file__).parent / "theme.json"
APPLY_SCRIPT = Path(__file__).parent / "apply_theme.py"

# ---------------------------------------------------------------------------
# Catppuccin Mocha プリセット
# ---------------------------------------------------------------------------

PRESETS = {
    "Catppuccin Mocha (デフォルト)": {
        "rosewater": "#f5e0dc", "flamingo": "#f2cdcd", "pink": "#f5c2e7",
        "mauve": "#cba6f7", "red": "#f38ba8", "maroon": "#eba0ac",
        "peach": "#fab387", "yellow": "#f9e2af", "green": "#a6e3a1",
        "teal": "#94e2d5", "sky": "#89dceb", "sapphire": "#74c7ec",
        "blue": "#89b4fa", "lavender": "#b4befe", "text": "#cdd6f4",
        "subtext1": "#bac2de", "subtext0": "#a6adc8", "overlay2": "#9399b2",
        "overlay1": "#7f849c", "overlay0": "#6c7086", "surface2": "#585b70",
        "surface1": "#45475a", "surface0": "#313244", "base": "#1e1e2e",
        "mantle": "#181825", "crust": "#11111b",
    },
    "Catppuccin Latte (ライト)": {
        "rosewater": "#dc8a78", "flamingo": "#dd7878", "pink": "#ea76cb",
        "mauve": "#8839ef", "red": "#d20f39", "maroon": "#e64553",
        "peach": "#fe640b", "yellow": "#df8e1d", "green": "#40a02b",
        "teal": "#179299", "sky": "#04a5e5", "sapphire": "#209fb5",
        "blue": "#1e66f5", "lavender": "#7287fd", "text": "#4c4f69",
        "subtext1": "#5c5f77", "subtext0": "#6c6f85", "overlay2": "#7c7f93",
        "overlay1": "#8c8fa1", "overlay0": "#9ca0b0", "surface2": "#acb0be",
        "surface1": "#bcc0cc", "surface0": "#ccd0da", "base": "#eff1f5",
        "mantle": "#e6e9ef", "crust": "#dce0e8",
    },
    "Catppuccin Frappé": {
        "rosewater": "#f2d5cf", "flamingo": "#eebebe", "pink": "#f4b8e4",
        "mauve": "#ca9ee6", "red": "#e78284", "maroon": "#ea999c",
        "peach": "#ef9f76", "yellow": "#e5c890", "green": "#a6d189",
        "teal": "#81c8be", "sky": "#99d1db", "sapphire": "#85c1dc",
        "blue": "#8caaee", "lavender": "#babbf1", "text": "#c6d0f5",
        "subtext1": "#b5bfe2", "subtext0": "#a5adce", "overlay2": "#949cbb",
        "overlay1": "#838ba7", "overlay0": "#737994", "surface2": "#626880",
        "surface1": "#51576d", "surface0": "#414559", "base": "#303446",
        "mantle": "#292c3c", "crust": "#232634",
    },
    "Catppuccin Macchiato": {
        "rosewater": "#f4dbd6", "flamingo": "#f0c6c6", "pink": "#f5bde6",
        "mauve": "#c6a0f6", "red": "#ed8796", "maroon": "#ee99a0",
        "peach": "#f5a97f", "yellow": "#eed49f", "green": "#a6da95",
        "teal": "#8bd5ca", "sky": "#91d7e3", "sapphire": "#7dc4e4",
        "blue": "#8aadf4", "lavender": "#b7bdf8", "text": "#cad3f5",
        "subtext1": "#b8c0e0", "subtext0": "#a5adcb", "overlay2": "#939ab7",
        "overlay1": "#8087a2", "overlay0": "#6e738d", "surface2": "#5b6078",
        "surface1": "#494d64", "surface0": "#363a4f", "base": "#24273a",
        "mantle": "#1e2030", "crust": "#181926",
    },
}

# ---------------------------------------------------------------------------
# QSS テーマ (Catppuccin Mocha)
# ---------------------------------------------------------------------------

QSS = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 8px 18px;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #cba6f7;
    border-bottom: 2px solid #cba6f7;
}
QTabBar::tab:hover:!selected {
    background-color: #45475a;
    color: #cdd6f4;
}
QGroupBox {
    border: 1px solid #313244;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    color: #cba6f7;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #cba6f7;
}
QPushButton:pressed {
    background-color: #585b70;
}
QPushButton#applyBtn {
    background-color: #cba6f7;
    color: #1e1e2e;
    font-weight: bold;
    border: none;
}
QPushButton#applyBtn:hover {
    background-color: #b4befe;
}
QPushButton#resetBtn {
    background-color: #313244;
    color: #f38ba8;
    border-color: #f38ba8;
}
QSlider::groove:horizontal {
    height: 6px;
    background-color: #313244;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background-color: #cba6f7;
    border: none;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background-color: #cba6f7;
    border-radius: 3px;
}
QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 3px 6px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #cba6f7;
}
QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #45475a;
    border-radius: 3px;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #cba6f7;
    border-color: #cba6f7;
}
QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}
QComboBox:focus {
    border-color: #cba6f7;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #585b70;
    border: 1px solid #45475a;
}
QScrollArea {
    border: none;
}
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #585b70;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #cba6f7;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}
QLabel#sectionLabel {
    color: #cba6f7;
    font-weight: bold;
    font-size: 14px;
}
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #313244;
}
"""

# ---------------------------------------------------------------------------
# カラーボタン ウィジェット
# ---------------------------------------------------------------------------

class ColorButton(QPushButton):
    """カラースウォッチ + クリックでカラーピッカーを開くボタン"""

    def __init__(self, hex_color: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_color(hex_color)
        self.clicked.connect(self._pick_color)

    def set_color(self, hex_color: str):
        self._color = hex_color
        self.setStyleSheet(
            f"background-color: {hex_color}; border: 2px solid #45475a;"
            f"border-radius: 4px;"
        )
        self.setToolTip(hex_color)

    def get_color(self) -> str:
        return self._color

    def _pick_color(self):
        initial = QColor(self._color)
        color = QColorDialog.getColor(initial, self, "色を選択")
        if color.isValid():
            self.set_color(color.name())


# ---------------------------------------------------------------------------
# スライダー + ラベル（連動）
# ---------------------------------------------------------------------------

def make_slider_row(min_val, max_val, value, step=1, is_float=False):
    """スライダーと値ラベルを横並びにしたウィジェットを返す"""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)

    if is_float:
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setSingleStep(step)
        spin.setDecimals(2)
        spin.setValue(value)
        spin.setFixedWidth(72)

        slider = QSlider(Qt.Orientation.Horizontal)
        factor = round(1 / step)
        slider.setRange(int(min_val * factor), int(max_val * factor))
        slider.setValue(int(value * factor))
        slider.valueChanged.connect(lambda v: spin.setValue(v / factor))
        spin.valueChanged.connect(lambda v: slider.setValue(int(v * factor)))
    else:
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setSingleStep(step)
        spin.setValue(value)
        spin.setFixedWidth(72)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(value)
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)

    layout.addWidget(slider, stretch=1)
    layout.addWidget(spin)
    return widget, spin


# ---------------------------------------------------------------------------
# apply_theme.py を別スレッドで実行するワーカー
# ---------------------------------------------------------------------------

class ApplyWorker(QThread):
    finished = pyqtSignal(int, str)  # returncode, stderr

    def __init__(self, script: Path):
        super().__init__()
        self._script = script

    def run(self):
        try:
            result = subprocess.run(
                [sys.executable, str(self._script)],
                capture_output=True, text=True,
                timeout=60
            )
            self.finished.emit(result.returncode, result.stderr)
        except subprocess.TimeoutExpired:
            self.finished.emit(1, "タイムアウト: apply_theme.py が60秒以内に完了しませんでした")
        except Exception as e:
            self.finished.emit(1, str(e))


def make_separator():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line


# ---------------------------------------------------------------------------
# メインウィンドウ
# ---------------------------------------------------------------------------

class QtileConfigGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.theme = json.loads(THEME_FILE.read_text())
        self._color_buttons: dict[str, ColorButton] = {}
        self._widgets: dict = {}  # key → spin/checkbox widget
        self._worker: ApplyWorker | None = None

        self.setWindowTitle("Qtile Config")
        self.setMinimumSize(780, 620)
        self.resize(860, 700)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(8)

        # タブ
        tabs = QTabWidget()
        tabs.addTab(self._build_tab_colors(),      "カラーテーマ")
        tabs.addTab(self._build_tab_layout(),      "レイアウト・バー")
        tabs.addTab(self._build_tab_scratchpad(),  "スクラッチパッド")
        tabs.addTab(self._build_tab_picom(),       "Picom エフェクト")
        tabs.addTab(self._build_tab_dunst(),       "通知 (Dunst)")
        root.addWidget(tabs)

        # 下部ボタン
        root.addWidget(make_separator())
        root.addLayout(self._build_bottom_bar())

        # ステータスバー
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("theme.json を読み込みました")

    # -----------------------------------------------------------------------
    # Tab 1: カラーテーマ
    # -----------------------------------------------------------------------

    def _build_tab_colors(self) -> QWidget:
        outer = QWidget()
        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(12, 12, 12, 12)

        # プリセット行
        preset_box = QGroupBox("プリセット")
        preset_lay = QHBoxLayout(preset_box)
        self._preset_combo = QComboBox()
        self._preset_combo.addItems(PRESETS.keys())
        apply_preset_btn = QPushButton("適用")
        apply_preset_btn.setFixedWidth(80)
        apply_preset_btn.clicked.connect(self._on_apply_preset)
        preset_lay.addWidget(self._preset_combo, stretch=1)
        preset_lay.addWidget(apply_preset_btn)
        vbox.addWidget(preset_box)

        # カラーグリッド（スクロール可能）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        grid = QGridLayout(scroll_widget)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        COLOR_GROUPS = [
            ("アクセントカラー", [
                "rosewater", "flamingo", "pink", "mauve",
                "red", "maroon", "peach", "yellow",
                "green", "teal", "sky", "sapphire",
                "blue", "lavender",
            ]),
            ("テキストカラー", [
                "text", "subtext1", "subtext0",
            ]),
            ("オーバーレイ", [
                "overlay2", "overlay1", "overlay0",
            ]),
            ("サーフェス・ベース", [
                "surface2", "surface1", "surface0",
                "base", "mantle", "crust",
            ]),
        ]

        row = 0
        for group_name, keys in COLOR_GROUPS:
            label = QLabel(group_name)
            label.setObjectName("sectionLabel")
            grid.addWidget(label, row, 0, 1, 4)
            row += 1
            for i, key in enumerate(keys):
                col_pair = (i % 2) * 2
                hex_val = self.theme["colors"].get(key, "#ffffff")
                name_label = QLabel(key)
                name_label.setFixedWidth(90)
                btn = ColorButton(hex_val)
                self._color_buttons[key] = btn
                grid.addWidget(name_label, row + i // 2, col_pair)
                grid.addWidget(btn,        row + i // 2, col_pair + 1)
            row += (len(keys) + 1) // 2 + 1

        vbox.addWidget(scroll, stretch=1)
        return outer

    def _on_apply_preset(self):
        preset_name = self._preset_combo.currentText()
        preset = PRESETS[preset_name]
        for key, btn in self._color_buttons.items():
            if key in preset:
                btn.set_color(preset[key])
        self.status.showMessage(f"プリセット '{preset_name}' を適用しました（未保存）")

    # -----------------------------------------------------------------------
    # Tab 2: レイアウト・バー
    # -----------------------------------------------------------------------

    def _build_tab_layout(self) -> QWidget:
        outer = QWidget()
        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        # レイアウト設定
        layout_box = QGroupBox("ウィンドウレイアウト")
        lg = QGridLayout(layout_box)
        lg.setColumnStretch(1, 1)

        bw_widget, self._widgets["layout.border_width"] = make_slider_row(
            0, 8, self.theme["layout"]["border_width"])
        margin_widget, self._widgets["layout.margin"] = make_slider_row(
            0, 32, self.theme["layout"]["margin"])

        lg.addWidget(QLabel("ウィンドウ枠の太さ"), 0, 0)
        lg.addWidget(bw_widget, 0, 1)
        lg.addWidget(QLabel("ウィンドウ間の隙間"), 1, 0)
        lg.addWidget(margin_widget, 1, 1)
        vbox.addWidget(layout_box)

        # バー設定
        bar_box = QGroupBox("ステータスバー")
        bg = QGridLayout(bar_box)
        bg.setColumnStretch(1, 1)

        h_widget, self._widgets["bar.height"] = make_slider_row(
            16, 48, self.theme["bar"]["height"])
        fs_widget, self._widgets["bar.fontsize"] = make_slider_row(
            8, 20, self.theme["bar"]["fontsize"])
        pad_widget, self._widgets["bar.padding"] = make_slider_row(
            0, 12, self.theme["bar"]["padding"])
        bb_widget, self._widgets["bar.border_bottom"] = make_slider_row(
            0, 8, self.theme["bar"]["border_bottom"])

        bg.addWidget(QLabel("バーの高さ"),        0, 0)
        bg.addWidget(h_widget,                    0, 1)
        bg.addWidget(QLabel("フォントサイズ"),      1, 0)
        bg.addWidget(fs_widget,                   1, 1)
        bg.addWidget(QLabel("ウィジェット余白"),    2, 0)
        bg.addWidget(pad_widget,                  2, 1)
        bg.addWidget(QLabel("下ボーダーの太さ"),   3, 0)
        bg.addWidget(bb_widget,                   3, 1)
        vbox.addWidget(bar_box)

        # Qtile 動作フラグ
        flags_box = QGroupBox("Qtile 動作設定")
        fl = QVBoxLayout(flags_box)
        FLAGS = [
            ("follow_mouse_focus",          "マウス移動でフォーカスを追う"),
            ("bring_front_click",           "クリックでウィンドウを前面に出す"),
            ("floats_kept_above",           "フローティングウィンドウを常に前面に保つ"),
            ("cursor_warp",                 "フォーカス変更時にカーソルを移動する"),
            ("auto_fullscreen",             "フルスクリーンを自動で有効にする"),
            ("auto_minimize",               "フォーカス喪失時に自動最小化"),
        ]
        for key, label_text in FLAGS:
            cb = QCheckBox(label_text)
            cb.setChecked(bool(self.theme.get(key, False)))
            self._widgets[f"flag.{key}"] = cb
            fl.addWidget(cb)
        vbox.addWidget(flags_box)
        vbox.addStretch()
        return outer

    # -----------------------------------------------------------------------
    # Tab 3: スクラッチパッド
    # -----------------------------------------------------------------------

    def _build_tab_scratchpad(self) -> QWidget:
        outer = QWidget()
        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        DROPDOWNS = [
            ("term",  "ターミナル (Mod+`)"),
            ("calc",  "電卓 (Mod+Shift+`)"),
            ("files", "ファイルマネージャー (Mod+Ctrl+`)"),
        ]
        for key, title in DROPDOWNS:
            box = QGroupBox(title)
            g = QGridLayout(box)
            g.setColumnStretch(1, 1)
            sc = self.theme["scratchpad"][key]

            w_widget, self._widgets[f"sc.{key}.width"]   = make_slider_row(0.1, 1.0, sc["width"],  0.05, True)
            h_widget, self._widgets[f"sc.{key}.height"]  = make_slider_row(0.1, 1.0, sc["height"], 0.05, True)
            x_widget, self._widgets[f"sc.{key}.x"]       = make_slider_row(0.0, 0.9, sc["x"],      0.05, True)
            y_widget, self._widgets[f"sc.{key}.y"]       = make_slider_row(0.0, 0.9, sc["y"],      0.05, True)
            op_widget, self._widgets[f"sc.{key}.opacity"] = make_slider_row(0.5, 1.0, sc["opacity"], 0.05, True)

            g.addWidget(QLabel("幅 (画面比率)"),     0, 0); g.addWidget(w_widget,  0, 1)
            g.addWidget(QLabel("高さ (画面比率)"),   1, 0); g.addWidget(h_widget,  1, 1)
            g.addWidget(QLabel("X位置"),             2, 0); g.addWidget(x_widget,  2, 1)
            g.addWidget(QLabel("Y位置"),             3, 0); g.addWidget(y_widget,  3, 1)
            g.addWidget(QLabel("透明度"),             4, 0); g.addWidget(op_widget, 4, 1)
            vbox.addWidget(box)

        vbox.addStretch()
        return outer

    # -----------------------------------------------------------------------
    # Tab 4: Picom
    # -----------------------------------------------------------------------

    def _build_tab_picom(self) -> QWidget:
        outer = QWidget()
        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        pc = self.theme["picom"]

        # シャドウ
        shadow_box = QGroupBox("シャドウ")
        sg = QGridLayout(shadow_box)
        sg.setColumnStretch(1, 1)

        r_widget, self._widgets["picom.shadow_radius"]  = make_slider_row(0, 30, pc["shadow_radius"])
        op_widget, self._widgets["picom.shadow_opacity"] = make_slider_row(0.0, 1.0, pc["shadow_opacity"], 0.05, True)
        ox_widget, self._widgets["picom.shadow_offset_x"] = make_slider_row(-30, 0, pc["shadow_offset_x"])
        oy_widget, self._widgets["picom.shadow_offset_y"] = make_slider_row(-30, 0, pc["shadow_offset_y"])

        sg.addWidget(QLabel("シャドウ半径"),    0, 0); sg.addWidget(r_widget,  0, 1)
        sg.addWidget(QLabel("シャドウ濃度"),    1, 0); sg.addWidget(op_widget, 1, 1)
        sg.addWidget(QLabel("X オフセット"),   2, 0); sg.addWidget(ox_widget, 2, 1)
        sg.addWidget(QLabel("Y オフセット"),   3, 0); sg.addWidget(oy_widget, 3, 1)
        vbox.addWidget(shadow_box)

        # フェード
        fade_box = QGroupBox("フェード (ウィンドウの開閉アニメーション)")
        fg_ = QGridLayout(fade_box)
        fg_.setColumnStretch(1, 1)

        fi_widget, self._widgets["picom.fade_in_step"]  = make_slider_row(0.01, 0.2, pc["fade_in_step"],  0.01, True)
        fo_widget, self._widgets["picom.fade_out_step"] = make_slider_row(0.01, 0.2, pc["fade_out_step"], 0.01, True)
        fd_widget, self._widgets["picom.fade_delta"]    = make_slider_row(1, 30, pc["fade_delta"])

        fg_.addWidget(QLabel("フェードイン速度"),  0, 0); fg_.addWidget(fi_widget, 0, 1)
        fg_.addWidget(QLabel("フェードアウト速度"), 1, 0); fg_.addWidget(fo_widget, 1, 1)
        fg_.addWidget(QLabel("フェード間隔 (ms)"), 2, 0); fg_.addWidget(fd_widget, 2, 1)
        vbox.addWidget(fade_box)

        # 透明度・ブラー
        misc_box = QGroupBox("透明度・ブラー")
        mg = QGridLayout(misc_box)
        mg.setColumnStretch(1, 1)

        iop_widget, self._widgets["picom.inactive_opacity"] = make_slider_row(0.5, 1.0, pc["inactive_opacity"], 0.05, True)
        bs_widget, self._widgets["picom.blur_strength"]     = make_slider_row(1, 20, pc["blur_strength"])
        blur_cb = QCheckBox("背景ブラーを有効にする")
        blur_cb.setChecked(pc["blur_background"])
        self._widgets["picom.blur_background"] = blur_cb

        mg.addWidget(QLabel("非アクティブ時の透明度"), 0, 0); mg.addWidget(iop_widget, 0, 1)
        mg.addWidget(QLabel("ブラー強度"),              1, 0); mg.addWidget(bs_widget,  1, 1)
        mg.addWidget(blur_cb, 2, 0, 1, 2)
        vbox.addWidget(misc_box)

        vbox.addStretch()
        return outer

    # -----------------------------------------------------------------------
    # Tab 5: Dunst 通知
    # -----------------------------------------------------------------------

    def _build_tab_dunst(self) -> QWidget:
        outer = QWidget()
        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        dc = self.theme["dunst"]

        # 見た目
        appear_box = QGroupBox("見た目")
        ag = QGridLayout(appear_box)
        ag.setColumnStretch(1, 1)

        cr_widget, self._widgets["dunst.corner_radius"]      = make_slider_row(0, 20, dc["corner_radius"])
        pad_widget, self._widgets["dunst.padding"]           = make_slider_row(0, 30, dc["padding"])
        hpad_widget, self._widgets["dunst.horizontal_padding"] = make_slider_row(0, 30, dc["horizontal_padding"])
        fw_widget, self._widgets["dunst.frame_width"]        = make_slider_row(0, 6, dc["frame_width"])

        fc_btn = ColorButton(dc["frame_color"])
        self._widgets["dunst.frame_color"] = fc_btn
        self._color_buttons["dunst.frame_color"] = fc_btn

        ag.addWidget(QLabel("角の丸み"),          0, 0); ag.addWidget(cr_widget,   0, 1)
        ag.addWidget(QLabel("上下の余白"),         1, 0); ag.addWidget(pad_widget,  1, 1)
        ag.addWidget(QLabel("左右の余白"),         2, 0); ag.addWidget(hpad_widget, 2, 1)
        ag.addWidget(QLabel("枠の太さ"),           3, 0); ag.addWidget(fw_widget,   3, 1)
        ag.addWidget(QLabel("枠の色 (グローバル)"), 4, 0); ag.addWidget(fc_btn,     4, 1)
        vbox.addWidget(appear_box)

        # Urgency別設定
        URGENCIES = [
            ("urgency_low",      "通知 低優先度"),
            ("urgency_normal",   "通知 通常"),
            ("urgency_critical", "通知 重要"),
        ]
        for urgency_key, title in URGENCIES:
            u = dc[urgency_key]
            box = QGroupBox(title)
            ug = QGridLayout(box)

            bg_btn = ColorButton(u["background"])
            fg_btn = ColorButton(u["foreground"])
            fc_btn2 = ColorButton(u["frame_color"])
            to_widget, self._widgets[f"dunst.{urgency_key}.timeout"] = make_slider_row(0, 30, u["timeout"])

            self._widgets[f"dunst.{urgency_key}.background"]  = bg_btn
            self._widgets[f"dunst.{urgency_key}.foreground"]  = fg_btn
            self._widgets[f"dunst.{urgency_key}.frame_color"] = fc_btn2

            ug.addWidget(QLabel("背景色"),       0, 0); ug.addWidget(bg_btn,    0, 1)
            ug.addWidget(QLabel("文字色"),       1, 0); ug.addWidget(fg_btn,    1, 1)
            ug.addWidget(QLabel("枠の色"),       2, 0); ug.addWidget(fc_btn2,   2, 1)
            ug.addWidget(QLabel("表示時間 (秒)"), 3, 0); ug.addWidget(to_widget, 3, 1)
            ug.setColumnStretch(1, 1)
            vbox.addWidget(box)

        vbox.addStretch()
        return outer

    # -----------------------------------------------------------------------
    # 下部ボタンバー
    # -----------------------------------------------------------------------

    def _build_bottom_bar(self) -> QHBoxLayout:
        hbox = QHBoxLayout()

        reset_btn = QPushButton("リセット")
        reset_btn.setObjectName("resetBtn")
        reset_btn.clicked.connect(self._on_reset)

        self._apply_btn = QPushButton("保存して適用")
        self._apply_btn.setObjectName("applyBtn")
        self._apply_btn.clicked.connect(self._on_apply)

        hbox.addWidget(reset_btn)
        hbox.addStretch()
        hbox.addWidget(self._apply_btn)
        return hbox

    # -----------------------------------------------------------------------
    # 保存・適用ロジック
    # -----------------------------------------------------------------------

    def _collect_values(self) -> dict:
        """GUIの現在値を theme dict に反映して返す"""
        theme = json.loads(json.dumps(self.theme))  # deep copy

        # カラー
        for key, btn in self._color_buttons.items():
            if "." in key:
                # dunst.frame_color 等
                parts = key.split(".")
                theme[parts[0]][parts[1]] = btn.get_color()
            else:
                theme["colors"][key] = btn.get_color()

        # スピンボックス / チェックボックス / _widgets 内のカラーボタン
        for key, widget in self._widgets.items():
            parts = key.split(".")

            if isinstance(widget, ColorButton):
                # urgency別など _color_buttons に登録されていないカラーボタン
                val = widget.get_color()
                if parts[0] == "dunst":
                    if len(parts) == 3:
                        theme["dunst"][parts[1]][parts[2]] = val
                    else:
                        theme["dunst"][parts[1]] = val

            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                val = widget.value()
                if parts[0] == "layout":
                    theme["layout"][parts[1]] = val
                elif parts[0] == "bar":
                    theme["bar"][parts[1]] = val
                elif parts[0] == "sc":
                    theme["scratchpad"][parts[1]][parts[2]] = val
                elif parts[0] == "picom":
                    theme["picom"][parts[1]] = val
                elif parts[0] == "dunst":
                    if len(parts) == 2:
                        theme["dunst"][parts[1]] = val
                    else:
                        theme["dunst"][parts[1]][parts[2]] = val

            elif isinstance(widget, QCheckBox):
                val = widget.isChecked()
                if parts[0] == "flag":
                    theme[parts[1]] = val
                elif parts[0] == "picom":
                    theme["picom"][parts[1]] = val

        return theme

    def _on_apply(self):
        theme = self._collect_values()

        # theme.json を保存
        THEME_FILE.write_text(
            json.dumps(theme, indent=2, ensure_ascii=False)
        )
        self.theme = theme

        # ボタンを無効化してフリーズを防ぐ
        self._apply_btn.setEnabled(False)
        self._apply_btn.setText("適用中...")
        self.status.showMessage("theme.json を保存しました。適用中...")

        # apply_theme.py を別スレッドで実行
        self._worker = ApplyWorker(APPLY_SCRIPT)
        self._worker.finished.connect(self._on_apply_done)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_apply_done(self, returncode: int, stderr: str):
        self._worker = None
        self._apply_btn.setEnabled(True)
        self._apply_btn.setText("保存して適用")

        if returncode == 0:
            self.status.showMessage("適用完了！")
        else:
            error_msg = stderr.strip() or "不明なエラー（終了コード: {returncode}）"
            QMessageBox.warning(
                self, "適用エラー",
                f"apply_theme.py でエラーが発生しました:\n{error_msg}"
            )
            self.status.showMessage(f"エラー (code={returncode})")

    def _on_reset(self):
        reply = QMessageBox.question(
            self, "リセット確認",
            "現在の theme.json の値に戻しますか？\n（未保存の変更は失われます）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.theme = json.loads(THEME_FILE.read_text())
            # カラーボタンをリセット
            for key, btn in self._color_buttons.items():
                if "." in key:
                    parts = key.split(".")
                    btn.set_color(self.theme[parts[0]][parts[1]])
                else:
                    btn.set_color(self.theme["colors"].get(key, "#ffffff"))
            # _widgets 内のウィジェットをリセット
            for key, widget in self._widgets.items():
                parts = key.split(".")

                if isinstance(widget, ColorButton):
                    if parts[0] == "dunst":
                        if len(parts) == 3:
                            widget.set_color(self.theme["dunst"][parts[1]][parts[2]])
                        else:
                            widget.set_color(self.theme["dunst"][parts[1]])

                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    if parts[0] == "layout":
                        widget.setValue(self.theme["layout"][parts[1]])
                    elif parts[0] == "bar":
                        widget.setValue(self.theme["bar"][parts[1]])
                    elif parts[0] == "sc":
                        widget.setValue(self.theme["scratchpad"][parts[1]][parts[2]])
                    elif parts[0] == "picom":
                        widget.setValue(self.theme["picom"][parts[1]])
                    elif parts[0] == "dunst":
                        if len(parts) == 2:
                            widget.setValue(self.theme["dunst"][parts[1]])
                        else:
                            widget.setValue(self.theme["dunst"][parts[1]][parts[2]])
            self.status.showMessage("リセットしました")


# ---------------------------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setApplicationName("Qtile Config")

    window = QtileConfigGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

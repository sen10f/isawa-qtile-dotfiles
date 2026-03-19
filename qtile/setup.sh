#!/bin/bash
#
# Qtile環境セットアップスクリプト
# 使用方法: bash ~/.config/qtile/setup.sh
#

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                        Qtile環境セットアップスクリプト                          ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# パッケージのインストール確認関数
install_if_missing() {
    local package=$1
    if ! dpkg -l | grep -q "^ii  $package "; then
        log_info "Installing $package..."
        sudo apt install -y "$package"
        log_success "$package installed"
    else
        log_info "$package is already installed"
    fi
}

echo ""
log_info "システムのアップデート確認中..."
sudo apt update

echo ""
log_info "必要なパッケージをインストール中..."
echo ""

# 基本ツール
install_if_missing "rofi"
install_if_missing "arandr"
install_if_missing "pavucontrol"

# システムサービス
install_if_missing "i3lock"
install_if_missing "xss-lock"
install_if_missing "policykit-1-gnome"
install_if_missing "xsettingsd"

# メディア・明るさ制御
install_if_missing "playerctl"
install_if_missing "brightnessctl"

# ユーティリティ
install_if_missing "picom"
install_if_missing "dunst"
install_if_missing "flameshot"
install_if_missing "dex"

# クリップボードマネージャー (copyq or parcellite)
if ! dpkg -l | grep -q "^ii  copyq " && ! dpkg -l | grep -q "^ii  parcellite "; then
    log_info "Installing clipboard manager..."
    install_if_missing "copyq"
fi

# 壁紙設定
install_if_missing "nitrogen"

# スクラッチパッド用アプリ
install_if_missing "qalculate-gtk"

# Qt関連
install_if_missing "qt5-style-plugins"

# Qtile Config GUI
install_if_missing "python3-pyqt6"

echo ""
log_success "すべてのパッケージがインストールされました！"

echo ""
log_info "クリップボードマネージャーの設定..."
if dpkg -l | grep -q "^ii  copyq "; then
    log_info "CopyQを使用します (Mod+cで起動)"
    # clipmenu -> copyq に設定を更新
    if grep -q "clipmenu" ~/.config/qtile/config.py; then
        sed -i 's/clipmenu/copyq show/g' ~/.config/qtile/config.py
        sed -i 's/clipmenud/copyq/g' ~/.config/qtile/config.py
        log_success "config.pyをCopyQ用に更新しました"
    fi
elif dpkg -l | grep -q "^ii  parcellite "; then
    log_info "Parcelliteを使用します"
    if grep -q "clipmenu" ~/.config/qtile/config.py; then
        sed -i 's/clipmenu/parcellite/g' ~/.config/qtile/config.py
        sed -i 's/clipmenud/parcellite/g' ~/.config/qtile/config.py
        log_success "config.pyをParcellite用に更新しました"
    fi
fi

echo ""
log_info "ダークテーマの設定を適用中..."
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
gsettings set org.gnome.desktop.interface gtk-theme 'Yaru-bark-dark'
log_success "ダークテーマが設定されました"

echo ""
log_info "Qtile設定ファイルの構文チェック中..."
if python3 -m py_compile ~/.config/qtile/config.py; then
    log_success "設定ファイルに構文エラーはありません"
else
    log_error "設定ファイルに構文エラーがあります"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                           セットアップ完了！                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
log_info "次のステップ:"
echo "  1. Qtileを再起動してください:"
echo "     qtile cmd-obj -o cmd -f restart"
echo ""
echo "  2. または、ログアウトして再度ログインしてください"
echo ""
echo "  3. チートシートを表示: Mod+? (Mod = Windowsキー)"
echo ""
log_success "すべてのセットアップが完了しました！"

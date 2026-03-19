#!/usr/bin/env bash
# =============================================================================
# isawa-qtile-dotfiles セットアップスクリプト
# Qtile + デスクトップ環境を新しいマシンに一括インストールする
#
# 使い方:
#   git clone https://github.com/sen10f/isawa-qtile-dotfiles.git
#   cd isawa-qtile-dotfiles
#   bash setup.sh
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# 定数・色定義
# -----------------------------------------------------------------------------

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QTILE_VERSION="0.34.0"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# -----------------------------------------------------------------------------
# ログ関数
# -----------------------------------------------------------------------------

info()    { echo -e "${BLUE}[INFO]${NC}    $*"; }
success() { echo -e "${GREEN}[OK]${NC}      $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}    $*"; }
error()   { echo -e "${RED}[ERROR]${NC}   $*"; }
step()    { echo -e "\n${BOLD}${CYAN}▶ $*${NC}"; }
die()     { error "$*"; exit 1; }

header() {
    echo ""
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    printf "${BOLD}${CYAN}║${NC}  %-60s${BOLD}${CYAN}║${NC}\n" "$*"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# -----------------------------------------------------------------------------
# ユーティリティ
# -----------------------------------------------------------------------------

# コマンドが存在するか確認
has_cmd() { command -v "$1" &>/dev/null; }

# パッケージがインストール済みか確認
pkg_installed() { dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"; }

# aptパッケージを未インストールの場合のみインストール
apt_install() {
    local pkg="$1"
    if pkg_installed "$pkg"; then
        info "$pkg は導入済みです"
    else
        info "$pkg をインストール中..."
        sudo apt-get install -y "$pkg"
        success "$pkg をインストールしました"
    fi
}

# ファイルをバックアップしてからコピー
safe_copy() {
    local src="$1"
    local dst="$2"
    if [ -e "$dst" ] && ! [ -L "$dst" ]; then
        cp -a "$dst" "${dst}.bak.$(date +%Y%m%d_%H%M%S)"
        info "既存ファイルをバックアップ: ${dst}.bak.*"
    fi
    cp -a "$src" "$dst"
}

# ディレクトリをバックアップしてからコピー
safe_copy_dir() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -d "$dst" ] && ! [ -L "$dst" ]; then
        local bak="${dst}.bak.$(date +%Y%m%d_%H%M%S)"
        mv "$dst" "$bak"
        info "既存ディレクトリをバックアップ: $bak"
    fi
    cp -a "$src" "$dst"
}

# インタラクティブに確認
confirm() {
    local prompt="$1"
    local default="${2:-y}"
    local yn
    if [ "$default" = "y" ]; then
        read -r -p "$(echo -e "${YELLOW}?${NC} $prompt [Y/n] ")" yn
        yn="${yn:-y}"
    else
        read -r -p "$(echo -e "${YELLOW}?${NC} $prompt [y/N] ")" yn
        yn="${yn:-n}"
    fi
    [[ "$yn" =~ ^[Yy]$ ]]
}

# -----------------------------------------------------------------------------
# 前提条件チェック
# -----------------------------------------------------------------------------

check_prerequisites() {
    step "前提条件を確認中"

    # rootで実行していないか確認
    [ "$(id -u)" -ne 0 ] || die "rootユーザーで実行しないでください。sudoが使えるユーザーで実行してください。"

    # sudoが使えるか確認
    sudo -v 2>/dev/null || die "sudo 権限が必要です。"

    # Ubuntu/Debian系か確認
    has_cmd apt-get || die "このスクリプトはapt-get (Debian/Ubuntu) が必要です。"

    # Python3が使えるか確認
    has_cmd python3 || die "python3 が必要です: sudo apt-get install python3"

    # Pythonバージョン確認 (3.10+)
    local pyver
    pyver=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" \
        || die "Python 3.10 以上が必要です (現在: $pyver)"

    success "前提条件 OK (Python $pyver)"
}

# -----------------------------------------------------------------------------
# Step 1: システムパッケージ
# -----------------------------------------------------------------------------

install_system_packages() {
    step "システムパッケージをインストール中"

    info "パッケージリストを更新中..."
    sudo apt-get update -q

    # ── Xorg 基盤 ────────────────────────────────────────────────────────────
    info "--- Xorg 基盤 ---"
    apt_install "xorg"
    apt_install "xserver-xorg"
    apt_install "xinit"
    apt_install "x11-xserver-utils"   # xrandr, xsetroot 等
    apt_install "x11-utils"           # xprop 等

    # ── ウィンドウマネージャー依存 ────────────────────────────────────────────
    info "--- WM 依存パッケージ ---"
    apt_install "python3-pip"
    apt_install "python3-xcb"
    apt_install "python3-cairocffi"
    apt_install "libpangocairo-1.0-0"
    apt_install "libxcb-cursor0"

    # pipx (Qtileのインストールに使用)
    if ! has_cmd pipx; then
        info "pipx をインストール中..."
        sudo apt-get install -y pipx
        pipx ensurepath
        export PATH="$HOME/.local/bin:$PATH"
        success "pipx をインストールしました"
    else
        info "pipx は導入済みです"
    fi

    # ── コンポジター・通知 ────────────────────────────────────────────────────
    info "--- コンポジター・通知 ---"
    apt_install "picom"
    apt_install "dunst"
    apt_install "libnotify-bin"

    # ── ランチャー・壁紙・ロック ──────────────────────────────────────────────
    info "--- ランチャー・壁紙・ロック ---"
    apt_install "rofi"
    apt_install "nitrogen"
    apt_install "i3lock"
    apt_install "xss-lock"

    # ── システムトレイ・デーモン ──────────────────────────────────────────────
    info "--- システムトレイ・デーモン ---"
    apt_install "network-manager-gnome"   # nm-applet
    apt_install "blueman"
    apt_install "dex"
    apt_install "xsettingsd"

    # ── オーディオ・メディア ──────────────────────────────────────────────────
    info "--- オーディオ・メディア ---"
    apt_install "pipewire"
    apt_install "wireplumber"
    apt_install "pavucontrol"
    apt_install "playerctl"

    # ── 画面・電源管理 ────────────────────────────────────────────────────────
    info "--- 画面・電源管理 ---"
    apt_install "arandr"
    apt_install "brightnessctl"
    apt_install "xfce4-power-manager"

    # ── スクリーンショット・クリップボード ────────────────────────────────────
    info "--- スクリーンショット・クリップボード ---"
    apt_install "flameshot"
    apt_install "imagemagick"           # i3lockのブラーウォールペーパー
    apt_install "xclip"
    apt_install "copyq"

    # ── スクラッチパッド用アプリ ──────────────────────────────────────────────
    info "--- スクラッチパッド ---"
    apt_install "qalculate-gtk"

    # ── 日本語入力 ────────────────────────────────────────────────────────────
    info "--- 日本語入力 (fcitx5) ---"
    apt_install "fcitx5"
    apt_install "fcitx5-mozc"
    apt_install "fcitx5-config-qt"

    # ── テーマ・フォント ──────────────────────────────────────────────────────
    info "--- テーマ・フォント ---"
    apt_install "yaru-theme-gtk"         # Yaru-bark-dark (Ubuntuデフォルト)
    apt_install "fonts-noto-cjk"         # 日本語フォント
    apt_install "fonts-font-awesome"     # アイコンフォント
    apt_install "policykit-1-gnome"      # PolKit 認証エージェント

    # ── GUI ツール (Qtile Config GUI) ─────────────────────────────────────────
    info "--- GUI ツール ---"
    apt_install "python3-pyqt6"

    success "システムパッケージのインストール完了"
}

# -----------------------------------------------------------------------------
# Step 2: Qtile (pipx)
# -----------------------------------------------------------------------------

install_qtile() {
    step "Qtile をインストール中"

    export PATH="$HOME/.local/bin:$PATH"

    if has_cmd qtile; then
        local installed_ver
        installed_ver=$(qtile --version 2>/dev/null || echo "不明")
        info "Qtile は導入済みです ($installed_ver)"
        if confirm "Qtile を最新版に更新しますか？" "n"; then
            pipx upgrade qtile
            success "Qtile を更新しました"
        fi
    else
        info "Qtile $QTILE_VERSION をインストール中..."
        pipx install "qtile==$QTILE_VERSION"
        success "Qtile $QTILE_VERSION をインストールしました"
    fi

    # psutil (CPU ウィジェット用)
    info "psutil を注入中 (CPU ウィジェット用)..."
    pipx inject qtile psutil 2>/dev/null && success "psutil OK" || warn "psutil の注入に失敗しました (CPU ウィジェットが使えません)"

    # xsession ファイルを作成 (ディスプレイマネージャー登録)
    local xsession_dir="/usr/share/xsessions"
    local xsession_file="$xsession_dir/qtile.desktop"
    if ! [ -f "$xsession_file" ]; then
        info "Qtile xsession ファイルを作成中..."
        sudo tee "$xsession_file" > /dev/null <<EOF
[Desktop Entry]
Name=Qtile
Comment=Qtile Session
Exec=$HOME/.local/bin/qtile start
Type=Application
Keywords=wm;tiling
EOF
        success "xsession ファイルを作成しました: $xsession_file"
    else
        info "xsession ファイルは既に存在します: $xsession_file"
    fi
}

# -----------------------------------------------------------------------------
# Step 3: dotfiles のコピー
# -----------------------------------------------------------------------------

install_dotfiles() {
    step "設定ファイルをコピー中"

    local config_dir="$HOME/.config"
    mkdir -p "$config_dir"

    # Qtile
    info "Qtile 設定をコピー中..."
    if [ -d "$config_dir/qtile" ]; then
        if confirm "~/.config/qtile が既に存在します。上書きしますか？"; then
            safe_copy_dir "$REPO_DIR/qtile" "$config_dir/qtile"
            success "~/.config/qtile をコピーしました"
        else
            warn "Qtile 設定のコピーをスキップしました"
        fi
    else
        cp -a "$REPO_DIR/qtile" "$config_dir/qtile"
        success "~/.config/qtile をコピーしました"
    fi

    # Picom
    info "Picom 設定をコピー中..."
    mkdir -p "$config_dir/picom"
    safe_copy "$REPO_DIR/picom/picom.conf" "$config_dir/picom/picom.conf"
    success "~/.config/picom/picom.conf をコピーしました"

    # Dunst
    info "Dunst 設定をコピー中..."
    mkdir -p "$config_dir/dunst"
    safe_copy "$REPO_DIR/dunst/dunstrc" "$config_dir/dunst/dunstrc"
    success "~/.config/dunst/dunstrc をコピーしました"

    # Rofi
    info "Rofi 設定をコピー中..."
    mkdir -p "$config_dir/rofi"
    for f in "$REPO_DIR/rofi/"*; do
        safe_copy "$f" "$config_dir/rofi/$(basename "$f")"
    done
    success "~/.config/rofi をコピーしました"

    # Nitrogen (壁紙設定 - 任意)
    if [ -d "$REPO_DIR/nitrogen" ] && confirm "Nitrogen の壁紙設定もコピーしますか？ (既存の壁紙設定が上書きされます)" "n"; then
        mkdir -p "$config_dir/nitrogen"
        for f in "$REPO_DIR/nitrogen/"*; do
            safe_copy "$f" "$config_dir/nitrogen/$(basename "$f")"
        done
        success "~/.config/nitrogen をコピーしました"
    fi

    # スクリプトに実行権限を付与
    info "スクリプトに実行権限を付与中..."
    chmod +x "$config_dir/qtile/"*.sh 2>/dev/null || true
    chmod +x "$config_dir/qtile/"*.py 2>/dev/null || true
    success "実行権限を付与しました"
}

# -----------------------------------------------------------------------------
# Step 4: GUI アプリ登録 (.desktop ファイル)
# -----------------------------------------------------------------------------

install_desktop_entry() {
    step "GUI アプリをシステムに登録中"

    local apps_dir="$HOME/.local/share/applications"
    mkdir -p "$apps_dir"

    # Qtile Config GUI
    cat > "$apps_dir/qtile-config.desktop" <<EOF
[Desktop Entry]
Name=Qtile Config
GenericName=Window Manager Settings
Comment=Qtile デスクトップ環境の設定ツール
Exec=python3 $HOME/.config/qtile/qtile-config-gui.py
Icon=preferences-desktop
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;
StartupNotify=true
EOF
    success ".desktop ファイルを作成しました: $apps_dir/qtile-config.desktop"

    # デスクトップデータベースを更新
    has_cmd update-desktop-database && update-desktop-database "$apps_dir" 2>/dev/null || true
}

# -----------------------------------------------------------------------------
# Step 5: fcitx5 の環境変数設定
# -----------------------------------------------------------------------------

configure_fcitx5() {
    step "fcitx5 の環境変数を設定中"

    local profile="$HOME/.profile"
    local fcitx_env="
# fcitx5 - 日本語入力
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx"

    if grep -q "fcitx" "$profile" 2>/dev/null; then
        info "fcitx5 環境変数は ~/.profile に既に設定されています"
    else
        echo "$fcitx_env" >> "$profile"
        success "fcitx5 環境変数を ~/.profile に追加しました"
    fi

    # /etc/environment にも設定 (ディスプレイマネージャー経由での起動時に有効)
    if ! grep -q "GTK_IM_MODULE" /etc/environment 2>/dev/null; then
        if confirm "/etc/environment に fcitx5 環境変数を追加しますか？ (ログイン画面からのセッションでも有効になります)"; then
            sudo tee -a /etc/environment > /dev/null <<'EOF'
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
EOF
            success "/etc/environment に fcitx5 設定を追加しました"
        fi
    else
        info "fcitx5 設定は /etc/environment に既に存在します"
    fi
}

# -----------------------------------------------------------------------------
# Step 6: テーマ適用 (apply_theme.py)
# -----------------------------------------------------------------------------

apply_theme() {
    step "テーマを適用中 (picom/dunst/rofi)"

    local apply_script="$HOME/.config/qtile/apply_theme.py"
    if [ -f "$apply_script" ]; then
        info "apply_theme.py を実行中..."
        python3 "$apply_script" && success "テーマを適用しました" \
            || warn "テーマの適用中にエラーが発生しました (後で手動で実行してください)"
    else
        warn "apply_theme.py が見つかりません。スキップします。"
    fi
}

# -----------------------------------------------------------------------------
# Step 7: 設定の構文チェック
# -----------------------------------------------------------------------------

verify_config() {
    step "Qtile 設定ファイルの構文チェック"

    local config="$HOME/.config/qtile/config.py"
    if python3 -m py_compile "$config" 2>/dev/null; then
        success "config.py に構文エラーはありません"
    else
        error "config.py に構文エラーがあります:"
        python3 -m py_compile "$config"
    fi
}

# -----------------------------------------------------------------------------
# Step 8: ユーザー固有の設定について案内
# -----------------------------------------------------------------------------

show_user_specific_notice() {
    step "ユーザー固有の設定について"

    warn "以下の設定はマシン固有のため、手動で編集が必要です:"
    echo ""
    echo -e "  ${BOLD}~/.config/qtile/settings/hooks.py${NC}"
    echo "    → xrandr の設定 (DP-4, HDMI-0 等のディスプレイ名・解像度・リフレッシュレート)"
    echo "    → 使用するアプリの autostart リスト (nextcloud, amazon-music等)"
    echo ""
    echo -e "  ${BOLD}確認コマンド:${NC}"
    echo "    xrandr --listmonitors   # 接続中のディスプレイ名を確認"
    echo "    xrandr                  # 利用可能なモードを確認"
    echo ""
}

# -----------------------------------------------------------------------------
# 完了メッセージ
# -----------------------------------------------------------------------------

show_completion() {
    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║  セットアップ完了！                                          ║${NC}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}次のステップ:${NC}"
    echo ""
    echo "  1. ログアウトして、ディスプレイマネージャーで"
    echo "     「Qtile」セッションを選択してログインしてください"
    echo ""
    echo "  2. 初回起動後、以下で設定を確認してください:"
    echo "     Mod + Shift + C    → 設定リロード"
    echo "     Mod + /            → キーバインド一覧 (チートシート)"
    echo "     Mod + Space        → Qtile メニュー"
    echo ""
    echo "  3. 設定 GUI を開く:"
    echo "     python3 ~/.config/qtile/qtile-config-gui.py"
    echo "     または アプリランチャーから「Qtile Config」を検索"
    echo ""
    echo "  4. マシン固有の設定 (xrandr等) を確認:"
    echo "     $HOME/.config/qtile/settings/hooks.py"
    echo ""
    echo -e "${CYAN}  Mod = Super (Windows) キー${NC}"
    echo ""
}

# -----------------------------------------------------------------------------
# メイン処理
# -----------------------------------------------------------------------------

main() {
    header "isawa-qtile-dotfiles セットアップスクリプト"

    info "リポジトリ: $REPO_DIR"
    info "インストール先: $HOME/.config/"
    echo ""

    check_prerequisites
    install_system_packages
    install_qtile
    install_dotfiles
    install_desktop_entry
    configure_fcitx5
    apply_theme
    verify_config
    show_user_specific_notice
    show_completion
}

main "$@"

#!/bin/bash
#
# Qtile メインメニュー
# すべての主要機能にアクセスできるランチャー
#

# カテゴリ選択
CATEGORY=$(echo -e "🚀 アプリケーション\n⚙️  システム設定\n📋 スクラッチパッド\n🪟  ウィンドウ操作\n🔒 システム操作\n📖 ヘルプ" | rofi -dmenu -i -p "Qtile メニュー" -theme-str 'window {width: 400px;}')

case "$CATEGORY" in
    "🚀 アプリケーション")
        APP=$(echo -e "🌐 ブラウザ\n📁 ファイルマネージャー\n📝 テキストエディタ\n🎵 音楽プレイヤー\n🎨 画像ビューアー\n⚙️  すべてのアプリ" | rofi -dmenu -i -p "アプリケーション")
        case "$APP" in
            "🌐 ブラウザ") vivaldi &;;
            "📁 ファイルマネージャー") nautilus &;;
            "📝 テキストエディタ") gedit &;;
            "🎵 音楽プレイヤー") rhythmbox &;;
            "🎨 画像ビューアー") eog &;;
            "⚙️  すべてのアプリ") rofi -show drun &;;
        esac
        ;;

    "⚙️  システム設定")
        SETTING=$(echo -e "🖥️  ディスプレイ設定\n🔊 オーディオ設定\n🖼️  壁紙設定\n🎨 テーマ設定\n⌨️  キーボード設定\n🖱️  マウス設定" | rofi -dmenu -i -p "システム設定")
        case "$SETTING" in
            "🖥️  ディスプレイ設定") arandr &;;
            "🔊 オーディオ設定") pavucontrol &;;
            "🖼️  壁紙設定") nitrogen &;;
            "🎨 テーマ設定") lxappearance &;;
            "⌨️  キーボード設定") gnome-control-center keyboard &;;
            "🖱️  マウス設定") gnome-control-center mouse &;;
        esac
        ;;

    "📋 スクラッチパッド")
        SCRATCH=$(echo -e "💻 ターミナル\n🔢 電卓\n📁 ファイルマネージャー" | rofi -dmenu -i -p "スクラッチパッド")
        case "$SCRATCH" in
            "💻 ターミナル") qtile cmd-obj -o group scratchpad -f dropdown_toggle -a term;;
            "🔢 電卓") qtile cmd-obj -o group scratchpad -f dropdown_toggle -a calc;;
            "📁 ファイルマネージャー") qtile cmd-obj -o group scratchpad -f dropdown_toggle -a files;;
        esac
        ;;

    "🪟  ウィンドウ操作")
        WINDOW=$(echo -e "📸 スクリーンショット（選択）\n📸 スクリーンショット（全画面）\n🔲 フローティング切り替え\n⛶  フルスクリーン切り替え\n📋 クリップボード履歴\n🔍 ワークスペースプレビュー" | rofi -dmenu -i -p "ウィンドウ操作")
        case "$WINDOW" in
            "📸 スクリーンショット（選択）") flameshot gui &;;
            "📸 スクリーンショット（全画面）") flameshot full &;;
            "🔲 フローティング切り替え") qtile cmd-obj -o window -f toggle_floating;;
            "⛶  フルスクリーン切り替え") qtile cmd-obj -o window -f toggle_fullscreen;;
            "📋 クリップボード履歴") copyq show &;;
            "🔍 ワークスペースプレビュー")
                TERMINAL=$(qtile cmd-obj -o cmd -f eval -a "qtile.config.terminal" 2>/dev/null | grep -o '".*"' | tr -d '"')
                ${TERMINAL:-kitty} --title 'Workspace Preview' -e python3 ~/.config/qtile/workspace-preview.py &
                ;;
        esac
        ;;

    "🔒 システム操作")
        SYSTEM=$(echo -e "🔒 スクリーンロック\n🔄 Qtile再起動\n⚙️  設定リロード\n🚪 ログアウト\n⏻  電源メニュー" | rofi -dmenu -i -p "システム操作")
        case "$SYSTEM" in
            "🔒 スクリーンロック") i3lock -c 000000 &;;
            "🔄 Qtile再起動") qtile cmd-obj -o cmd -f restart;;
            "⚙️  設定リロード") qtile cmd-obj -o cmd -f reload_config;;
            "🚪 ログアウト") qtile cmd-obj -o cmd -f shutdown;;
            "⏻  電源メニュー")
                POWER=$(echo -e "🔌 シャットダウン\n🔄 再起動\n💤 サスペンド\n🔒 ロック" | rofi -dmenu -i -p "電源")
                case "$POWER" in
                    "🔌 シャットダウン") systemctl poweroff;;
                    "🔄 再起動") systemctl reboot;;
                    "💤 サスペンド") systemctl suspend;;
                    "🔒 ロック") i3lock -c 000000 &;;
                esac
                ;;
        esac
        ;;

    "📖 ヘルプ")
        HELP=$(echo -e "📋 チートシート\n⌨️  キーバインド一覧\n❓ Qtileについて" | rofi -dmenu -i -p "ヘルプ")
        case "$HELP" in
            "📋 チートシート")
                TERMINAL=$(qtile cmd-obj -o cmd -f eval -a "qtile.config.terminal" 2>/dev/null | grep -o '".*"' | tr -d '"')
                ${TERMINAL:-kitty} --title 'Qtile Cheatsheet' -e less ~/.config/qtile/cheatsheet.txt &
                ;;
            "⌨️  キーバインド一覧")
                qtile cmd-obj -o cmd -f display_kb > /tmp/qtile-kb.txt
                TERMINAL=$(qtile cmd-obj -o cmd -f eval -a "qtile.config.terminal" 2>/dev/null | grep -o '".*"' | tr -d '"')
                ${TERMINAL:-kitty} --title 'Keybindings' -e less /tmp/qtile-kb.txt &
                ;;
            "❓ Qtileについて")
                notify-send "Qtile" "Version: $(qtile --version)\nConfig: ~/.config/qtile/config.py" -i dialog-information
                ;;
        esac
        ;;
esac

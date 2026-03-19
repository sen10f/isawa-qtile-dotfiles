#!/bin/bash
# Qtile Power Menu

options="ログアウト\nサスペンド\n再起動\nシャットダウン"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "電源メニュー" -theme-str 'window {width: 300px;}')

case "$chosen" in
    "ログアウト")
        qtile cmd-obj -o cmd -f shutdown
        ;;
    "サスペンド")
        systemctl suspend
        ;;
    "再起動")
        systemctl reboot
        ;;
    "シャットダウン")
        systemctl poweroff
        ;;
esac

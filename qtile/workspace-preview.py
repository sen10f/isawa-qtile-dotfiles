#!/usr/bin/env python3
"""
Qtile Workspace Preview with Rofi Integration
Shows a preview of all workspaces and allows quick switching
"""

import subprocess
import json
import sys

def get_workspace_info():
    """Get information about all workspaces using bulk API"""
    try:
        # Get all groups info in a single API call
        result = subprocess.run(
            ['qtile', 'cmd-obj', '-o', 'cmd', '-f', 'get_groups'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None

        all_groups = json.loads(result.stdout)

        # Get current screen to determine current group
        screen_result = subprocess.run(
            ['qtile', 'cmd-obj', '-o', 'screen', '-f', 'info'],
            capture_output=True,
            text=True
        )

        current_screen_index = None
        if screen_result.returncode == 0:
            screen_info = json.loads(screen_result.stdout)
            current_screen_index = screen_info.get('index', None)

        workspace_data = []

        # Process groups 1-9 (exclude scratchpad)
        for group_num in range(1, 10):
            group_name = str(group_num)

            if group_name not in all_groups:
                continue

            group_info = all_groups[group_name]
            windows = group_info.get('windows', [])
            screen = group_info.get('screen', None)
            is_current = (screen == current_screen_index) if current_screen_index is not None else False

            workspace_data.append({
                'name': group_name,
                'windows': windows,
                'screen': screen,
                'is_current': is_current
            })

        return workspace_data
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def format_for_rofi(workspace_data):
    """Format workspace information for Rofi display"""
    lines = []

    for ws in workspace_data:
        # Status indicator
        status = "●" if ws['is_current'] else "○"

        # Window count
        window_count = len(ws['windows'])
        if window_count == 0:
            count_str = "[empty]"
        elif window_count == 1:
            count_str = "[1 window]"
        else:
            count_str = f"[{window_count} windows]"

        # Window names (truncated)
        if ws['windows']:
            # Take first 3 windows and join with comma, filter out None values
            window_names = [w for w in ws['windows'][:3] if w is not None]
            if window_names:
                windows_str = ", ".join(window_names)
                # Truncate if too long
                if len(windows_str) > 60:
                    windows_str = windows_str[:57] + "..."
            else:
                windows_str = ""
        else:
            windows_str = ""

        # Format: "● 1 [3 windows] Firefox, Terminal, VSCode"
        line = f"{status} {ws['name']} {count_str}"
        if windows_str:
            line += f" {windows_str}"

        lines.append(line)

    return "\n".join(lines)

def switch_workspace(workspace_num):
    """Switch to the specified workspace"""
    try:
        subprocess.run(
            ['qtile', 'cmd-obj', '-o', 'group', workspace_num, '-f', 'toscreen'],
            check=True
        )
        return True
    except:
        return False

def main():
    """Main function"""
    # Get workspace information
    workspace_data = get_workspace_info()

    if workspace_data is None:
        print("Error: Could not get workspace information", file=sys.stderr)
        print("Make sure Qtile is running.", file=sys.stderr)
        return 1

    # Format for Rofi
    rofi_input = format_for_rofi(workspace_data)

    # Call Rofi
    try:
        result = subprocess.run(
            [
                'rofi',
                '-dmenu',
                '-i',
                '-p', 'Workspace',
                '-no-custom',
                '-format', 's',
                '-mesg', 'Select workspace to switch'
            ],
            input=rofi_input,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # User cancelled
            return 0

        # Parse selected line
        selected = result.stdout.strip()
        if not selected:
            return 0

        # Extract workspace number (second character after status indicator)
        parts = selected.split()
        if len(parts) >= 2:
            workspace_num = parts[1]
            if workspace_num.isdigit():
                switch_workspace(workspace_num)

    except Exception as e:
        print(f"Error running rofi: {e}", file=sys.stderr)
        return 1

    return 0

if __name__ == '__main__':
    exit(main())

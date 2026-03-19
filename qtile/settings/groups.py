"""
Workspace and Scratchpad configuration
"""

from libqtile.config import Group, ScratchPad, DropDown
from libqtile.lazy import lazy


def init_groups(terminal):
    """Initialize workspace groups and scratchpad"""
    groups = [Group(i) for i in "123456789"]

    def normalize_group_layout(group):
        """
        Normalize a group's layout state to fix any corruption.
        This fixes issues like empty columns or buggy layout states.
        """
        try:
            if group and group.layout:
                # Force the layout to recalculate and clean up its state
                group.layout.group = group

                # For Columns layout specifically, clean up empty columns
                if hasattr(group.layout, 'columns'):
                    # Remove empty columns
                    group.layout.columns = [col for col in group.layout.columns if col]

                    # If all columns are empty, reset to default state
                    if not group.layout.columns:
                        group.layout.columns = [[]]

                # Force a layout refresh
                if hasattr(group.layout, 'layout'):
                    group.layout.layout(group.windows, group.screen.width, group.screen.height)
        except Exception as e:
            # If normalization fails, just log and continue
            import traceback
            traceback.print_exc()

    # Custom function to swap groups between screens
    @lazy.function
    def go_to_group(qtile, group_name):
        """
        Go to specified group. If the group is already visible on another screen,
        swap it with the current screen's group.
        Includes error handling and layout normalization for buggy workspaces.
        """
        try:
            target_group = qtile.groups_map.get(group_name)
            if not target_group:
                return

            # Normalize the target group's layout before switching
            normalize_group_layout(target_group)

            current_screen = qtile.current_screen
            current_group = current_screen.group

            # If the target group is already on the current screen, do nothing
            if target_group == current_group:
                return

            # Find which screen is displaying the target group
            target_screen = None
            for screen in qtile.screens:
                if screen.group == target_group:
                    target_screen = screen
                    break

            if target_screen and target_screen != current_screen:
                # Target group is on another screen - we need to swap
                current_screen_index = current_screen.index
                target_screen_index = target_screen.index

                # Find an unused group to temporarily assign to target screen
                unused_group = None
                for group in qtile.groups:
                    if group.name == "scratchpad":
                        continue
                    # Find a group that's not currently visible on any screen
                    is_visible = False
                    for screen in qtile.screens:
                        if screen.group == group:
                            is_visible = True
                            break
                    if not is_visible:
                        unused_group = group
                        break

                if unused_group:
                    # Normalize the unused group too
                    normalize_group_layout(unused_group)

                    # Three-way swap to avoid conflicts:
                    # 1. Move unused group to target screen
                    unused_group.toscreen(target_screen_index, toggle=False)
                    # 2. Move target group to current screen
                    target_group.toscreen(current_screen_index, toggle=False)
                    # 3. Move current group to target screen (replacing unused)
                    current_group.toscreen(target_screen_index, toggle=False)
                else:
                    # Fallback: direct swap (might cause temporary glitch)
                    target_group.toscreen(current_screen_index, toggle=False)
                    current_group.toscreen(target_screen_index, toggle=False)
            else:
                # Target group is not visible on any screen, just bring it to current screen
                target_group.toscreen(current_screen.index, toggle=False)

            # Normalize current group after switch
            normalize_group_layout(current_screen.group)

        except Exception as e:
            # If anything goes wrong, fall back to simple switch
            import traceback
            traceback.print_exc()
            try:
                target_group = qtile.groups_map.get(group_name)
                if target_group:
                    target_group.toscreen(toggle=False)
            except:
                pass

    # Add scratchpad after groups are created
    groups.append(
        ScratchPad("scratchpad", [
            # Dropdown terminal
            DropDown(
                "term",
                terminal,
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=0.95,
            ),
            # Calculator
            DropDown(
                "calc",
                "qalculate-gtk",
                width=0.4,
                height=0.6,
                x=0.3,
                y=0.2,
                opacity=0.95,
            ),
            # File manager
            DropDown(
                "files",
                "nautilus",
                width=0.6,
                height=0.7,
                x=0.2,
                y=0.15,
                opacity=0.95,
            ),
        ])
    )

    return groups, go_to_group

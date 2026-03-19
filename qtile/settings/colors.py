"""
Color scheme loaded from theme.json
"""

import json
from pathlib import Path

_theme_file = Path(__file__).parent.parent / "theme.json"
colors = json.loads(_theme_file.read_text())["colors"]

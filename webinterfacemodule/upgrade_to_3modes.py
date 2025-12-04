#!/usr/bin/env python3
"""Upgrade web app to 3-mode system"""

with open('app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # Replace ROBOT_MODES configuration
    if line.strip() == "# Robot configurations":
        new_lines.append("# ==================== MODE CONFIGURATIONS ====================\n")
        new_lines.append("# THREE MODES:\n")
        new_lines.append("# 1. MANUAL: Full control, user provides everything\n")
        new_lines.append("# 2. EMBODIMENT: AI extension tuned for specific robots\n")
        new_lines.append("# 3. GENERAL: AI analyzes any image and extends prompt\n")
        new_lines.append("\n")
        new_lines.append("EMBODIMENT_MODES = {\n")
        new_lines.append("    'so1': {\n")
        new_lines.append("        'name': 'SO-1 Arm (LeRobot)',\n")
        new_lines.append("        'script': 'prompt_extender_so1_arm.py',\n")
        new_lines.append("        'description': 'Single-arm manipulation',\n")
        new_lines.append("        'icon': '🦾'\n")
        new_lines.append("    },\n")
        new_lines.append("    '2wheel': {\n")
        new_lines.append("        'name': '2-Wheel Mobile Robot',\n")
        new_lines.append("        'script': 'prompt_extender_2wheel_mobile.py',\n")
        new_lines.append("        'description': 'Differential drive navigation',\n")
        new_lines.append("        'icon': '🤖'\n")
        new_lines.append("    },\n")
        new_lines.append("    'bimanual': {\n")
        new_lines.append("        'name': 'Bimanual UR3',\n")
        new_lines.append("        'script': 'prompt_extender_bimanual_ur3.py',\n")
        new_lines.append("        'description': 'Dual-arm coordination',\n")
        new_lines.append("        'icon': '🤝'\n")
        new_lines.append("    }\n")
        new_lines.append("}\n")
        new_lines.append("\n")
        new_lines.append("GENERAL_MODE = {\n")
        new_lines.append("    'name': 'General Image Analyzer',\n")
        new_lines.append("    'script': 'prompt_extender_general.py',\n")
        new_lines.append("    'description': 'AI analyzes any robot/scene',\n")
        new_lines.append("    'icon': '🔬'\n")
        new_lines.append("}\n")
        new_lines.append("# ==============================================================\n")

        # Skip old ROBOT_MODES definition
        i += 1
        while i < len(lines) and not lines[i].strip().startswith("# Global"):
            i += 1
        i -= 1  # Back up one line

    else:
        new_lines.append(line)

    i += 1

# Write updated file
with open('app.py', 'w') as f:
    f.writelines(new_lines)

print("✓ Updated MODE configurations in app.py")

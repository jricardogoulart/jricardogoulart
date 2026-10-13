#!/usr/bin/env python3
"""
Convert Ricardo Goulart's ASCII art into an animated terminal-style SVG portrait.
Mimics AVIVASHISHTA29's typing aesthetic:
- macOS-style terminal window with traffic lights
- Line-by-line raster wipe with active typing cursor
- Terminal prompt title bar (jricardo@github: ~$ ./portrait.sh)
- Terminal status line with blinking prompt cursor (jricardo@github: ~$ whoami Ricardo Goulart)
- Crisp dark mode gradient (#111722 -> #0d1117)
"""

import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(HERE, "ascii-art.txt")
OUTPUT_FILE = os.path.join(HERE, "ricardo-ascii.svg")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_lines = f.read().splitlines()

# Trim empty lines from top and bottom if needed, but maintain uniform structure
while raw_lines and not raw_lines[0].strip():
    raw_lines.pop(0)
while raw_lines and not raw_lines[-1].strip():
    raw_lines.pop()

if not raw_lines:
    print("Error: ascii-art.txt is empty!")
    sys.exit(1)

# Find max length and pad all lines evenly
COLS = max(len(line) for line in raw_lines)
rows_txt = [line.ljust(COLS) for line in raw_lines]
ROWS = len(rows_txt)

# Terminal Geometry matching Avi's clean 840px layout
ART_W_TARGET = 800.0
CELL_W = ART_W_TARGET / COLS
CELL_H = CELL_W * 15.0 / 8.0  # Monospace char aspect ratio ~ 1:1.875

ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H

PAD = 20.0
TITLEBAR_H = 32.0
STATUS_H = 34.0

CANVAS_W = round(ART_W + PAD * 2)
CANVAS_H = round(TITLEBAR_H + ART_H + STATUS_H + PAD * 0.8)

# Palette
BG_TOP = "#111722"
BG_BOT = "#0d1117"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"        # GitHub Markdown dimmed text color
CURSOR = "#38bdf8"     # Cyan accent cursor matching Ricardo's banner theme

# Animation timing: portrait finishes revealing in ~5.5s
TOTAL_PRINT_TIME = 5.5
ROW_DUR = TOTAL_PRINT_TIME / ROWS
STAGGER = ROW_DUR

font_size = CELL_H * 0.88
art_top = TITLEBAR_H + 8.0

parts = []

# SVG Root
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, Monaco, monospace">\n'
)

# Gradient Defs
parts.append(
    '  <defs>\n'
    '    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">\n'
    f'      <stop offset="0%" stop-color="{BG_TOP}"/>\n'
    f'      <stop offset="100%" stop-color="{BG_BOT}"/>\n'
    '    </linearGradient>\n'
    '  </defs>\n\n'
)

# Background & Border
parts.append(f'  <rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>\n')
parts.append(
    f'  <rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
    f'fill="none" stroke="{FRAME}" stroke-width="1"/>\n\n'
)

# Titlebar
parts.append(f'  <!-- Terminal Title Bar -->\n')
parts.append(f'  <line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>\n')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'  <circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>\n')

title_label = "jricardo@github: ~$ ./render-portrait.sh --ascii"
parts.append(
    f'  <text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
    f'font-weight="500" text-anchor="middle">{html.escape(title_label)}</text>\n\n'
)

# ASCII Lines with Typing Cursor Effect
parts.append(f'  <!-- Animated ASCII Art Grid ({COLS}x{ROWS}) -->\n')
for ry, line in enumerate(rows_txt):
    row_y = art_top + ry * CELL_H
    y = row_y + CELL_H * 0.74
    delay = ry * STAGGER
    safe = html.escape(line)
    cid = f"r{ry}"

    text_element = (
        f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
        f'font-size="{font_size:.2f}" textLength="{ART_W:.1f}" lengthAdjust="spacing">{safe}</text>'
    )

    # Wipe clipPath
    parts.append(
        f'  <clipPath id="{cid}">'
        f'<rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H:.2f}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W:.1f}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.3f}s" fill="freeze"/>'
        f'</rect></clipPath>\n'
    )
    parts.append(f'  <g clip-path="url(#{cid})">{text_element}</g>\n')

    # Scanning typing cursor on current line
    parts.append(
        f'  <rect y="{row_y+0.5:.1f}" width="{max(CELL_W * 1.2, 4.0):.1f}" height="{CELL_H-1:.1f}" '
        f'fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.3f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.9" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/>'
        f'</rect>\n'
    )

# Footer Status Bar
status_line_y = art_top + ART_H + 8.0
status_y = status_line_y + 19.0
parts.append(f'\n  <!-- Terminal Status Footer -->\n')
parts.append(f'  <line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>\n')

status_prompt = "jricardo@github:~$ whoami "
status_user = "Ricardo Goulart"
prompt_x = PAD
parts.append(
    f'  <text x="{prompt_x}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="12.5">'
    f'{status_prompt}<tspan fill="#38bdf8" font-weight="600">{status_user}</tspan></text>\n'
)

# Blinking prompt cursor after the text
cursor_offset_chars = len(status_prompt + status_user) + 0.5
cursor_x = PAD + cursor_offset_chars * 7.5
parts.append(
    f'  <rect x="{cursor_x:.1f}" y="{status_y - 11:.1f}" width="7.5" height="13" fill="#38bdf8">'
    f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
    f'dur="1s" repeatCount="indefinite"/>'
    f'</rect>\n'
)

parts.append('</svg>\n')

svg_content = "".join(parts)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Generated {OUTPUT_FILE} successfully: {COLS}x{ROWS}, {CANVAS_W}x{CANVAS_H}px, {len(svg_content):,} bytes")

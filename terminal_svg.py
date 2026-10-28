#!/usr/bin/env python3
"""Generate an animated terminal SVG for a GitHub profile README. No dependencies.

Usage:  python terminal_svg.py config.json terminal.svg
        python terminal_svg.py config.json > terminal.svg
See example.json for the config format.
"""
from __future__ import annotations

import argparse
import json
import sys
from xml.sax.saxutils import escape

DEFAULTS = {
    "style": "windows",          # "windows", "linux" or "mac" window chrome
    "title": "user@host",
    "prompt": "$ ",              # a text, or colored parts: [{"text": "me@pc", "color": "#8ae234"}, {"text": "$ "}]
    "width": 800,
    "font_size": 14,
    "char_width": 7.7,           # px per character at font_size 14 (Consolas); tune for other fonts
    "line_height": 21,
    "typing_speed": 12,          # characters per second
    "pause": 0.5,                # seconds between a command and its output
    "loop": True,                # replay forever; false plays once and keeps the final screen
    "hold": 5,                   # seconds the finished screen stays before replaying
    "theme": {"bg": "#0c0c0c", "bar": "#202020", "border": "#3a3a3a",
              "cmd": "#39ff14", "out": "#21c421", "title": "#d0d0d0"},
    "lines": [],
}
POSITIVE = ("width", "font_size", "char_width", "line_height", "typing_speed")
NON_NEGATIVE = ("pause", "hold")
FONT_FAMILY = "Consolas, 'Cascadia Mono', Menlo, ui-monospace, monospace"
WIDER_FONTS = 1.1                # Menlo and Linux monospace fonts are ~10% wider than Consolas

# Layout (px)
TEXT_X = 16                      # left margin of every line
FIRST_BASELINE = 62              # baseline of the first line, just below the title bar
ASCENT = 16                      # how far glyphs rise above the baseline
BOTTOM_PADDING = 4
CURSOR_ROOM = 8                  # extra clip width so the last typed character isn't shaved

# Timing (s)
START_DELAY = 0.3
OUTPUT_STEP = 0.1                # gap between output lines
MIN_TYPING = 0.01                # an empty command still needs a non-zero animation


# ---------------------------------------------------------------- config

def load_config(cfg: dict) -> dict:
    """Merge the user config over DEFAULTS and reject mistakes with a clear message."""
    unknown = sorted(set(cfg) - set(DEFAULTS))
    if unknown:
        raise ValueError(f"unknown option(s): {', '.join(unknown)}")
    c = {**DEFAULTS, **cfg, "theme": {**DEFAULTS["theme"], **cfg.get("theme", {})}}
    if c["style"] not in CHROME:
        raise ValueError(f'style must be one of {", ".join(CHROME)}, got "{c["style"]}"')
    if not isinstance(c["loop"], bool):
        raise ValueError(f"loop must be true or false, got {c['loop']!r}")
    for key in POSITIVE + NON_NEGATIVE:
        check_number(key, c[key], allow_zero=key in NON_NEGATIVE)
    c["prompt"] = prompt_parts(c["prompt"])
    for i, line in enumerate(c["lines"]):
        is_command = isinstance(line, dict) and list(line) == ["cmd"] and isinstance(line["cmd"], str)
        if not (isinstance(line, str) or is_command):
            raise ValueError(f'lines[{i}] must be a text or {{"cmd": "..."}}, got {line!r}')
    return c


def check_number(key: str, value, allow_zero: bool) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{key} must be a number {'>= 0' if allow_zero else '> 0'}, got {value!r}")


def prompt_parts(prompt) -> list[dict]:
    """A prompt is a text or a list of {"text", "color"} parts; always return the list form."""
    parts = [{"text": prompt}] if isinstance(prompt, str) else prompt
    valid = isinstance(parts, list) and all(
        isinstance(p, dict) and isinstance(p.get("text"), str) and set(p) <= {"text", "color"} for p in parts)
    if not valid:
        raise ValueError('prompt must be a text or a list of {"text": "...", "color": "#..."}')
    return parts


def prompt_text(c: dict) -> str:
    return "".join(part["text"] for part in c["prompt"])


def long_lines(c: dict) -> list[str]:
    """Lines that would run past the right edge on Mac/Linux fonts."""
    max_chars = int((c["width"] - 2 * TEXT_X) / (c["char_width"] * WIDER_FONTS))
    texts = [line if isinstance(line, str) else prompt_text(c) + line["cmd"] for line in c["lines"]]
    return [text for text in texts if len(text) > max_chars]


# ---------------------------------------------------------------- timeline

def schedule(c: dict, lines: list) -> tuple[list[float], float]:
    """Start time of every line, and the length of one full cycle (until the replay)."""
    starts, t = [], START_DELAY
    for line in lines:
        starts.append(t)
        if isinstance(line, dict):
            t += typing_time(c, line["cmd"]) + c["pause"]
        elif line:
            t += OUTPUT_STEP
    return starts, starts[-1] + MIN_TYPING + c["hold"]


def typing_time(c: dict, cmd: str) -> float:
    return max(MIN_TYPING, len(cmd) / c["typing_speed"])


def animate(c: dict, attribute: str, values: list, times: list[float], cycle: float, mode: str = "linear") -> str:
    """One animation spanning the whole cycle, so every replay starts from a clean screen.

    values[k] is reached at times[k] seconds; two equal times make an instant jump."""
    key_times = ";".join(f"{t / cycle:.4f}" for t in times)
    ending = 'repeatCount="indefinite"' if c["loop"] else 'fill="freeze"'
    return (f'<animate attributeName="{attribute}" values="{";".join(map(str, values))}" keyTimes="{key_times}" '
            f'calcMode="{mode}" dur="{cycle:.2f}s" {ending}/>')


# ---------------------------------------------------------------- terminal body

def render_lines(c: dict) -> tuple[list[str], list[str]]:
    """Return the clip paths and <text> elements of every line."""
    lines = c["lines"] + [{"cmd": ""}]  # the extra empty command holds the cursor
    starts, cycle = schedule(c, lines)
    clips, texts = [], []
    for i, (line, t) in enumerate(zip(lines, starts)):
        if isinstance(line, dict):
            clip, text = command(c, i, line["cmd"], t, cycle)
            clips.append(clip)
            texts.append(text)
        elif line:
            texts.append(output(c, i, line, t, cycle))
    return clips, texts


def line_y(c: dict, i: int) -> int:
    return FIRST_BASELINE + c["line_height"] * i


def command(c: dict, i: int, cmd: str, t: float, cycle: float) -> tuple[str, str]:
    """Return the clip path and the <text> of one command.

    The clip keeps the line hidden until its turn, shows the prompt, grows to "type" the
    command, then opens to full width so wider fonts (no Consolas) aren't cut."""
    typed_at = t + typing_time(c, cmd)
    prompt_end = TEXT_X + c["char_width"] * len(prompt_text(c))
    typed_end = prompt_end + c["char_width"] * len(cmd) + CURSOR_ROOM
    width = animate(c, "width", [0, 0, f"{prompt_end:.0f}", f"{typed_end:.0f}", c["width"], c["width"]],
                    [0, t, t, typed_at, typed_at, cycle], cycle)
    clip = (f'<clipPath id="c{i}"><rect x="0" y="{line_y(c, i) - ASCENT}" width="0" height="{c["line_height"]}">'
            f'{width}</rect></clipPath>')
    prompt = "".join(f'<tspan fill="{part["color"]}">{escape(part["text"])}</tspan>' if "color" in part
                     else escape(part["text"]) for part in c["prompt"])
    text = (f'<text x="{TEXT_X}" y="{line_y(c, i)}" fill="{c["theme"]["cmd"]}" clip-path="url(#c{i})" '
            f'xml:space="preserve">{prompt}{escape(cmd)}{"" if cmd else CURSOR}</text>')
    return clip, text


def output(c: dict, i: int, text: str, t: float, cycle: float) -> str:
    """An output line that appears at time t."""
    return (f'<text x="{TEXT_X}" y="{line_y(c, i)}" opacity="0" xml:space="preserve">{escape(text)}'
            f'{animate(c, "opacity", [0, 1], [0, t], cycle, mode="discrete")}</text>')


# Blinks from the start; the clip of its line keeps it hidden until its turn.
CURSOR = ('<tspan>_<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1s" '
          'repeatCount="indefinite"/></tspan>')


# ---------------------------------------------------------------- window chrome

def title_bar(c: dict) -> str:
    """Title bar with rounded top corners."""
    w = c["width"]
    return f'<path d="M0.5 8 a8 8 0 0 1 8 -7.5 H{w - 8.5} a8 8 0 0 1 8 7.5 V32 H0.5 Z" fill="{c["theme"]["bar"]}"/>'


def windows_chrome(c: dict) -> str:
    """Windows Terminal: icon and title on the left, buttons on the right."""
    th, w = c["theme"], c["width"]
    return (f'<rect x="12" y="9" width="16" height="14" rx="2" fill="{th["bg"]}" stroke="#8a8a8a"/>'
            f'<text x="15" y="20" fill="{th["cmd"]}" font-size="10" font-weight="bold">&gt;_</text>'
            f'<text x="38" y="21" fill="{th["title"]}" font-size="13">{escape(c["title"])}</text>'
            f'<text x="{w - 12}" y="21" text-anchor="end" fill="{th["title"]}" font-size="14" '
            f'xml:space="preserve">─    ☐    ✕</text>')


def linux_chrome(c: dict) -> str:
    """GNOME/Ubuntu: centered bold title, round buttons on the right."""
    w = c["width"]
    buttons = "".join(
        f'<circle cx="{w - x}" cy="16" r="9" fill="{fill}"/>'
        f'<text x="{w - x}" y="20" text-anchor="middle" fill="#ffffff" font-size="11">{glyph}</text>'
        for x, fill, glyph in ((64, "#4a4a4a", "─"), (40, "#4a4a4a", "□"), (16, "#e95420", "✕")))
    return (buttons + f'<text x="{w / 2}" y="21" text-anchor="middle" fill="{c["theme"]["title"]}" '
                      f'font-size="13" font-weight="bold">{escape(c["title"])}</text>')


def mac_chrome(c: dict) -> str:
    """macOS: traffic lights on the left, centered title."""
    return ('<circle cx="20" cy="17" r="6" fill="#ff5f56"/><circle cx="40" cy="17" r="6" fill="#ffbd2e"/>'
            '<circle cx="60" cy="17" r="6" fill="#27c93f"/>'
            f'<text x="{c["width"] / 2}" y="22" text-anchor="middle" fill="{c["theme"]["title"]}" '
            f'font-size="13">{escape(c["title"])}</text>')


CHROME = {"windows": windows_chrome, "linux": linux_chrome, "mac": mac_chrome}


# ---------------------------------------------------------------- document

def render(cfg: dict) -> str:
    """Config dict -> SVG text. Raises ValueError on a bad config."""
    c = load_config(cfg)
    th, w = c["theme"], c["width"]
    h = line_y(c, len(c["lines"]) + 1) + BOTTOM_PADDING  # one extra line for the cursor
    clips, texts = render_lines(c)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'font-family="{FONT_FAMILY}" font-size="{c["font_size"]}">',
        f'<defs>{"".join(clips)}</defs>',
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="8" fill="{th["bg"]}" stroke="{th["border"]}"/>',
        title_bar(c) + CHROME[c["style"]](c),
        f'<g fill="{th["out"]}">',  # xml:space stays on each <text>: Chrome doesn't inherit it from <g>
        *texts,
        "</g>",
        "</svg>",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an animated terminal SVG for a GitHub profile README.")
    parser.add_argument("config", help="JSON config, see example.json")
    parser.add_argument("output", nargs="?", help="SVG file to write (default: stdout)")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        try:
            c = load_config(json.load(f))
        except ValueError as e:  # also catches invalid JSON (JSONDecodeError is a ValueError)
            sys.exit(f"{args.config}: {e}")
    for text in long_lines(c):
        print(f"warning: may not fit on Mac/Linux, raise width or shorten it: {text}", file=sys.stderr)
    svg = render(c)

    if args.output:  # safer than ">" on Windows PowerShell 5.1, which would write UTF-16
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
    else:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        sys.stdout.write(svg)


if __name__ == "__main__":
    main()

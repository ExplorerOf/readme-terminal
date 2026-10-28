#!/usr/bin/env python3
"""Generate an animated terminal SVG for a GitHub profile README. No dependencies.

Usage:  python terminal_svg.py config.json > terminal.svg
See example.json for the config format.
"""
import json
import sys
from xml.sax.saxutils import escape

DEFAULTS = {
    "style": "windows",          # "windows" or "mac" window chrome
    "title": "user@host",
    "prompt": "$ ",
    "width": 800,
    "font_size": 14,
    "char_width": 7.7,           # px per character at font_size 14 (Consolas); tune for other fonts
    "line_height": 21,
    "typing_speed": 12,          # characters per second
    "pause": 0.5,                # seconds between a command and its output
    "theme": {"bg": "#0c0c0c", "bar": "#202020", "border": "#3a3a3a",
              "cmd": "#39ff14", "out": "#21c421", "title": "#d0d0d0"},
    "lines": [],
}


def render(cfg):
    c = {**DEFAULTS, **cfg}
    th = {**DEFAULTS["theme"], **cfg.get("theme", {})}
    W, CW, LH, X, Y0 = c["width"], c["char_width"], c["line_height"], 16, 62
    prompt = c["prompt"]
    lines = c["lines"] + [{"cmd": ""}]        # final blinking cursor
    H = Y0 + LH * len(lines) + 4
    t, body, defs = 0.3, [], []
    for i, line in enumerate(lines):
        y = Y0 + LH * i
        if isinstance(line, str):
            line = {"out": line}
        if "cmd" in line:
            txt, pw = line["cmd"], X + CW * len(prompt)
            dur = max(0.01, len(txt) / c["typing_speed"])
            w = pw + CW * len(txt) + 8
            defs.append(
                f'<clipPath id="c{i}"><rect x="0" y="{y-16}" width="{pw:.0f}" height="{LH}">'
                f'<animate attributeName="width" from="{pw:.0f}" to="{w:.0f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
                f'</rect></clipPath>')
            cursor = "" if txt else (
                f'<tspan opacity="0">_<animate attributeName="opacity" values="1;1;0;0" dur="1s" '
                f'begin="{t:.2f}s" repeatCount="indefinite"/></tspan>')
            body.append(f'<text x="{X}" y="{y}" fill="{th["cmd"]}" clip-path="url(#c{i})" xml:space="preserve">'
                        f'{escape(prompt)}{escape(txt)}{cursor}</text>')
            t += dur + c["pause"]
        elif line.get("out"):
            body.append(f'<text x="{X}" y="{y}" fill="{th["out"]}" opacity="0" xml:space="preserve">{escape(line["out"])}'
                        f'<animate attributeName="opacity" to="1" begin="{t:.2f}s" dur="0.05s" fill="freeze"/></text>')
            t += 0.1
    bar = f'<path d="M0.5 8 a8 8 0 0 1 8 -7.5 H{W-8.5} a8 8 0 0 1 8 7.5 V32 H0.5 Z" fill="{th["bar"]}"/>'
    if c["style"] == "mac":
        chrome = (bar +
                  '<circle cx="20" cy="17" r="6" fill="#ff5f56"/><circle cx="40" cy="17" r="6" fill="#ffbd2e"/>'
                  '<circle cx="60" cy="17" r="6" fill="#27c93f"/>'
                  f'<text x="{W/2}" y="22" text-anchor="middle" fill="{th["title"]}" font-size="13">{escape(c["title"])}</text>')
    else:
        chrome = (bar +
                  f'<rect x="12" y="9" width="16" height="14" rx="2" fill="{th["bg"]}" stroke="#8a8a8a"/>'
                  f'<text x="15" y="20" fill="{th["cmd"]}" font-size="10" font-weight="bold">&gt;_</text>'
                  f'<text x="38" y="21" fill="{th["title"]}" font-size="13">{escape(c["title"])}</text>'
                  f'<text x="{W-100}" y="21" fill="{th["title"]}" font-size="14" xml:space="preserve">─    ☐    ✕</text>')
    font = "Consolas, 'Cascadia Mono', Menlo, ui-monospace, monospace"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="{font}" font-size="{c["font_size"]}">\n'
            f'<defs>{"".join(defs)}</defs>\n'
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="{th["bg"]}" stroke="{th["border"]}"/>\n'
            f'{chrome}\n' + "\n".join(body) + "\n</svg>\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(render(json.load(f)))

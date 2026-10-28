"""Run: python test_terminal_svg.py"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from terminal_svg import long_lines, load_config, render

NS = "{http://www.w3.org/2000/svg}"

# Every example renders to valid SVG, commands start hidden, and the committed SVG is up to date.
configs = sorted(Path(__file__).parent.glob("example*.json"))
assert len(configs) == 3, configs
for cfg in configs:
    svg = render(json.loads(cfg.read_text(encoding="utf-8")))
    clips = list(ET.fromstring(svg).iter(NS + "clipPath"))
    assert clips and all(c[0].get("width") == "0" for c in clips), "commands must start hidden"
    assert cfg.with_suffix(".svg").read_text(encoding="utf-8") == svg, f"{cfg.stem}.svg is stale, regenerate it"

# Loops by default; "loop": false plays once and keeps the final screen.
lines = [{"cmd": "ls"}, "a.txt"]
assert 'keyTimes="0.0000;' in render({"lines": lines}) and 'repeatCount="indefinite"' in render({"lines": lines})
once = render({"lines": lines, "loop": False})
assert once.count('fill="freeze"') == 3 and once.count('repeatCount="indefinite"') == 1  # 1 = cursor blink

# Colored prompt parts become <tspan>s; plain parts use the command color.
svg = render({"prompt": [{"text": "me", "color": "#8ae234"}, {"text": "$ "}], "lines": lines})
assert '<tspan fill="#8ae234">me</tspan>$ ls' in svg

# Config mistakes fail with a clear message instead of a silently wrong SVG.
for bad in [{"style": "ubuntu"}, {"typing-speed": 20}, {"lines": [{"out": "x"}]}, {"lines": [42]},
            {"loop": "yes"}, {"hold": -1}, {"width": 0}, {"prompt": [{"txt": "$ "}]}]:
    try:
        render(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"accepted bad config {bad}")

# Long lines are reported; a normal one is not.
assert long_lines(load_config({"lines": ["x" * 120, "ok"]})) == ["x" * 120]

print("ok")

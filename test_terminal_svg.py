"""Run: python test_terminal_svg.py"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from terminal_svg import render

NS = "{http://www.w3.org/2000/svg}"
configs = sorted(Path(__file__).parent.glob("example*.json"))
assert len(configs) == 3, configs
for cfg in configs:
    svg = render(json.loads(cfg.read_text(encoding="utf-8")))
    clips = list(ET.fromstring(svg).iter(NS + "clipPath"))
    assert clips and all(c[0].get("width") == "0" for c in clips), "commands must start hidden"
    assert cfg.with_suffix(".svg").read_text(encoding="utf-8") == svg, f"{cfg.stem}.svg is stale, regenerate it"
print("ok")

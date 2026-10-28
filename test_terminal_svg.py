"""Run: python test_terminal_svg.py"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from terminal_svg import render

NS = "{http://www.w3.org/2000/svg}"
here = Path(__file__).parent
for name in ["example", "example-mac"]:
    svg = render(json.loads((here / f"{name}.json").read_text(encoding="utf-8")))
    clips = list(ET.fromstring(svg).iter(NS + "clipPath"))
    assert clips and all(c[0].get("width") == "0" for c in clips), "commands must start hidden"
    assert (here / f"{name}.svg").read_text(encoding="utf-8") == svg, f"{name}.svg is stale, regenerate it"
print("ok")

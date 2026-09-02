from pathlib import Path
import xml.etree.ElementTree as ElementTree


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
OUTPUT_DIRECTORY = Path("profile-3d-contrib")
MAPS = (
    ("profile-season.svg", "profile-map-light.svg", False),
    ("profile-season.svg", "profile-map-dark.svg", True),
)

DARK_THEME = """
.fill-bg { fill: #0d1117 !important; }
[class^="cont-top-"][class$="-0"] { fill: #161b22 !important; }
[class^="cont-left-"][class$="-0"] { fill: #0d1117 !important; }
[class^="cont-right-"][class$="-0"] { fill: #010409 !important; }
[class^="cont-top-"][class$="-1"] { fill: #0e4429 !important; }
[class^="cont-left-"][class$="-1"] { fill: #0a321f !important; }
[class^="cont-right-"][class$="-1"] { fill: #082818 !important; }
[class^="cont-top-"][class$="-2"] { fill: #006d32 !important; }
[class^="cont-left-"][class$="-2"] { fill: #005327 !important; }
[class^="cont-right-"][class$="-2"] { fill: #00431f !important; }
[class^="cont-top-"][class$="-3"] { fill: #26a641 !important; }
[class^="cont-left-"][class$="-3"] { fill: #1d7f32 !important; }
[class^="cont-right-"][class$="-3"] { fill: #176629 !important; }
[class^="cont-top-"][class$="-4"] { fill: #39d353 !important; }
[class^="cont-left-"][class$="-4"] { fill: #2aa343 !important; }
[class^="cont-right-"][class$="-4"] { fill: #218336 !important; }
"""


def svg_tag(name: str) -> str:
    return f"{{{SVG_NAMESPACE}}}{name}"


def extract_map(source_name: str, destination_name: str, use_dark_theme: bool) -> None:
    source = OUTPUT_DIRECTORY / source_name
    destination = OUTPUT_DIRECTORY / destination_name
    tree = ElementTree.parse(source)
    root = tree.getroot()

    top_level_groups = [child for child in root if child.tag == svg_tag("g")]
    if len(top_level_groups) < 4:
        raise RuntimeError(f"Unexpected contribution SVG structure in {source}")

    for group in top_level_groups[1:]:
        root.remove(group)

    root.set("width", "1240")
    root.set("height", "710")
    root.set("viewBox", "0 110 1240 710")

    title = ElementTree.Element(svg_tag("title"))
    title.text = "GitHub contribution activity in 3D"
    root.insert(0, title)

    if use_dark_theme:
        theme = ElementTree.Element(svg_tag("style"))
        theme.text = DARK_THEME
        root.insert(2, theme)

    tree.write(destination, encoding="utf-8", xml_declaration=False)


if __name__ == "__main__":
    ElementTree.register_namespace("", SVG_NAMESPACE)
    for source_file, destination_file, dark_theme in MAPS:
        extract_map(source_file, destination_file, dark_theme)

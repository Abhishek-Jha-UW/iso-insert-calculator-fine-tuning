"""Schematic plan-view thumbnails keyed by insert shape code."""

from math import cos, pi, radians, sin, tan
from urllib.parse import quote


def shape_thumbnail(code, nose_angle_deg):
    if code == "R":
        outline = '<circle cx="20" cy="20" r="14"/>'
    elif code == "W":
        outline = '<path d="M20 5 Q31 13 35 29 Q20 36 5 29 Q9 13 20 5Z"/>'
    elif code == "L":
        outline = '<rect x="5" y="11" width="30" height="18"/>'
    elif code == "S":
        outline = '<rect x="7" y="7" width="26" height="26"/>'
    else:
        sides = {"T": 3, "P": 5, "H": 6, "O": 8}.get(code)
        if sides:
            angles = [-pi / 2 + (2 * index + (sides == 8)) * pi / sides
                      for index in range(sides)]
            points = [(20 + 15 * cos(angle), 20 + 15 * sin(angle)) for angle in angles]
        elif code in {"C", "D", "V", "E", "M"}:
            half_width = 16 * tan(radians(nose_angle_deg / 2))
            points = [(4, 20), (20, 20 - half_width), (36, 20), (20, 20 + half_width)]
        elif code in {"A", "B", "K"}:
            skew = 20 / tan(radians(nose_angle_deg))
            points = [(6, 30), (34 - skew, 30), (34, 10), (6 + skew, 10)]
        else:
            return None
        coordinates = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        outline = f'<polygon points="{coordinates}"/>'

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40">'
        f'<g fill="#f3c75b" stroke="#604512" stroke-width="1.5" stroke-linejoin="round">{outline}</g>'
        '</svg>'
    )
    return "data:image/svg+xml;utf8," + quote(svg)

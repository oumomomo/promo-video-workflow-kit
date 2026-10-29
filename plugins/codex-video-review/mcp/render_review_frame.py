"""Draw saved normalized video review marks on a temporary extracted frame."""

import json
import math
import sys

from PIL import Image, ImageDraw


def main():
    source, target = sys.argv[1:3]
    marks = json.load(sys.stdin)
    image = Image.open(source).convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    stroke = max(4, round(min(width, height) / 130))
    color = (255, 139, 0)

    for mark in marks:
        points = [(round(x * width), round(y * height)) for x, y in mark["points"]]
        if len(points) < 2:
            continue
        kind = mark["type"]
        if kind == "box":
            x0, y0 = points[0]
            x1, y1 = points[-1]
            draw.rectangle((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), outline=color, width=stroke)
        elif kind == "pen":
            draw.line(points, fill=color, width=stroke, joint="curve")
        else:
            start, end = points[0], points[-1]
            draw.line((start, end), fill=color, width=stroke)
            if kind == "arrow":
                angle = math.atan2(end[1] - start[1], end[0] - start[0])
                length = stroke * 5
                for offset in (-0.55, 0.55):
                    tip = (
                        round(end[0] - length * math.cos(angle + offset)),
                        round(end[1] - length * math.sin(angle + offset)),
                    )
                    draw.line((end, tip), fill=color, width=stroke)

    image.save(target)


if __name__ == "__main__":
    main()

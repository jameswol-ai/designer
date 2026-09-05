from __future__ import annotations

from html import escape
from typing import Dict, Iterable, Optional


def _num(value: float) -> str:
    return f"{float(value):.3f}".rstrip("0").rstrip(".")


def _bounds(graphics: Dict):
    xs, ys = [], []
    for item in graphics.get("graphics", []):
        if item.get("type") in {"line", "dimension"}:
            for x, y in item.get("points", []):
                xs.append(float(x)); ys.append(float(y))
            for x, y in item.get("extension", []):
                xs.append(float(x)); ys.append(float(y))
        elif item.get("type") in {"text"}:
            xs.append(float(item.get("x", 0))); ys.append(float(item.get("y", 0)))
        elif item.get("type") == "arc":
            cx, cy = item.get("center", [0, 0]); r = float(item.get("radius", 0))
            xs.extend([cx-r, cx+r]); ys.extend([cy-r, cy+r])
    if not xs:
        return -1, -1, 2, 2
    pad = max(0.75, (max(xs)-min(xs))*0.06, (max(ys)-min(ys))*0.06)
    return min(xs)-pad, min(ys)-pad, max(xs)-min(xs)+2*pad, max(ys)-min(ys)+2*pad


def graphics_to_svg(graphics: Dict, width: int = 1200, height: int = 850, layers: Optional[Iterable[str]] = None, title: str = "Architectural Drawing") -> str:
    min_x, min_y, span_x, span_y = _bounds(graphics)
    scale = min((width-80)/span_x, (height-80)/span_y)
    allowed = set(layers) if layers is not None else None

    def pt(x, y):
        return 40 + (float(x)-min_x)*scale, height - (40 + (float(y)-min_y)*scale)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<title>{escape(title)}</title>']
    for item in graphics.get("graphics", []):
        layer = item.get("layer", "annotation")
        if allowed is not None and layer not in allowed:
            continue
        kind = item.get("type")
        if kind == "line":
            points = [pt(*p) for p in item.get("points", [])]
            if len(points) >= 2:
                d = " ".join(f"{_num(x)},{_num(y)}" for x,y in points)
                parts.append(f'<polyline points="{d}" fill="none" stroke="black" stroke-width="2" vector-effect="non-scaling-stroke"/>')
        elif kind == "dimension":
            ext = item.get("extension", [])
            if len(ext) == 4:
                for a,b in ((ext[0],ext[1]),(ext[2],ext[3])):
                    x1,y1=pt(*a); x2,y2=pt(*b)
                    parts.append(f'<line x1="{_num(x1)}" y1="{_num(y1)}" x2="{_num(x2)}" y2="{_num(y2)}" stroke="black" stroke-width="1"/>')
            points=[pt(*p) for p in item.get("points", [])]
            if len(points)>=2:
                d=" ".join(f"{_num(x)},{_num(y)}" for x,y in points)
                parts.append(f'<polyline points="{d}" fill="none" stroke="black" stroke-width="1"/>')
                x=sum(p[0] for p in points)/len(points); y=sum(p[1] for p in points)/len(points)
                parts.append(f'<text x="{_num(x)}" y="{_num(y-5)}" text-anchor="middle" font-family="Arial" font-size="12" fill="black">{escape(str(item.get("label","")))}</text>')
        elif kind == "text":
            x,y=pt(item.get("x",0),item.get("y",0))
            size=max(9,float(item.get("size",0.14))*55)
            parts.append(f'<text x="{_num(x)}" y="{_num(y)}" text-anchor="middle" font-family="Arial" font-size="{_num(size)}" fill="black">{escape(str(item.get("text","")))}</text>')
        elif kind == "arc":
            cx,cy=pt(*item.get("center",[0,0])); r=float(item.get("radius",1))*scale
            parts.append(f'<circle cx="{_num(cx)}" cy="{_num(cy)}" r="{_num(r)}" fill="none" stroke="black" stroke-width="1" stroke-dasharray="4 3"/>')
    parts.append('</svg>')
    return "".join(parts)

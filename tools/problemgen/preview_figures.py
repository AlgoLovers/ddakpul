#!/usr/bin/env python3
"""문제 도형(figure) 시각 QA 미리보기.

에뮬레이터 없이 도형이 제대로 그려지는지 확인하려고, 앱 렌더러
(core/designsystem/component/ProblemFigureView.kt · presentation/print/WorksheetPdfGenerator.kt)와
'같은 수학'(좌표계·투영·오클루전 순서)으로 그림을 그려 대조표 PNG를 만든다.
새 FigureType을 추가하면 여기 렌더 함수도 추가해 사람이 눈으로 검증할 것.

필요: Pillow.  실행:
  python3 -m venv .venv && .venv/bin/pip install Pillow
  .venv/bin/python tools/problemgen/preview_figures.py     # PNG → $PREVIEW_OUT (기본 /tmp/ddakpul-preview)
"""
import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = os.environ.get("PREVIEW_OUT", "/tmp/ddakpul-preview")
os.makedirs(OUT, exist_ok=True)
INK, ACCENT = (40, 40, 40), (60, 100, 200)
FONT_PATHS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
]


def font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


F, FID = font(15), font(16)


def clock(d, fig, box):
    h, m = fig["params"].get("hour", 12), fig["params"].get("minute", 0)
    x0, y0, x1, y1 = box
    cx, cy, rad = (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) * 0.42
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=INK, width=3)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        d.line([(cx + math.cos(a) * rad * 0.82, cy + math.sin(a) * rad * 0.82),
                (cx + math.cos(a) * rad * 0.95, cy + math.sin(a) * rad * 0.95)], fill=INK, width=4 if i % 3 == 0 else 2)
    ha, ma = math.radians((h % 12) * 30 + m * 0.5 - 90), math.radians(m * 6 - 90)
    d.line([(cx, cy), (cx + math.cos(ha) * rad * 0.5, cy + math.sin(ha) * rad * 0.5)], fill=ACCENT, width=6)
    d.line([(cx, cy), (cx + math.cos(ma) * rad * 0.75, cy + math.sin(ma) * rad * 0.75)], fill=INK, width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)


def polygon(d, fig, box):
    n, diag = fig["params"].get("n", 5), fig["params"].get("diagonals", 0)
    x0, y0, x1, y1 = box
    cx, cy, rad = (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) * 0.42
    pts = [(cx + math.cos(math.radians(-90 + i * 360 / n)) * rad, cy + math.sin(math.radians(-90 + i * 360 / n)) * rad) for i in range(n)]
    d.polygon(pts, outline=INK, width=3)
    if diag:
        for i in range(n):
            for j in range(i + 2, n):
                if not (i == 0 and j == n - 1):
                    d.line([pts[i], pts[j]], fill=ACCENT, width=2)


def grid(d, fig, box):
    w, h, mark = fig["params"].get("w", 3), fig["params"].get("h", 3), fig["params"].get("mark", 0)
    x0, y0, x1, y1 = box
    cell = min(x1 - x0, y1 - y0) * 0.82 / max(w, h)
    gl, gt = (x0 + x1) / 2 - cell * w / 2, (y0 + y1) / 2 - cell * h / 2
    for i in range(w + 1):
        d.line([(gl + i * cell, gt), (gl + i * cell, gt + h * cell)], fill=INK, width=2)
    for j in range(h + 1):
        d.line([(gl, gt + j * cell), (gl + w * cell, gt + j * cell)], fill=INK, width=2)
    if mark:
        d.ellipse([gl - 6, gt + h * cell - 6, gl + 6, gt + h * cell + 6], fill=ACCENT)
        d.ellipse([gl + w * cell - 6, gt - 6, gl + w * cell + 6, gt + 6], outline=ACCENT, width=3)


def dot_border(d, fig, box):
    n = min(fig["params"].get("side", 6), 20)
    x0, y0, x1, y1 = box
    side = min(x1 - x0, y1 - y0) * 0.82
    step = side / (n - 1) if n > 1 else side
    left, top, r = (x0 + x1) / 2 - side / 2, (y0 + y1) / 2 - side / 2, min(step * 0.28, 8)
    for row in range(n):
        for col in range(n):
            if row in (0, n - 1) or col in (0, n - 1):
                x, y = left + col * step, top + row * step
                d.ellipse([x - r, y - r, x + r, y + r], fill=INK)


def cube_stack(d, fig, box):
    w, dep, hs = fig["params"].get("w", 1), fig["params"].get("d", 1), fig.get("heights", [])
    if len(hs) != w * dep:
        return
    mh = max(max(hs), 1)
    x0, y0, x1, y1 = box
    side = min(x1 - x0, y1 - y0)
    left, top = x0 + ((x1 - x0) - side) / 2, y0 + ((y1 - y0) - side) / 2
    u = side * 0.9 / max(w + dep, (w + dep) / 2 + mh)
    hw, hh, ch = u, u / 2, u
    ox = left + (side - (w + dep) * hw) / 2 + dep * hw
    oy = top + (side - ((w + dep) * hh + mh * ch)) / 2 + mh * ch
    pr = lambda gx, gy, gz: (ox + (gx - gy) * hw, oy + (gx + gy) * hh - gz * ch)
    fills = [(246, 246, 246), (214, 214, 214), (184, 184, 184)]
    for t in range(w + dep - 1):
        for c in range(w):
            r = t - c
            if r < 0 or r >= dep:
                continue
            for l in range(hs[r * w + c]):
                d.polygon([pr(c, r, l + 1), pr(c + 1, r, l + 1), pr(c + 1, r + 1, l + 1), pr(c, r + 1, l + 1)], fill=fills[0], outline=INK, width=2)
                d.polygon([pr(c + 1, r, l + 1), pr(c + 1, r + 1, l + 1), pr(c + 1, r + 1, l), pr(c + 1, r, l)], fill=fills[1], outline=INK, width=2)
                d.polygon([pr(c, r + 1, l + 1), pr(c + 1, r + 1, l + 1), pr(c + 1, r + 1, l), pr(c, r + 1, l)], fill=fills[2], outline=INK, width=2)


def grid_polygon(d, fig, box):
    cols = fig["params"].get("cols", 4)
    rows = fig["params"].get("rows", 4)
    n = fig["params"].get("n", 3)
    hs = fig.get("heights", [])
    if len(hs) != 2 * n:
        return
    x0, y0, x1, y1 = box
    cell = min(x1 - x0, y1 - y0) * 0.82 / max(cols, rows)
    gl = (x0 + x1) / 2 - cell * cols / 2
    gt = (y0 + y1) / 2 - cell * rows / 2
    for i in range(cols + 1):
        d.line([(gl + i * cell, gt), (gl + i * cell, gt + rows * cell)], fill=(185, 185, 185), width=1)
    for j in range(rows + 1):
        d.line([(gl, gt + j * cell), (gl + cols * cell, gt + j * cell)], fill=(185, 185, 185), width=1)
    pts = [(gl + hs[2 * i] * cell, gt + hs[2 * i + 1] * cell) for i in range(n)]
    d.polygon(pts, fill=(185, 208, 246))
    for i in range(n):
        d.line([pts[i], pts[(i + 1) % n]], fill=ACCENT, width=3)


def triangle_fan(d, fig, box):
    k = fig["params"].get("cevians", 2)
    x0, y0, x1, y1 = box
    s = min(x1 - x0, y1 - y0)
    cx = (x0 + x1) / 2
    ty = (y0 + y1) / 2 - s / 2
    apex = (cx, ty + s * 0.06)
    base_y = ty + s * 0.94
    bl_x = cx - s * 0.44
    br_x = cx + s * 0.44
    for i in range(1, k + 1):
        fx = bl_x + (br_x - bl_x) * i / (k + 1)
        d.line([apex, (fx, base_y)], fill=ACCENT, width=2)
    d.line([apex, (bl_x, base_y)], fill=INK, width=3)
    d.line([apex, (br_x, base_y)], fill=INK, width=3)
    d.line([(bl_x, base_y), (br_x, base_y)], fill=INK, width=3)


RENDERERS = {"CLOCK": clock, "POLYGON": polygon, "GRID": grid, "DOT_BORDER": dot_border, "CUBE_STACK": cube_stack, "GRID_POLYGON": grid_polygon, "TRIANGLE_FAN": triangle_fan}
TW, FH, LH = 300, 210, 96


def tile(p):
    img = Image.new("RGB", (TW, FH + LH), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, TW - 1, FH + LH - 1], outline=(210, 210, 210))
    RENDERERS[p["figure"]["type"]](d, p["figure"], (8, 8, TW - 8, FH - 8))
    d.line([(0, FH), (TW, FH)], fill=(230, 230, 230))
    d.text((8, FH + 4), f"[{p['id']}]  정답: {p['choices'][p['answerIndex']]}", font=FID, fill=(20, 20, 120))
    y = FH + 26
    for i in range(0, min(len(p["statement"]), 72), 24):
        d.text((8, y), p["statement"][i:i + 24], font=F, fill=(70, 70, 70))
        y += 20
    return img


def sheet(problems, name):
    tiles = [tile(p) for p in problems]
    cols, th = 4, FH + LH
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * TW, rows * th + 40), "white")
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * TW, 40 + (i // cols) * th))
    path = os.path.join(OUT, name)
    out.save(path)
    print("saved", path, f"({len(tiles)})")


def main():
    data = json.load(open(ROOT / "app/src/main/assets/problems_generated.json"))["problems"]
    figs = [p for p in data if "figure" in p]
    order = {t: i for i, t in enumerate(["GRID_POLYGON", "TRIANGLE_FAN", "CUBE_STACK", "POLYGON", "GRID", "L_SHAPE", "DOT_BORDER", "CLOCK"])}
    figs.sort(key=lambda p: order.get(p["figure"]["type"], 99))
    sheet(figs, "figures_all.png")


if __name__ == "__main__":
    main()

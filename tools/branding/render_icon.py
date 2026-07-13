#!/usr/bin/env python3
"""딱풀 런처 아이콘 실제 에셋 생성 — '아이디어 전구'(클레이).

산출:
  1) drawable-{d}/ic_launcher_foreground.png  — 전구(투명, 세이프존, 글로우/섀도 baked)
  2) mipmap-{d}/ic_launcher.webp / ic_launcher_round.webp — 레거시 폴백(합성/원형마스크)
  3) docs/store/icon-512.png — 플레이스토어 512 아이콘(합성)
배경(radial 그라데이션)·monochrome 실루엣 벡터는 XML로 별도 작성.
실행: venv/bin/python render_icon.py
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

REPO = str(Path(__file__).resolve().parents[2])
RES = f"{REPO}/app/src/main/res"
M = 1728                      # 마스터 해상도(108 * 16)
k = M / 108.0

VIOLET_DK  = (72, 63, 200)
VIOLET_LT  = (150, 143, 255)
AMBER      = (255, 194, 74)
BASE       = (196, 186, 214)
BASE_LN    = (150, 138, 175)
WHITE      = (255, 255, 255)

# 전구가 foreground 세이프존에서 차지할 지름 비율(=지름/108). 콘셉트(0.39)보다 약 +12%.
FRAC = 0.44
CY = 0.46                    # 전구 중심의 세로 위치(약간 위 — 아래 소켓 여유)


def px(x):
    return x * k


def L():
    return Image.new("RGBA", (M, M), (0, 0, 0, 0))


def rrect(d, box, r, fill):
    d.rounded_rectangle([px(box[0]), px(box[1]), px(box[2]), px(box[3])], radius=px(r), fill=fill)


def ellipse(d, cx, cy, rx, ry, fill):
    d.ellipse([px(cx - rx), px(cy - ry), px(cx + rx), px(cy + ry)], fill=fill)


def check(d, pts, color, w):
    xy = [(px(p[0]), px(p[1])) for p in pts]
    d.line(xy, fill=color, width=int(px(w)), joint="curve")
    rr = px(w) / 2
    for p in (xy[0], xy[-1]):
        d.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=color)


def shadow(shape_fn, blur, alpha, dy):
    lay = L()
    shape_fn(ImageDraw.Draw(lay), (0, 0, 0, alpha))
    return lay.filter(ImageFilter.GaussianBlur(px(blur))), (0, int(px(dy)))


def highlight(img, hl_fn, blur, alpha):
    lay = L()
    hl_fn(ImageDraw.Draw(lay), (255, 255, 255, alpha))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(px(blur))))


def draw_bulb_core(img):
    """전구 본체(그림자·소켓·유리·체크 필라멘트·광택). 글로우 제외 — 크기 기준."""
    sh, off = shadow(lambda d, c: ellipse(d, 54, 48, 21, 21, c), 7, 90, 6)
    img.alpha_composite(sh, off)
    d = ImageDraw.Draw(img)
    rrect(d, (47, 64, 61, 78), 4, BASE)                       # 소켓
    d.line([(px(47), px(69)), (px(61), px(69))], fill=BASE_LN, width=int(px(1.5)))
    d.line([(px(47), px(73)), (px(61), px(73))], fill=BASE_LN, width=int(px(1.5)))
    ellipse(d, 54, 47, 21, 21, AMBER)                         # 유리
    check(d, [(45, 48), (52, 57), (65, 38)], WHITE, 4)        # 체크 필라멘트
    highlight(img, lambda d, c: ellipse(d, 46, 39, 6, 9, c), 5, 170)   # 광택


def draw_glow(img):
    glow = L()
    ellipse(ImageDraw.Draw(glow), 54, 47, 26, 26, AMBER + (150,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(px(12))))


def bulb_sprites():
    """(글로우 포함 스프라이트, 본체 폭, 유리 중심) — 본체 지름으로 사이즈 결정."""
    core = L()
    draw_bulb_core(core)
    cb = core.getbbox()
    full = L()
    draw_glow(full)
    draw_bulb_core(full)
    fb = full.getbbox()
    sprite = full.crop(fb)
    gcx, gcy = px(54) - fb[0], px(47) - fb[1]                 # 유리중심 → 스프라이트 로컬
    core_w = cb[2] - cb[0]
    return sprite, core_w, (gcx, gcy)


def place_bulb(target, sprite, core_w, gc):
    """본체 폭이 target*FRAC 가 되도록 스케일, 유리중심을 (0.5, CY)에 정렬."""
    out = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    scale = (FRAC * target) / core_w
    s = sprite.resize((max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))), Image.LANCZOS)
    cx, cy = gc[0] * scale, gc[1] * scale
    out.alpha_composite(s, (int(target * 0.5 - cx), int(target * CY - cy)))
    return out


def radial_bg():
    img = Image.new("RGB", (M, M), VIOLET_DK)
    d = ImageDraw.Draw(img)
    cx, cy, maxr = M * 0.42, M * 0.36, M * 0.98
    for i in range(80, 0, -1):
        t = i / 80
        r = maxr * t
        c = tuple(int(VIOLET_DK[j] + (VIOLET_LT[j] - VIOLET_DK[j]) * (1 - t)) for j in range(3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    return img.convert("RGBA")


def circle_mask(img):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, img.size[0], img.size[1]], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out


def main():
    sprite, core_w, gc = bulb_sprites()
    fg_master = place_bulb(M, sprite, core_w, gc)             # foreground(투명)
    full = radial_bg()                                        # 합성 아이콘(풀블리드)
    full.alpha_composite(fg_master)

    # 1) foreground PNG (drawable-{d})
    fg_dens = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
    for d, sz in fg_dens.items():
        p = f"{RES}/drawable-{d}"
        os.makedirs(p, exist_ok=True)
        fg_master.resize((sz, sz), Image.LANCZOS).save(f"{p}/ic_launcher_foreground.png")

    # 2) 레거시 mipmap webp (square + round)
    mip_dens = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    for d, sz in mip_dens.items():
        full.resize((sz, sz), Image.LANCZOS).convert("RGB").save(f"{RES}/mipmap-{d}/ic_launcher.webp", "WEBP", quality=92)
        circle_mask(full.resize((sz, sz), Image.LANCZOS)).save(f"{RES}/mipmap-{d}/ic_launcher_round.webp", "WEBP", quality=92)

    # 3) 스토어 512
    os.makedirs(f"{REPO}/docs/store", exist_ok=True)
    full.resize((512, 512), Image.LANCZOS).convert("RGB").save(f"{REPO}/docs/store/icon-512.png")

    # 자기검증용 미리보기(원형 마스크)
    prev = circle_mask(full.resize((360, 360), Image.LANCZOS))
    flat = Image.new("RGB", (360, 360), (247, 247, 250))
    flat.paste(prev, (0, 0), prev)
    flat.save(os.environ.get("ICON_PREVIEW", "/tmp/ddakpul-icon-preview.png"))
    print("assets written. fg:", list(fg_dens), "| webp:", list(mip_dens), "| FRAC:", FRAC)


if __name__ == "__main__":
    main()

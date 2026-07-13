#!/usr/bin/env python3
"""딱풀 런처 아이콘 실제 에셋 생성 — '딱풀이' 마스코트(클레이).

산출:
  1) drawable-{d}/ic_launcher_foreground.png  — 마스코트(투명, 세이프존 안, 그림자 baked)
  2) mipmap-{d}/ic_launcher.webp / ic_launcher_round.webp — 레거시 폴백(합성/원형마스크)
  3) docs/store/icon-512.png — 플레이스토어 512 아이콘(합성)
배경(radial 그라데이션)·monochrome 실루엣 벡터는 XML로 별도 작성.
실행: venv/bin/python render_icon_assets.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter

from pathlib import Path
REPO = str(Path(__file__).resolve().parents[2])
RES = f"{REPO}/app/src/main/res"
M = 1728                      # 마스터 해상도(108 * 16)
k = M / 108.0

VIOLET_DK  = (72, 63, 200)
VIOLET_LT  = (150, 143, 255)
CREAM      = (255, 251, 243)
CAP_MINT   = (54, 214, 178)
CAP_MINT_D = (28, 150, 122)
MINT       = (52, 210, 172)
CHEEK      = (255, 158, 158)
INK        = (66, 58, 128)
WHITE      = (255, 255, 255)


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


def draw_mascot(img):
    """render_icon_v2.concept_mascot과 동일 좌표(108-space)를 투명 캔버스에."""
    sh, off = shadow(lambda d, c: rrect(d, (37, 40, 73, 88), 14, c), 7, 110, 5)
    img.alpha_composite(sh, off)
    d = ImageDraw.Draw(img)
    rrect(d, (48, 20, 62, 30), 5, (245, 238, 226))            # 글루 nib
    rrect(d, (37, 27, 73, 46), 9, CAP_MINT)                   # 캡
    d.line([(px(37), px(43)), (px(73), px(43))], fill=CAP_MINT_D, width=int(px(1.6)))
    rrect(d, (37, 42, 73, 88), 14, CREAM)                     # 몸통
    rrect(d, (37, 62, 73, 71), 0, (241, 234, 223))            # 라벨 밴드
    ellipse(d, 47.5, 55, 3.5, 4.2, INK)                       # 눈
    ellipse(d, 62.5, 55, 3.5, 4.2, INK)
    ellipse(d, 48.9, 53.5, 1.2, 1.5, WHITE)
    ellipse(d, 63.9, 53.5, 1.2, 1.5, WHITE)
    ellipse(d, 42, 60, 2.8, 1.9, CHEEK)                       # 볼
    ellipse(d, 68, 60, 2.8, 1.9, CHEEK)
    d.arc([px(50), px(57.5), px(60), px(66)], 20, 160, fill=INK, width=int(px(2.0)))   # 입
    highlight(img, lambda d, c: ellipse(d, 47, 33, 7, 3.2, c), 4, 150)
    highlight(img, lambda d, c: rrect(d, (41, 46, 48, 84), 5, c), 5, 85)
    sh2, o2 = shadow(lambda d, c: ellipse(d, 74, 77, 12, 12, c), 5, 90, 3)             # 배지 그림자
    img.alpha_composite(sh2, o2)
    d2 = ImageDraw.Draw(img)
    ellipse(d2, 74, 77, 11, 11, MINT)                         # 정답 배지
    check(d2, [(69, 77), (73, 82), (80, 72)], WHITE, 3)


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


def sprite():
    """마스코트만 그려 알파 bbox로 크롭한 스프라이트."""
    canvas = L()
    draw_mascot(canvas)
    return canvas.crop(canvas.getbbox())


def place(target_size, spr, frac, cy_frac=0.5):
    """스프라이트를 target(정사각)에 frac 폭으로 중앙 배치(투명 배경)."""
    out = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    w = int(target_size * frac)
    h = int(spr.height * w / spr.width)
    s = spr.resize((w, h), Image.LANCZOS)
    out.alpha_composite(s, ((target_size - w) // 2, int(target_size * cy_frac) - h // 2))
    return out


def circle_mask(img):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, img.size[0], img.size[1]], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out


def main():
    spr = sprite()
    FRAC = 0.60          # 세이프존(≈66/108) 안에 들도록
    # 마스터 합성 아이콘(풀블리드)
    full = radial_bg()
    full.alpha_composite(place(M, spr, FRAC, 0.49))

    # 1) foreground PNG (drawable-{d}), 108dp 캔버스에 세이프존 배치
    fg_dens = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
    fg_master = place(M, spr, FRAC, 0.49)
    for d, sz in fg_dens.items():
        p = f"{RES}/drawable-{d}"
        os.makedirs(p, exist_ok=True)
        fg_master.resize((sz, sz), Image.LANCZOS).save(f"{p}/ic_launcher_foreground.png")

    # 2) 레거시 mipmap webp (square + round)
    mip_dens = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    for d, sz in mip_dens.items():
        sq = full.resize((sz, sz), Image.LANCZOS).convert("RGB")
        sq.save(f"{RES}/mipmap-{d}/ic_launcher.webp", "WEBP", quality=92)
        rd = circle_mask(full.resize((sz, sz), Image.LANCZOS))
        rd.save(f"{RES}/mipmap-{d}/ic_launcher_round.webp", "WEBP", quality=92)

    # 3) 스토어 512
    os.makedirs(f"{REPO}/docs/store", exist_ok=True)
    full.resize((512, 512), Image.LANCZOS).convert("RGB").save(f"{REPO}/docs/store/icon-512.png")

    # 자기검증용 미리보기(원형 마스크 씌운 최종 모습)
    prev = circle_mask(full.resize((360, 360), Image.LANCZOS))
    flat = Image.new("RGB", (360, 360), (247, 247, 250))
    flat.paste(prev, (0, 0), prev)
    flat.save("/private/tmp/claude-501/-Users-na982-claude-DDAKPUL/77a69bb6-b868-4ead-9958-5b2c15ddbd10/scratchpad/icon_final_preview.png")
    print("assets written. fg densities:", list(fg_dens), "| webp:", list(mip_dens))


if __name__ == "__main__":
    main()

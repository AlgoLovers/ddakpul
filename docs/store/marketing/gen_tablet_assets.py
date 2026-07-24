# -*- coding: utf-8 -*-
"""딱풀 태블릿(가로) 마케팅 스크린샷 생성.

Google Play 태블릿 규격: 가로세로 16:9(또는 9:16), 짧은 변 1080~7680px.
→ 2160x1215(16:9, 짧은 변 1215px)로 렌더. 소스(1280px)보다 축소라 선명하다.
레이아웃은 1600x1000 기준 설계를 S배 스케일(s()). 세로 위치는 H 비율로 잡아 16:9에 맞춘다.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "screenshots", "tablet")
OUT = HERE  # 커밋된 tab1~3.png을 규격 맞게 덮어쓴다
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

W, H = 2160, 1215                 # 16:9, 짧은 변 1215 ≥ 1080
S = W / 1600.0                    # 1600 기준 설계 → 스케일


def s(x):
    return round(x * S)


def f(size):
    return ImageFont.truetype(FONT, s(size))


INDIGO = (74, 73, 196); PERI = (108, 100, 225); PERI_LT = (142, 134, 238)
MINT = (150, 235, 200); AMBER = (240, 186, 74); WHITE = (255, 255, 255)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(w, h, top, bot):
    img = Image.new("RGB", (w, h), top); d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bot, y / max(1, h - 1)))
    return img


def wrap(draw, text, font, maxw):
    words = text.split(" "); lines = []; cur = ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def frame_shot(name, crop_bottom=70):
    shot = Image.open(os.path.join(SRC, name)).convert("RGB")
    w, h = shot.size
    shot = shot.crop((0, 0, w, h - crop_bottom))     # 하단 시스템 태스크바 제거
    tw = s(940); th = int(tw * shot.height / shot.width)
    shot = shot.resize((tw, th), Image.LANCZOS)
    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw, th], radius=s(40), fill=255)
    return shot, mask, tw, th


def panel(idx, name, headline, sub, top, bot):
    bg = vgrad(W, H, top, bot); d = ImageDraw.Draw(bg)
    shot, mask, tw, th = frame_shot(name)
    sx = W - tw - s(70); sy = (H - th) // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([sx, sy + s(18), sx + tw, sy + th + s(18)], radius=s(40), fill=(20, 18, 60, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(s(34))); bg.paste(sh, (0, 0), sh)
    bg.paste(shot, (sx, sy), mask)
    hf = f(76); sf = f(37)
    hlines = headline.split("\n")
    asc, desc = hf.getmetrics(); lh = int((asc + desc) * 1.12)
    slines = wrap(d, sub, sf, sx - s(120))
    total = len(hlines) * lh + s(24) + len(slines) * s(54)
    y = (H - total) // 2
    for ln in hlines:
        d.text((s(70), y), ln, font=hf, fill=WHITE, stroke_width=1, stroke_fill=(50, 48, 120)); y += lh
    y += s(24)
    for ln in slines:
        d.text((s(72), y), ln, font=sf, fill=(230, 228, 255)); y += s(54)
    bg.save(os.path.join(OUT, f"tab{idx}.png"))


panel(1, "02-solve.png", "5분 생각하는\n사고력 문제", "계산 드릴이 아니라, 연습장 펴고 푸는 문제", PERI, INDIGO)
panel(2, "03-report.png", "부모를 위한\n성장 리포트", "'다음 한 걸음'까지 알려주는 코칭", PERI_LT, PERI)


def trust():
    bg = vgrad(W, H, INDIGO, (48, 46, 140)); d = ImageDraw.Draw(bg)
    cx = W // 2
    by = round(H * 0.25)          # 세로 위치는 H 비율
    r = s(92)
    d.ellipse([cx - r, by - r, cx + r, by + r], fill=AMBER)
    d.rounded_rectangle([cx - s(34), by + s(74), cx + s(34), by + s(126)], radius=s(14), fill=(214, 210, 235))
    d.line([(cx - s(42), by + s(4)), (cx - s(12), by + s(38)), (cx + s(50), by - s(44))], fill=WHITE, width=s(22), joint="curve")
    hf = f(78); t = "믿고 맡기는 학습"; w = d.textlength(t, font=hf)
    d.text((cx - w / 2, round(H * 0.44)), t, font=hf, fill=WHITE, stroke_width=1, stroke_fill=(40, 38, 110))
    chips = ["완전 무료", "광고 없음", "오프라인 학습", "아동 데이터 수집 0"]
    cf = f(50); gap = s(34)
    ws = [d.textlength(c, font=cf) + s(80) for c in chips]
    totalw = sum(ws) + gap * (len(chips) - 1); x = (W - totalw) // 2
    cy = round(H * 0.60); ch = s(104)
    for c, cw in zip(chips, ws):
        d.rounded_rectangle([x, cy, x + cw, cy + ch], radius=s(52), fill=WHITE)
        tw = d.textlength(c, font=cf); d.text((x + (cw - tw) / 2, cy + s(22)), c, font=cf, fill=INDIGO)
        x += cw + gap
    sf = f(40); sub = "계정 없이, 인터넷 없이도 기기 안에서 모두 완결됩니다"
    w = d.textlength(sub, font=sf); d.text((cx - w / 2, round(H * 0.77)), sub, font=sf, fill=(222, 220, 250))
    bg.save(os.path.join(OUT, "tab3.png"))


trust()
print(f"태블릿 생성 완료({W}x{H}):", [x for x in sorted(os.listdir(OUT)) if x.startswith("tab") and x.endswith(".png")])

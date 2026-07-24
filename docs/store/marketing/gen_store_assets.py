# -*- coding: utf-8 -*-
"""딱풀 스토어 마케팅 자산 생성 (PIL). 시장조사 규칙 반영."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "/Users/na982/claude/DDAKPUL/docs/store"
OUT = "/private/tmp/claude-501/-Users-na982-claude-DDAKPUL/d7d914b5-a280-480f-8f16-48e981f03a2d/scratchpad/marketing"
os.makedirs(OUT, exist_ok=True)

FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
def f(size, index=0):
    return ImageFont.truetype(FONT, size, index=index)

# 브랜드 팔레트
INDIGO   = (74, 73, 196)
PERI     = (108, 100, 225)
PERI_LT  = (142, 134, 238)
LAV      = (245, 243, 255)
MINT     = (150, 235, 200)
AMBER    = (240, 186, 74)
INK      = (38, 38, 60)
WHITE    = (255, 255, 255)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def vgrad(w, h, top, bot):
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bot, y/max(1, h-1)))
    return img

def wrap(draw, text, font, maxw):
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines

def text_center(draw, cx, y, text, font, fill, stroke=0, stroke_fill=None, ls=1.16):
    lines = text.split("\n")
    asc, desc = font.getmetrics()
    lh = int((asc+desc)*ls)
    for i, ln in enumerate(lines):
        w = draw.textlength(ln, font=font)
        draw.text((cx - w/2, y + i*lh), ln, font=font, fill=fill,
                  stroke_width=stroke, stroke_fill=stroke_fill)
    return y + len(lines)*lh

def rounded_card(shot, pad=0, radius=54):
    """스크린샷을 흰 카드에 라운드 + 그림자."""
    w, h = shot.size
    card = Image.new("RGB", (w, h), WHITE)
    card.paste(shot, (0, 0))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    return card, mask

def paste_with_shadow(bg, card, mask, pos, blur=38, sh_alpha=110, dy=22):
    x, y = pos
    w, h = card.size
    shadow = Image.new("RGBA", bg.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([x, y+dy, x+w, y+h+dy], radius=54, fill=(20,18,60, sh_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    bg.paste(shadow, (0,0), shadow)
    bg.paste(card, (x, y), mask)

# ---------- 폰 마케팅 스크린샷 ----------
PANELS = [
    ("02-solve-figure.png",      "5분 생각하는\n사고력 문제",        "계산 드릴이 아니라, 연습장 펴고 푸는 문제"),
    ("03-result-explanation.png","실력 따라\n다음 문제 자동 추천",   "단계별·심화 풀이로 이해까지"),
    ("04-report-level.png",      "부모를 위한\n성장 리포트",         "'다음 한 걸음'까지 알려주는 코칭"),
    ("05-report-areas.png",      "네 영역\n강점·약점 한눈에",        "어디가 강하고 어디를 더 볼지"),
]

def make_panel(idx, shot_name, headline, sub, top, bot):
    W, H = 1080, 1920
    bg = vgrad(W, H, top, bot)
    d = ImageDraw.Draw(bg)
    # 캡션
    y = 96
    hl = f(78)
    y = text_center(d, W//2, y, headline, hl, WHITE, stroke=1, stroke_fill=(50,48,120), ls=1.14)
    sf = f(37)
    for ln in wrap(d, sub, sf, 860):
        w = d.textlength(ln, font=sf)
        d.text((W/2 - w/2, y+8), ln, font=sf, fill=(232,230,255))
        y += 52
    # 스크린샷 카드
    shot = Image.open(os.path.join(SRC, "screenshots/phone", shot_name)).convert("RGB")
    tw = 812
    th = int(tw * shot.height / shot.width)
    shot = shot.resize((tw, th), Image.LANCZOS)
    card, mask = rounded_card(shot, radius=48)
    x = (W - tw)//2
    yc = 470
    paste_with_shadow(bg, card, mask, (x, yc))
    bg.save(os.path.join(OUT, f"ss{idx}.png"))

grads = [(PERI, INDIGO), (PERI_LT, PERI), (INDIGO, PERI), (PERI, INDIGO)]
for i, (sn, hl, sub) in enumerate(PANELS, 1):
    make_panel(i, sn, hl, sub, *grads[i-1])

# 패널 6: 신뢰 슬라이드 (스크린샷 없음)
def make_trust():
    W, H = 1080, 1920
    bg = vgrad(W, H, INDIGO, (48,46,140))
    d = ImageDraw.Draw(bg)
    # 전구 심볼
    cx, cy = W//2, 430
    d.ellipse([cx-120, cy-120, cx+120, cy+120], fill=AMBER)
    d.rounded_rectangle([cx-44, cy+96, cx+44, cy+168], radius=18, fill=(214,210,235))
    # 체크
    d.line([(cx-52, cy+6),(cx-14, cy+48),(cx+66, cy-52)], fill=WHITE, width=26, joint="curve")
    y = text_center(d, cx, 660, "믿고 맡기는 학습", f(78), WHITE, stroke=1, stroke_fill=(40,38,110))
    chips = ["완전 무료", "광고 없음", "오프라인 학습", "아동 데이터 수집 0"]
    cf = f(58)
    yy = 830
    for c in chips:
        w = d.textlength(c, font=cf)
        pad = 46
        cw = w + pad*2
        x0 = (W-cw)//2
        d.rounded_rectangle([x0, yy, x0+cw, yy+118], radius=59, fill=(255,255,255,255))
        d.text((W/2 - w/2, yy+26), c, font=cf, fill=INDIGO)
        yy += 158
    text_center(d, cx, yy+30, "계정 없이, 인터넷 없이도\n기기 안에서 모두 완결됩니다", f(40), (222,220,250), ls=1.3)
    bg.save(os.path.join(OUT, "ss5.png"))
make_trust()

# ---------- 피처그래픽 1024x500 ----------
def make_feature():
    W, H = 1024, 500
    bg = vgrad(W, H, PERI, INDIGO)
    d = ImageDraw.Draw(bg)
    # 우측 비주얼: 격자 + 기울어진 사각형 (도형 문제 모티프) + 전구
    import math
    gx, gy, cell = 690, 150, 55
    for i in range(5):
        d.line([(gx, gy+i*cell),(gx+4*cell, gy+i*cell)], fill=(255,255,255,60), width=2)
        d.line([(gx+i*cell, gy),(gx+i*cell, gy+4*cell)], fill=(255,255,255,60), width=2)
    # 기울어진 사각형
    ccx, ccy, r = gx+2*cell, gy+2*cell, 118
    pts = []
    for a in [25, 115, 205, 295]:
        pts.append((ccx + r*math.cos(math.radians(a)), ccy + r*math.sin(math.radians(a))))
    d.polygon(pts, fill=(150,235,200,90), outline=WHITE)
    d.line(pts+[pts[0]], fill=WHITE, width=5, joint="curve")
    # 전구 (우상단)
    bx, by = 930, 96
    d.ellipse([bx-46, by-46, bx+46, by+46], fill=AMBER)
    d.rounded_rectangle([bx-17, by+38, bx+17, by+64], radius=7, fill=(214,210,235))
    # 좌측 텍스트 (가장자리·중앙 회피)
    d.text((70, 116), "딱풀", font=f(150), fill=WHITE)
    d.text((78, 292), "초등 사고력 수학", font=f(56), fill=(226,224,252))
    d.text((80, 372), "딱 맞는 문제로, 생각의 힘을", font=f(44), fill=MINT)
    bg.save(os.path.join(OUT, "feature.png"))
make_feature()

# ---------- 아이콘 컨셉 2종 512 ----------
def rrect_bg(size, top, bot, radius=110):
    img = vgrad(size, size, top, bot)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,size,size], radius=radius, fill=255)
    out = Image.new("RGB", (size, size), WHITE)
    out.paste(img, (0,0), mask)
    return out

def icon_A():  # 밝은 전구+체크 (현행 개선: 더 밝고 따뜻하게)
    S = 512
    img = rrect_bg(S, PERI_LT, PERI)
    d = ImageDraw.Draw(img)
    cx, cy = 256, 232
    # 후광
    glow = Image.new("RGBA", (S,S), (0,0,0,0))
    ImageDraw.Draw(glow).ellipse([cx-150, cy-150, cx+150, cy+150], fill=(255,255,255,40))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(30))).convert("RGB"),(0,0))
    d = ImageDraw.Draw(img)
    d.ellipse([cx-108, cy-108, cx+108, cy+108], fill=AMBER)
    d.rounded_rectangle([cx-40, cy+92, cx+40, cy+150], radius=16, fill=(224,220,242))
    d.line([cx-8, cy+104, cx-8, cy+150], fill=(150,146,180), width=4)
    d.line([(cx-56, cy+6),(cx-18, cy+48),(cx+60, cy-56)], fill=WHITE, width=30, joint="curve")
    img.save(os.path.join(OUT, "icon-conceptA.png"))

def icon_B():  # 전구+퍼즐조각 (todo 오인 제거, 사고력 시그널)
    S = 512
    img = rrect_bg(S, INDIGO, PERI)
    d = ImageDraw.Draw(img)
    cx, cy = 256, 226
    d.ellipse([cx-112, cy-112, cx+112, cy+112], fill=AMBER)
    d.rounded_rectangle([cx-42, cy+96, cx+42, cy+156], radius=16, fill=(224,220,242))
    d.line([cx-8, cy+108, cx-8, cy+156], fill=(150,146,180), width=4)
    # 퍼즐 조각 (흰색, 전구 안)
    ps = 96
    px, py = cx-ps//2, cy-ps//2-6
    d.rounded_rectangle([px, py, px+ps, py+ps], radius=18, fill=WHITE)
    d.ellipse([cx+ps//2-22, cy-24, cx+ps//2+24, cy+22], fill=WHITE)          # 우측 볼록
    d.ellipse([cx-24, py-24, cx+24, py+22], fill=WHITE)                      # 상단 볼록
    d.ellipse([px-24, cy-24, px+22, cy+22], fill=AMBER)                      # 좌측 오목
    img.save(os.path.join(OUT, "icon-conceptB.png"))

icon_A(); icon_B()

print("생성 완료:", sorted(os.listdir(OUT)))

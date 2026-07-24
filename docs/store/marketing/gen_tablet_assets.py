# -*- coding: utf-8 -*-
"""딱풀 태블릿(가로) 마케팅 스크린샷 생성."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "/Users/na982/claude/DDAKPUL/docs/store/screenshots/tablet"
OUT = "/private/tmp/claude-501/-Users-na982-claude-DDAKPUL/d7d914b5-a280-480f-8f16-48e981f03a2d/scratchpad/marketing"
os.makedirs(OUT, exist_ok=True)
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
def f(size): return ImageFont.truetype(FONT, size)

INDIGO=(74,73,196); PERI=(108,100,225); PERI_LT=(142,134,238)
MINT=(150,235,200); AMBER=(240,186,74); WHITE=(255,255,255)

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def vgrad(w,h,top,bot):
    img=Image.new("RGB",(w,h),top); d=ImageDraw.Draw(img)
    for y in range(h): d.line([(0,y),(w,y)],fill=lerp(top,bot,y/max(1,h-1)))
    return img
def wrap(draw,text,font,maxw):
    words=text.split(" "); lines=[]; cur=""
    for wd in words:
        t=(cur+" "+wd).strip()
        if draw.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=wd
    if cur: lines.append(cur)
    return lines

W,H=1600,1000
def frame_shot(name, crop_bottom=70):
    shot=Image.open(os.path.join(SRC,name)).convert("RGB")
    w,h=shot.size
    shot=shot.crop((0,0,w,h-crop_bottom))           # 하단 시스템 태스크바 제거
    tw=940; th=int(tw*shot.height/shot.width)
    shot=shot.resize((tw,th),Image.LANCZOS)
    mask=Image.new("L",(tw,th),0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,tw,th],radius=40,fill=255)
    return shot,mask,tw,th

def panel(idx, name, headline, sub, top, bot):
    bg=vgrad(W,H,top,bot); d=ImageDraw.Draw(bg)
    shot,mask,tw,th=frame_shot(name)
    sx=W-tw-70; sy=(H-th)//2
    sh=Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(sh).rounded_rectangle([sx,sy+18,sx+tw,sy+th+18],radius=40,fill=(20,18,60,120))
    sh=sh.filter(ImageFilter.GaussianBlur(34)); bg.paste(sh,(0,0),sh)
    bg.paste(shot,(sx,sy),mask)
    # 좌측 캡션 (좌정렬, 세로 중앙)
    hf=f(76); sf=f(37)
    hlines=headline.split("\n")
    asc,desc=hf.getmetrics(); lh=int((asc+desc)*1.12)
    slines=wrap(d,sub,sf,sx-120)
    total=len(hlines)*lh+24+len(slines)*54
    y=(H-total)//2
    for ln in hlines:
        d.text((70,y),ln,font=hf,fill=WHITE,stroke_width=1,stroke_fill=(50,48,120)); y+=lh
    y+=24
    for ln in slines:
        d.text((72,y),ln,font=sf,fill=(230,228,255)); y+=54
    bg.save(os.path.join(OUT,f"tab{idx}.png"))

panel(1,"02-solve.png","5분 생각하는\n사고력 문제","계산 드릴이 아니라, 연습장 펴고 푸는 문제",PERI,INDIGO)
panel(2,"03-report.png","부모를 위한\n성장 리포트","'다음 한 걸음'까지 알려주는 코칭",PERI_LT,PERI)

# 신뢰 슬라이드 (가로)
def trust():
    bg=vgrad(W,H,INDIGO,(48,46,140)); d=ImageDraw.Draw(bg)
    cx=W//2
    # 전구
    by=250
    d.ellipse([cx-92,by-92,cx+92,by+92],fill=AMBER)
    d.rounded_rectangle([cx-34,by+74,cx+34,by+126],radius=14,fill=(214,210,235))
    d.line([(cx-42,by+4),(cx-12,by+38),(cx+50,by-44)],fill=WHITE,width=22,joint="curve")
    hf=f(78); t="믿고 맡기는 학습"; w=d.textlength(t,font=hf)
    d.text((cx-w/2,440),t,font=hf,fill=WHITE,stroke_width=1,stroke_fill=(40,38,110))
    chips=["완전 무료","광고 없음","오프라인 학습","아동 데이터 수집 0"]
    cf=f(50); gap=34; xs=[]
    ws=[d.textlength(c,font=cf)+80 for c in chips]
    totalw=sum(ws)+gap*(len(chips)-1); x=(W-totalw)//2
    for c,cw in zip(chips,ws):
        d.rounded_rectangle([x,600,x+cw,704],radius=52,fill=WHITE)
        tw=d.textlength(c,font=cf); d.text((x+(cw-tw)/2,622),c,font=cf,fill=INDIGO)
        x+=cw+gap
    sf=f(40); s="계정 없이, 인터넷 없이도 기기 안에서 모두 완결됩니다"
    w=d.textlength(s,font=sf); d.text((cx-w/2,770),s,font=sf,fill=(222,220,250))
    bg.save(os.path.join(OUT,"tab3.png"))
trust()
print("태블릿 생성 완료:", [x for x in sorted(os.listdir(OUT)) if x.startswith("tab")])

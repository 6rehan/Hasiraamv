# RILO SOLO techno logo: line-art helmet icon with a glowing visor, spaced wordmark sliced by a scanline
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S=2048; C=S//2; W=(236,240,248); CY=(120,210,255)
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',200)
def glow(base,layer,r,amt):
    a=np.array(base,float)+np.array(layer.filter(ImageFilter.GaussianBlur(r)),float)*amt
    return Image.fromarray(np.clip(a,0,255).astype('uint8'))
def icon(d,cx,cy,s):
    L=int(18*s)
    d.ellipse([cx-300*s,cy-260*s,cx+300*s,cy+360*s],outline=W,width=L)                 # helmet
    d.arc([cx-320*s,cy-340*s,cx+330*s,cy+240*s],190,335,fill=W,width=L)                  # pompadour sweep
    d.line([(cx+260*s,cy-230*s),(cx+440*s,cy-330*s),(cx+300*s,cy-120*s)],fill=W,width=L,joint='curve')
    d.polygon([(cx-80*s,cy+150*s),(cx+80*s,cy+150*s),(cx,cy+330*s)],outline=W,width=L)   # beak
def visor(d,cx,cy,s): d.rounded_rectangle([cx-230*s,cy+10*s,cx+230*s,cy+70*s],radius=int(30*s),fill=CY)
def wordmark(img,cx,cy,spacing):
    d=ImageDraw.Draw(img); txt="RILO SOLO"; ws=[d.textlength(ch,font=F) for ch in txt]
    total=sum(ws)+spacing*(len(txt)-1); x=cx-total/2
    for ch,w in zip(txt,ws): d.text((x,cy),ch,font=F,fill=W,anchor='lm'); x+=w+spacing
    d.rectangle([cx-total/2-40,cy-8,cx+total/2+40,cy+8],fill=(8,8,12))                    # scanline slice
    d.line([(cx-total/2-40,cy),(cx+total/2+40,cy)],fill=CY,width=4)
def render(w,h,layout,name):
    img=Image.new('RGB',(w,h),(8,8,12)); d=ImageDraw.Draw(img)
    g=Image.new('RGB',(w,h)); gd=ImageDraw.Draw(g)
    if layout=='stack':
        icon(d,w//2,760,1.25); visor(d,w//2,760,1.25); visor(gd,w//2,760,1.25); wordmark(img,w//2,1640,34)
        gd.line([(w//2-700,1640),(w//2+700,1640)],fill=CY,width=6)
    elif layout=='wide':
        icon(d,520,h//2-30,.95); visor(d,520,h//2-30,.95); visor(gd,520,h//2-30,.95); wordmark(img,1900,h//2,26)
        gd.line([(1200,h//2),(2600,h//2)],fill=CY,width=6)
    else:
        icon(d,w//2,w//2-60,1.9); visor(d,w//2,w//2-60,1.9); visor(gd,w//2,w//2-60,1.9)
    img=glow(img,g,50,1.4); img=glow(img,g,12,0.8)
    img.save(name); return img
render(S,S,'stack','rilo_solo_logo.png').resize((600,600)).save('prev_logo.jpg')
render(3000,1000,'wide','rilo_solo_logo_wide.png').resize((900,300)).save('prev_wide.jpg')
render(S,S,'icon','rilo_solo_icon.png')
print('ok')

# Cover art for "Late Night Scroll" - 3000x3000 (streaming-platform size)
import numpy as np, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S=3000; rng=random.Random(7)
y=np.linspace(0,1,S)[:,None]
top=np.array([14,12,40]); bot=np.array([58,28,88])
bg=(top*(1-y[...,None])+bot*y[...,None]).repeat(S,1).astype(np.uint8)
img=Image.fromarray(bg,'RGB')
# city bokeh behind window
bok=Image.new('RGB',(S,S)); d=ImageDraw.Draw(bok)
for _ in range(260):
    x=rng.randint(300,2700); yy=rng.randint(500,1900); r=rng.randint(20,110)
    c=rng.choice([(170,120,255),(255,140,200),(120,170,255),(255,200,140)])
    d.ellipse([x-r,yy-r,x+r,yy+r],fill=tuple(int(v*rng.uniform(.25,.6)) for v in c))
img=Image.fromarray(np.clip(np.array(img,int)+np.array(bok.filter(ImageFilter.GaussianBlur(28)),int),0,255).astype(np.uint8))
d=ImageDraw.Draw(img)
# window frame
d.rectangle([250,380,2750,2050],outline=(20,16,38),width=60); d.line([1500,380,1500,2050],fill=(20,16,38),width=45)
# rain streaks
rain=Image.new('L',(S,S)); rd=ImageDraw.Draw(rain)
for _ in range(900):
    x=rng.randint(280,2720); yy=rng.randint(410,2000); l=rng.randint(20,90)
    rd.line([x,yy,x-4,yy+l],fill=rng.randint(60,150),width=3)
img.paste((200,200,255),mask=rain.filter(ImageFilter.GaussianBlur(1.5)))
# bed + silhouette
d.rectangle([0,2250,S,S],fill=(10,8,22))
d.ellipse([1260,1500,1640,1880],fill=(8,6,18))                  # head
d.polygon([(1100,2600),(1180,1950),(1450,1820),(1720,1950),(1800,2600)],fill=(8,6,18))  # hoodie body
# phone glow
glow=Image.new('RGB',(S,S)); gd=ImageDraw.Draw(glow)
gd.ellipse([1150,1450,1750,2150],fill=(70,120,255))
img=Image.fromarray(np.clip(np.array(img,int)+np.array(glow.filter(ImageFilter.GaussianBlur(160)),int)*0.55,0,255).astype(np.uint8))
d=ImageDraw.Draw(img)
d.rounded_rectangle([1520,1930,1600,2070],radius=12,fill=(170,205,255))
# film grain
g=np.random.default_rng(3).normal(0,9,(S,S,1))
img=Image.fromarray(np.clip(np.array(img,float)+g,0,255).astype(np.uint8))
d=ImageDraw.Draw(img)
f=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',190)
t="late night scroll"; w=d.textlength(t,font=f); d.text(((S-w)/2,2640),t,font=f,fill=(236,232,255))
f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',58)
t2="2 : 0 0   A . M ."; w2=d.textlength(t2,font=f2); d.text(((S-w2)/2,2560),t2,font=f2,fill=(170,160,220))
img.save('cover_art.png'); img.resize((1000,1000)).save('cover_art_small.jpg',quality=90); print('ok')

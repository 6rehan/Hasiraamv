# CROWE mascot helmet: black-and-white greaser crow mask with a glowing pompadour, 2048px
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S=2048; C=S//2
img=Image.new('RGB',(S,S),(10,10,12)); d=ImageDraw.Draw(img)
glow=Image.new('RGB',(S,S)); gd=ImageDraw.Draw(glow)
gd.ellipse([C-760,C-700,C+760,C+820],fill=(90,90,110)); img=Image.blend(img,Image.composite(glow.filter(ImageFilter.GaussianBlur(200)),img,Image.new('L',(S,S),255)),.5); d=ImageDraw.Draw(img)
W=(242,242,238); K=(12,12,14)
# helmet head
d.ellipse([C-520,C-420,C+520,C+640],fill=W)
# pompadour: glossy black swoop
d.chord([C-580,C-640,C+600,C+80],180,360,fill=K)
d.polygon([(C+400,C-300),(C+720,C-460),(C+560,C-180)],fill=K)
d.arc([C-420,C-540,C+480,C-80],200,320,fill=(80,80,90),width=26)   # shine
# beak
d.polygon([(C-150,C+200),(C+150,C+200),(C,C+520)],fill=K)
d.line([(C-150,C+200),(C+150,C+200)],fill=(60,60,66),width=14)
# X eyes (deadmau5-like simplicity, but its own shape: glowing slits)
eg=Image.new('RGB',(S,S)); ed=ImageDraw.Draw(eg)
for sx in(-1,1):
    x=C+sx*260; ed.rounded_rectangle([x-150,C-20,x+150,C+60],radius=40,fill=(170,220,255))
img=Image.fromarray(__import__('numpy').clip(__import__('numpy').array(img,int)+__import__('numpy').array(eg.filter(ImageFilter.GaussianBlur(40)),int),0,255).astype('uint8'))
d=ImageDraw.Draw(img)
for sx in(-1,1):
    x=C+sx*260; d.rounded_rectangle([x-150,C-20,x+150,C+60],radius=40,fill=(225,245,255))
# leather collar
d.polygon([(C-560,S),(C-420,C+560),(C-120,C+700),(C,S)],fill=K)
d.polygon([(C+560,S),(C+420,C+560),(C+120,C+700),(C,S)],fill=K)
d.line([(C-300,C+640),(C-200,S)],fill=(150,150,160),width=12)
img.save('crowe_pfp.png'); img.resize((600,600)).save('prev_crowe.jpg'); print('ok')

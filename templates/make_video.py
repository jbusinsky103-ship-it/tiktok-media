"""Usage: python3 make_video.py scenes.json out.mp4
scenes.json: {"scenes":[{"tag":"warning","lines":[["Text line\\nsecond line","serif_italic",92,"white"]],"dur":3.0}, ...],
              "cover": true}   # cover=true appends book-cover CTA end card (4.5s)
font keys: serif, serif_italic, serif_bold_italic, sans, sans_bold ; colors: white, red, gray
Renders 1080x1920 30fps silent MP4 in the dark red/black brand style."""
import sys, json, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
HERE=os.path.dirname(os.path.abspath(__file__))
FONTS={"serif":"/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
 "serif_italic":"/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
 "serif_bold_italic":"/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
 "sans":"/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
 "sans_bold":"/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"}
COL={"white":(245,240,235),"red":(214,34,0),"gray":(130,130,130)}
def base():
    im=Image.new("RGB",(W,H),(4,4,4)); g=Image.new("L",(W,H),0)
    ImageDraw.Draw(g).ellipse((W/2-700,H*.42-700,W/2+700,H*.42+700),fill=90)
    im=Image.composite(Image.new("RGB",(W,H),(70,0,0)),im,g.filter(ImageFilter.GaussianBlur(220)))
    d=ImageDraw.Draw(im)
    for x,y,sx,sy in [(60,60,1,1),(W-60,60,-1,1),(60,H-60,1,-1),(W-60,H-60,-1,-1)]:
        d.line([(x,y),(x+50*sx,y)],fill=(60,0,0),width=2); d.line([(x,y),(x,y+50*sy)],fill=(60,0,0),width=2)
    return im
def ctext(d,y,t,f,c):
    for ln in t.split("\n"):
        w=d.textbbox((0,0),ln,font=f)[2]; d.text(((W-w)/2,y),ln,font=f,fill=c); y+=int(f.size*1.25)
    return y
def scene(s):
    im=base(); d=ImageDraw.Draw(im)
    ls=[(t,ImageFont.truetype(FONTS[f],sz),COL[c]) for t,f,sz,c in s["lines"]]
    tot=sum(int(f.size*1.25)*len(t.split("\n"))+40 for t,f,c in ls)+90; y=(H-tot)//2
    tf=ImageFont.truetype(FONTS["sans_bold"],30); tg=" ".join(s.get("tag","").upper())
    d.text(((W-d.textbbox((0,0),tg,font=tf)[2])/2,y),tg,font=tf,fill=(150,20,0)); y+=90
    for t,f,c in ls: y=ctext(d,y,t,f,c)+40
    return im
def cover_frame(cov,p):
    im=base(); s=1+.04*p; c=cov.resize((int(cov.width*s),int(cov.height*s)))
    cx=(W-c.width)//2; cy=230-(c.height-cov.height)//2
    g=Image.new("L",(W,H),0); ImageDraw.Draw(g).rectangle((cx-30,cy-30,cx+c.width+30,cy+c.height+30),fill=140)
    im=Image.composite(Image.new("RGB",(W,H),(120,0,0)),im,g.filter(ImageFilter.GaussianBlur(60)))
    im.paste(c,(cx,cy)); d=ImageDraw.Draw(im)
    y=ctext(d,230+cov.height+70,"Principles of\nDark Psychology",ImageFont.truetype(FONTS["serif_italic"],78),COL["white"])+20
    d.line([(W/2-60,y),(W/2+60,y)],fill=(150,0,0),width=2); y+=40
    ctext(d,y,"LINK IN BIO",ImageFont.truetype(FONTS["sans_bold"],52),COL["red"])
    ctext(d,y+80,"free version + full book",ImageFont.truetype(FONTS["sans"],38),COL["gray"])
    return im
def main(spec,out):
    cfg=json.load(open(spec)); tmp=tempfile.mkdtemp(); n=0; black=Image.new("RGB",(W,H)); F=8
    def save(im):
        nonlocal n; im.save(f"{tmp}/{n:05d}.jpg",quality=92); n+=1
    for s in cfg["scenes"]:
        im=scene(s); fr=int(s.get("dur",3)*FPS)
        for i in range(fr):
            a=max(0,min(1,i/F,(fr-1-i)/F)); dy=int(18*(1-min(1,i/(F*2))))
            f=im
            if dy: f=Image.new("RGB",(W,H),(4,4,4)); f.paste(im,(0,dy))
            save(Image.blend(black,f,a))
    if cfg.get("cover",True):
        cov=Image.open(os.path.join(HERE,"..","assets","cover.png")).convert("RGB")
        cw=760; ch=int(cov.height*cw/cov.width)
        if ch>1100: ch=1100; cw=int(cov.width*ch/cov.height)
        cov=cov.resize((cw,ch)); fr=int(4.5*FPS)
        for i in range(fr): save(Image.blend(black,cover_frame(cov,i/fr),min(1,i/F)))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{tmp}/%05d.jpg","-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-movflags","+faststart",out],check=True)
if __name__=="__main__": main(sys.argv[1],sys.argv[2])

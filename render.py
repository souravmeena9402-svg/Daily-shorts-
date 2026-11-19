import json, math as m, os, subprocess as sp, wave, sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from stories import story,TOPICS
W,H,FPS=720,1280,24
cfg=json.loads(Path('studio.json').read_text()); topics=cfg['topics']; assert topics and all(k in TOPICS for k in topics)
n=int(sys.argv[1]) if len(sys.argv)>1 else 0
k=topics[n%len(topics)]; v=n//len(topics); title,beats=story(k,v)
out=Path('output');out.mkdir(exist_ok=True)
def run(*args): sp.run(args,check=True)
def font(sz,b=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if b else '')+'.ttf',sz)
small,lab,cap,head=font(21,True),font(24),font(34),font(48,True)
navy='#101c32'; ink='#f5f2e9'; mint='#73edcc'; gold='#ffc775'; muted='#a7bed1'
def wrap(d,text,f,w):
    lines=['']
    for word in text.split():
        s=(lines[-1]+' '+word).strip()
        if d.textlength(s,font=f)>w and lines[-1]:lines.append(word)
        else:lines[-1]=s
    return lines
base=Image.new('RGB',(W,H),navy);d=ImageDraw.Draw(base)
d.text((48,50),cfg['series'].upper(),font=small,fill=mint);d.text((48,102),'FIELD NOTE  /  '+str(n+1).zfill(3),font=lab,fill=muted)
for i,l in enumerate(wrap(d,title,head,615)):d.text((48,153+i*58),l,font=head,fill=ink)
d.rounded_rectangle((34,362,674,800),radius=32,fill='#182a43');
for x in range(60,660,24):
    for y in range(390,778,24):d.point((x,y),fill='#47607a')
def scene(d,b,t):
    def line(points,color=muted,w=3):d.line(points,fill=color,width=w)
    def dot(x,y,r=10,c=mint):d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    def ring(x,y,r):d.ellipse((x-r,y-r,x+r,y+r),outline=muted,width=2)
    p=(t%4)/4
    if k=='echo':
        line((585,460,585,710),gold,8);dot(110,590,16);line((110,590,585,590));x=110+475*(1-abs(2*p-1));dot(x,590,12,gold);ring(x,590,23);ring(x,590,35)
    if k=='pendulum':
        ratio=2+v%6
        for x,l,period,c in [(205,245/ratio**2,1,mint),(480,245,ratio,gold)]:
            a=.28*m.cos(2*m.pi*t/period);u=x+l*m.sin(a);y=455+l*m.cos(a);line((x,455,u,y),c,4);dot(x,455,5);dot(u,y,12,c)
    if k=='wave':
        cycles=(2+v)*(2 if b==3 else 1); phase=2*m.pi*t*.55*(2 if b==3 else 1);pts=[(x,590-68*m.sin((x-80)/550*2*m.pi*cycles-phase)) for x in range(80,631,2)];line((80,590,630,590));line(pts,mint,5);dot(*pts[len(pts)//2],10,gold)
    if k=='fall':
        count=2+v;line((215,433,215,737));
        for j in range(min(count,100)+1):dot(215,433+304*(j/count)**2,6,gold)
        dot(215,433+304*p*p,13);line((178,738,536,738));line((245,509,529,509));d.text((315,468),'¼ of the drop',font=lab,fill=gold)
    if k=='orbit':
        r=2+v;dot(355,582,18,gold)
        for rad,period,c in [(157/r,2,mint),(157,2*r**1.5,gold)]:
            ring(355,582,rad);a=t*m.tau/period;dot(355+rad*m.cos(a),582+rad*m.sin(a),10,c)
    if k=='shadow':
        a=[30,45,60][v%3];angle=a-(10*p if b==3 else 0);s=145/m.tan(m.radians(angle));x=162;line((72,680,632,680));line((x,535,x,680),mint,9);line((x,680,x+s,680),gold,8);line((x-50,535-50*m.tan(m.radians(angle)),x+s,680),gold,3);dot(x-50,535-50*m.tan(m.radians(angle)),12,gold)
    if k=='circle':
        fac=2+v%4;r=140/fac;R=r*(1+(fac-1)*min(1,p*1.6));ring(355,590,140);d.ellipse((355-R,590-R,355+R,590+R),fill='#245957',outline=mint,width=4);ring(355,590,r);line((355,590,355+R,590),gold,4);dot(355,590,5,gold)
parts=[]; audio=bytearray(); rate=None
for j,(text,label) in enumerate(beats):
    src=out/'line.txt';src.write_text(text.replace('’',"'")); wav=out/'line.wav';run('flite','-voice','slt','-f',str(src),'-o',str(wav))
    with wave.open(str(wav)) as w:
        assert (w.getnchannels(),w.getsampwidth())==(1,2);rate=w.getframerate();raw=w.readframes(w.getnframes())
    frames=m.ceil((len(raw)/2/rate+.25)*FPS);target=round((sum(parts)+frames)*rate/FPS);audio.extend(raw);audio.extend(bytes(2*target-len(audio)));parts.append(frames)
with wave.open(str(out/'voice.wav'),'wb') as w:w.setparams((1,2,rate,0,'NONE',''));w.writeframes(audio)
p=sp.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(out/'voice.wav'),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(out/'short.mp4')],stdin=sp.PIPE)
for j,((text,label),frames) in enumerate(zip(beats,parts)):
    bg=base.copy();d=ImageDraw.Draw(bg);d.text((66,392),'MODEL IN MOTION',font=small,fill=muted);d.text((66,746),label,font=lab,fill=ink);d.text((48,845),['THE QUESTION','WATCH CLOSELY','THE MECHANISM','THE TAKEAWAY'][j],font=small,fill=gold)
    for i,l in enumerate(wrap(d,text,cap,592)):d.text((48,898+i*43),l,font=cap,fill=ink)
    for i in range(4): d.rounded_rectangle((48+152*i,1192,184+152*i,1198),3,fill=mint if i<=j else '#314560')
    for f in range(frames):
        im=bg.copy();scene(ImageDraw.Draw(im),j,(sum(parts[:j])+f)/FPS);p.stdin.write(im.tobytes())
p.stdin.close();assert p.wait()==0
meta={'title':f'{title} | Lab {n+1:03}', 'description':' '.join(x[0] for x in beats)+'\n\nOriginal schematic animation. Synthetic English narration. Diagrams illustrate idealized models. #Shorts','episode':n}
(out/'meta.json').write_text(json.dumps(meta));print(meta['title'],round(sum(parts)/FPS,1),'s')

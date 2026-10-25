"""16x16 item icons for the arcane weapons, drawn so each one shows the weapon as it looks in game
(same shapes and palette as the held / entity textures). All art is original."""
import math
from PIL import Image
import gen_weapons as G
O=G.OUT; C=G.CRY; W=G.GLOW; GO=G.GOLD; WD=G.WOOD; GM=G.GEM
class P:
    def __init__(s): s.p={}
    def s(s,x,y,c):
        if 0<=x<16 and 0<=y<16: s.p[(x,y)]=c
    def shift(s,dx,dy):
        s.p={(x+dx,y+dy):c for (x,y),c in s.p.items()}
    def outline(s):
        add={}
        for (x,y) in s.p:
            for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                q=(x+dx,y+dy)
                if q not in s.p and 0<=q[0]<16 and 0<=q[1]<16: add[q]=O
        s.p.update(add)
    def img(s):
        im=Image.new('RGBA',(16,16),(0,0,0,0))
        for (x,y),c in s.p.items(): im.putpixel((x,y),(*c,255))
        return im

def sword():
    p=P()
    L={0:14,1:13,2:12,3:11,4:10,5:9,6:8,7:7,8:6}
    R={0:14,1:14,2:14,3:14,4:13,5:12,6:11,7:10,8:9}
    L[9]=5;R[9]=8
    for y in range(10):
        w=R[y]-L[y]+1
        for i,x in enumerate(range(L[y],R[y]+1)):
            if w==4: col=[C[0],C[1],C[2],C[3]][i]
            elif w==3: col=[C[0],C[1],C[3]][i]
            elif w==2: col=[C[0],C[2]][i]
            else: col=C[0]
            if w==4 and i==1 and y in(3,4,6): col=W
            p.s(x,y,col)
    p.s(14,0,W)
    # guard: two diagonal lines x-y = -5,-4 for y 7..13
    for y in range(7,13):
        p.s(y-5,y,GO[0] if y<10 else GO[1]); p.s(y-4,y,GO[1] if y<10 else GO[2])
    p.s(5,10,GM[1]); p.s(6,10,GM[0])
    # grip + pommel
    p.s(4,11,WD[0]);p.s(5,11,WD[1]);p.s(3,12,WD[1]);p.s(4,12,WD[2]);p.s(2,13,WD[1])
    p.s(1,14,GO[1]);p.s(2,14,GO[2]);p.s(1,15,GO[2]);p.s(0,14,GO[2])
    p.outline(); return p.img()


import math
def axe():
    p=P()
    for k in range(0,10):
        x,y=2+k,13-k
        c=WD[k%2] if k not in(3,6) else GO[1]
        p.s(x,y,c); p.s(x+1,y,WD[1] if c!=GO[1] else GO[2])
    p.s(1,14,GO[1]);p.s(2,14,GO[2]);p.s(0,15,GM[1]);p.s(1,15,GM[2])
    cx,cy=6.6,5.2
    for y in range(0,12):
        for x in range(1,14):
            ro=math.hypot(x-cx,y-cy); ri=math.hypot(x-(cx+3.4),y-(cy+2.8))
            if ro<=5.6 and ri>4.6 and (x+y)<=17:
                d=ro/5.6
                col=C[0] if d>0.82 else C[1] if d>0.6 else C[2] if d>0.38 else C[3]
                if ri<5.5: col=GO[1] if (x+y)%2==0 else C[3]
                p.s(x,y,col)
    for (x,y) in ((4,2),(3,3),(3,5),(4,4)): p.s(x,y,W)
    # socket where the head meets the shaft
    for (x,y,c) in ((9,6,GO[0]),(10,6,GO[1]),(9,7,GO[1]),(10,7,GO[2]),(8,8,GO[2]),(9,8,GO[3])): p.s(x,y,c)
    # small back spike
    for (x,y,c) in ((11,5,C[3]),(12,5,C[4]),(12,4,C[4]),(11,6,C[4])): p.s(x,y,c)
    p.outline(); return p.img()

def spear():
    p=P()
    for k in range(0,11):
        x,y=2+k,13-k
        if y<=7: continue
        c=WD[k%2] if k not in(3,6) else GO[1]
        p.s(x,y,c); p.s(x+1,y,WD[1] if c!=GO[1] else GO[2])
    p.s(1,14,GM[1]);p.s(2,14,GM[2]);p.s(1,13,GM[0]);p.s(0,15,GM[2])
    p.s(8,7,GO[0]);p.s(9,7,GO[1]);p.s(10,7,GO[2]);p.s(7,8,GO[2])
    rows={0:(15,15),1:(14,15),2:(12,15),3:(10,14),4:(9,13),5:(9,11),6:(8,10)}
    for y,(l,r) in rows.items():
        n=r-l+1
        for i,x in enumerate(range(l,r+1)):
            col=C[0] if i==0 else C[3] if i==n-1 and n>2 else C[1] if i<=n//2 else C[2]
            if n>=3 and i==1 and y in(2,3,4): col=W
            if n==2: col=[C[0],C[2]][i]
            p.s(x,y,col)
    p.outline(); return p.img()

def bow():
    p=P()
    P0,Cc,P2=(12.5,2.5),(1.4,1.4),(2.5,12.5)
    seen=[]
    N=40
    for i in range(N+1):
        t=i/N
        x=(1-t)**2*P0[0]+2*(1-t)*t*Cc[0]+t*t*P2[0]
        y=(1-t)**2*P0[1]+2*(1-t)*t*Cc[1]+t*t*P2[1]
        seen.append((round(x),round(y),t))
    for x,y,t in seen:
        m=1-abs(2*t-1)           # 0 at tips, 1 at the middle
        col=C[0] if t<0.35 or t>0.65 else C[1]
        col=C[1] if 0.35<=t<=0.65 else C[0]
        p.s(x,y,C[1]); 
    for x,y,t in seen:
        p.s(x+1,y,C[3]); p.s(x,y+1,C[3])
    for x,y,t in seen: p.s(x,y,C[0] if t<0.5 else C[1])
    for x,y,t in seen:
        if min(abs(t-0.2),abs(t-0.8))<0.025: p.s(x,y,GO[1]); p.s(x+1,y,GO[2]); p.s(x,y+1,GO[2])
    # string
    for k in range(4,13): p.s(16-k,k,W if k%2 else C[1])
    # riser block with gem
    for (x,y,c) in ((2,3,GO[1]),(3,2,GO[1]),(3,3,GO[0]),(4,3,GO[1]),(3,4,GO[1]),(4,4,GM[0]),(5,4,GO[2]),(4,5,GO[2]),(5,5,GO[3]),(2,4,GO[2]),(4,2,GO[2]),(2,2,GO[0])): p.s(x,y,c)
    for (ox,oy) in ((12,3),(3,12)):
        for dx in(-1,0,1):
            for dy in(-1,0,1):
                p.s(ox+dx,oy+dy,GO[0] if dx+dy<0 else GO[1] if dx+dy==0 else GO[2])
        p.s(ox,oy,O)
    p.outline(); return p.img()

def wand():
    p=P()
    cx,cy=3.2,8.0
    for y in range(3,14):
        for x in range(0,7):
            d=math.hypot(x-cx,y-cy)
            if d<=3.9:
                if d>3.0: col=GO[0] if (x+y)<11 else GO[1] if (x+y)<13 else GO[2]
                else:
                    t=(y-(cy-3.0))/6.0
                    col=C[1] if t<0.3 else C[2] if t<0.65 else C[3]
                    if d<1.3: col=W if d<0.7 else GM[1]
                p.s(x,y,col)
    for y in range(5,12):
        for x in range(6,9):
            col=WD[0] if y==5 else WD[2] if y==11 else WD[1]
            p.s(x,y,col)
    p.s(7,7,GM[0]);p.s(7,8,GM[1]);p.s(7,9,GM[2])
    for x in (9,10,11):
        for y in (7,8,9): p.s(x,y,WD[0] if y==7 else WD[1] if y==8 else WD[2])
    p.s(10,8,GM[1]) 
    for y in range(6,11): p.s(9,y,GO[0] if y==6 else GO[1] if y<10 else GO[2])
    for y in range(6,11): p.s(12,y,GO[0] if y==6 else GO[1] if y<10 else GO[2])
    # crystal head, straight
    for x,rows in ((13,(7,8,9)),(14,(7,8,9)),(15,(8,))):
        for y in rows:
            p.s(x,y,C[0] if y==7 else C[1] if y==8 else C[3])
    p.s(14,8,W)
    p.outline(); return p.img()


import json, math
b=json.load(open('/home/claude/mark/build.json'))
C=b['C']; RC0=b['Rc']; D=b['d']
A0=[b['A'][0]-C[0], b['A'][1]-C[1]]; P10=[b['P1'][0]-C[0], b['P1'][1]-C[1]]
ANG=[90,30,-30,-90,-150,150]                 # lobe directions (screen y is down)
def mark(w, round_r=0, plump=1.0):
    """w: stroke width. round_r: radius of the rounded outer notch (0 = sharp). plump: lobe size multiplier."""
    Rc=RC0*plump
    cen=[(D*math.cos(math.radians(a)), -D*math.sin(math.radians(a))) for a in ANG]
    def notch_pt(c1,c2):
        (x1,y1),(x2,y2)=c1,c2; mx,my=(x1+x2)/2,(y1+y2)/2; dd=math.hypot(x2-x1,y2-y1); h=math.sqrt(Rc*Rc-(dd/2)**2)
        ux,uy=(y1-y2)/dd,(x2-x1)/dd; p=(mx+h*ux,my+h*uy); q=(mx-h*ux,my-h*uy)
        return max((p,q),key=lambda t:math.hypot(*t))
    f=lambda p: f'{p[0]:.1f} {p[1]:.1f}'
    if round_r<=0:
        N=[notch_pt(cen[i],cen[(i+1)%6]) for i in range(6)]
        ring='M'+f(N[5])+''.join(f'A{Rc:.1f} {Rc:.1f} 0 0 1 {f(N[i])}' for i in range(6))+'Z'
        SA,SB=N[5],N[2]
    else:
        rf=round_r+w/2                           # fillet on the centerline; the outer edge keeps radius round_r
        segs=[]; mids=[]
        for i in range(6):
            c1,c2=cen[i],cen[(i+1)%6]
            (x1,y1),(x2,y2)=c1,c2; mx,my=(x1+x2)/2,(y1+y2)/2; dd=math.hypot(x2-x1,y2-y1); R=Rc+rf
            h=math.sqrt(R*R-(dd/2)**2); ux,uy=(y1-y2)/dd,(x2-x1)/dd
            F=max(((mx+h*ux,my+h*uy),(mx-h*ux,my-h*uy)),key=lambda t:math.hypot(*t))   # fillet center, outward
            t1=(c1[0]+(F[0]-c1[0])*Rc/R, c1[1]+(F[1]-c1[1])*Rc/R); t2=(c2[0]+(F[0]-c2[0])*Rc/R, c2[1]+(F[1]-c2[1])*Rc/R)
            k=math.hypot(*F); mid=(F[0]-F[0]/k*rf, F[1]-F[1]/k*rf)
            segs.append((t1,t2)); mids.append(mid)
        ring='M'+f(segs[5][1])
        for i in range(6):
            t1,t2=segs[i]
            ring+=f'A{Rc:.1f} {Rc:.1f} 0 0 1 {f(t1)}A{rf:.1f} {rf:.1f} 0 0 0 {f(t2)}'
        ring+='Z'; SA,SB=mids[5],mids[2]
    P1=(SA[0]+(P10[0]-A0[0]), SA[1]+(P10[1]-A0[1])); P2=(-P1[0],-P1[1])
    s=f'M{f(SA)}C{f(P1)} {f(P2)} {f(SB)}'
    hw=D*math.cos(math.radians(30))+Rc+w/2+4; hh=D+Rc+w/2+4
    vb=f'{-hw:.0f} {-hh:.0f} {2*hw:.0f} {2*hh:.0f}'
    return vb, ring, s
def svg(vb, ring, s, w, col):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="SellClouds"><title>SellClouds</title>'
            f'<g fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"><path d="{ring}"/><path d="{s}"/></g></svg>')
OPTS=[('1','Current',70,0,1.0),('2','Fatter',84,0,1.0),('3','Fatter, soft joins',84,10,1.0),
      ('4','Fatter, round joins',84,22,1.0),('5','Plump lobes, round joins',84,22,1.06),('6','Heaviest, round, plump',96,22,1.06)]
out={}
for k,name,w,rr,pl in OPTS:
    vb,ring,s=mark(w,rr,pl)
    open(f'opt{k}.svg','w').write(svg(vb,ring,s,w,'#131619')); open(f'opt{k}-dark.svg','w').write(svg(vb,ring,s,w,'#E8EDF2'))
    out[k]=(name,w,rr,pl)
json.dump(out,open('opts.json','w'))
cells=''.join(f'''<div class="c"><div class="n">{k}. {n}</div><img src="opt{k}.svg" style="height:150px">
<div class="row"><img src="opt{k}.svg" style="height:48px"><img src="opt{k}.svg" style="height:34px"><img src="opt{k}.svg" style="height:16px">
<span class="dk"><img src="opt{k}-dark.svg" style="height:34px"><img src="opt{k}-dark.svg" style="height:16px"></span></div>
<div class="m">stroke {w}{", rounded joins" if rr else ", sharp joins"}{", lobes +6%" if pl>1 else ""}</div></div>''' for k,(n,w,rr,pl) in out.items())
open('board.html','w').write(f'''<html><head><style>body{{margin:0;background:#F9FCFF;font:14px Inter,system-ui,sans-serif;color:#131619}}
.g{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;padding:18px}}.c{{background:#fff;border:1px solid #e3e8ee;border-radius:14px;padding:16px;text-align:center}}
.n{{font-weight:700;margin-bottom:10px}}.row{{display:flex;align-items:center;justify-content:center;gap:14px;margin-top:14px}}
.dk{{display:inline-flex;gap:10px;align-items:center;background:#101418;padding:8px 10px;border-radius:8px}}.m{{color:#556270;font-size:12px;margin-top:10px}}</style></head>
<body><div class="g">{cells}</div></body></html>''')
print('ok')

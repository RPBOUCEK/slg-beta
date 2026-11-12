import json,math
G="/tmp/claude-0/-home-claude-slg-beta/991b3283-be07-532b-b3c5-8230aedd119b/scratchpad/geo2/ne/geojson/"
C=json.load(open(G+"ne_50m_admin_0_countries.geojson")); L=json.load(open(G+"ne_50m_lakes.geojson"))
LANES={'ukraine':['UKR'],'east':['KEN','TZA','SDS','BDI','UGA','RWA','ZMB','MWI','COD'],'west':['LBR','GHA','TGO','BEN','NGA','BFA','MLI'],
 'cac':['GTM','HND','SLV','NIC','PAN','HTI','DOM','JAM'],'south':['ZAF','MOZ','ZWE','NAM','SWZ','MDG','BWA']}
PORTS={'east':[('Dar es Salaam',39.3,-6.82),('Mombasa',39.67,-4.05)],'south':[('Durban',31.03,-29.87),('Beira',34.84,-19.84)],
 'west':[('Lomé',1.28,6.13),('Tema',0.0,5.63),('Monrovia',-10.8,6.32)],'cac':[('Kingston',-76.8,17.97),('Puerto Cortés',-87.95,15.85)],'ukraine':[]}
CITIES={'south':[('Gaborone',25.91,-24.65)]}
NAMES={'UKR':'Ukraine','KEN':'Kenya','TZA':'Tanzania','SDS':'South Sudan','BDI':'Burundi','UGA':'Uganda','RWA':'Rwanda','ZMB':'Zambia','MWI':'Malawi','COD':'DR Congo','LBR':'Liberia','GHA':'Ghana','TGO':'Togo','BEN':'Benin','NGA':'Nigeria','BFA':'Burkina Faso','MLI':'Mali','GTM':'Guatemala','HND':'Honduras','SLV':'El Salvador','NIC':'Nicaragua','PAN':'Panama','HTI':'Haiti','DOM':'Dominican Republic','JAM':'Jamaica','ZAF':'South Africa','MOZ':'Mozambique','ZWE':'Zimbabwe','NAM':'Namibia','SWZ':'Eswatini','MDG':'Madagascar','BWA':'Botswana'}
W,H=240,190; PAD=10
def code(f): p=f['properties']; return p.get('ADM0_A3') or p.get('ISO_A3')
def rings(g):
    if g['type']=='Polygon': return [g['coordinates']]
    if g['type']=='MultiPolygon': return g['coordinates']
    return []
def merc(lon,lat):
    lat=max(-85,min(85,lat)); return (math.radians(lon), math.log(math.tan(math.pi/4+math.radians(lat)/2)))
def dp(pts,eps):
    if len(pts)<4: return pts
    a,b=pts[0],pts[-1]; dmax=0; idx=0
    ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay; n=math.hypot(dx,dy) or 1e-9
    for i in range(1,len(pts)-1):
        px,py=pts[i]; d=abs(dy*px-dx*py+bx*ay-by*ax)/n
        if d>dmax: dmax,idx=d,i
    if dmax>eps: return dp(pts[:idx+1],eps)[:-1]+dp(pts[idx:],eps)
    return [a,b]
def clip(poly,x0,y0,x1,y1):
    def cl(pts,inside,inter):
        out=[]
        for i in range(len(pts)):
            c=pts[i]; p=pts[i-1]
            if inside(c):
                if not inside(p): out.append(inter(p,c))
                out.append(c)
            elif inside(p): out.append(inter(p,c))
        return out
    def ix(p,c,x): t=(x-p[0])/(c[0]-p[0]); return (x,p[1]+t*(c[1]-p[1]))
    def iy(p,c,y): t=(y-p[1])/(c[1]-p[1]); return (p[0]+t*(c[0]-p[0]),y)
    for ins,itr in [(lambda q:q[0]>=x0,lambda p,c:ix(p,c,x0)),(lambda q:q[0]<=x1,lambda p,c:ix(p,c,x1)),(lambda q:q[1]>=y0,lambda p,c:iy(p,c,y0)),(lambda q:q[1]<=y1,lambda p,c:iy(p,c,y1))]:
        if not poly: break
        poly=cl(poly,ins,itr)
    return poly
def path(polys,eps):
    d=''
    for ring in polys:
        if len(ring)>3:
            a=ring[0]; k=max(range(len(ring)),key=lambda i:(ring[i][0]-a[0])**2+(ring[i][1]-a[1])**2)
            r=dp(ring[:k+1],eps)[:-1]+dp(ring[k:]+[ring[0]],eps)
        else: r=ring
        if len(r)<3: continue
        d+='M'+'L'.join('%.1f %.1f'%q for q in r)+'Z'
    return d
OUT={}
for lid,codes in LANES.items():
    feats=[f for f in C['features'] if code(f) in codes]
    assert len(feats)==len(codes),(lid,[code(f) for f in feats])
    def area(r):
        a=0
        for i in range(len(r)): a+=r[i-1][0]*r[i][1]-r[i][0]*r[i-1][1]
        return abs(a)/2
    xs=[];ys=[]
    for f in feats:
        polys=rings(f['geometry']); big=max(area(p[0]) for p in polys)
        for poly in polys:
            if area(poly[0])<big*0.02: continue
            for lon,lat in poly[0]:
                x,y=merc(lon,lat); xs.append(x); ys.append(y)
    mnx,mxx,mny,mxy=min(xs),max(xs),min(ys),max(ys)
    s=min((W-2*PAD)/(mxx-mnx),(H-2*PAD)/(mxy-mny))
    ox=(W-(mxx-mnx)*s)/2; oy=(H-(mxy-mny)*s)/2
    P=lambda lon,lat:((merc(lon,lat)[0]-mnx)*s+ox, H-((merc(lon,lat)[1]-mny)*s+oy))
    # view bounds in lon/lat for neighbor selection
    def proj_poly(poly): return [P(lon,lat) for lon,lat in poly]
    lane=[];ctx=[];lakes=[];per={}
    for f in C['features']:
        polys=[]
        for poly in rings(f['geometry']):
            pp=clip(proj_poly(poly[0]),-2,-2,W+2,H+2)
            if len(pp)>2: polys.append(pp)
        if not polys: continue
        if code(f) in codes:
            lane.extend(polys)
            bigp=max(area(q) for q in polys); keep=[q for q in polys if area(q)>=bigp*0.02]
            bx=[q[0] for r in keep for q in r]; by=[q[1] for r in keep for q in r]
            per[NAMES[code(f)]]={'d':path(polys,.35),'bb':[round(min(bx),1),round(min(by),1),round(max(bx)-min(bx),1),round(max(by)-min(by),1)]}
        else: ctx.extend(polys)
    for f in L['features']:
        if f['properties'].get('scalerank',9)>5: continue
        for poly in rings(f['geometry']):
            pp=clip(proj_poly(poly[0]),-2,-2,W+2,H+2)
            if len(pp)>2: lakes.append(pp)
    OUT[lid]={'k':per,'cities':[{'p':n,'x':round(P(lo,la)[0],1),'y':round(P(lo,la)[1],1)} for n,lo,la in CITIES.get(lid,[])],'d':path(lane,.45),'c':path(ctx,1.0),'w':path(lakes,.6),'pts':[{'p':n,'x':round(P(lo,la)[0],1),'y':round(P(lo,la)[1],1)} for n,lo,la in PORTS[lid]]}
    print(lid,len(OUT[lid]['d']),len(OUT[lid]['c']),len(OUT[lid]['w']))
json.dump(OUT,open("/tmp/claude-0/-home-claude-slg-beta/991b3283-be07-532b-b3c5-8230aedd119b/scratchpad/geo2/lanemaps.json","w"),separators=(",",":"))

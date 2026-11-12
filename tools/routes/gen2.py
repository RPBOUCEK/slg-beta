import math,re,json,collections
S="/tmp/claude-0/-home-claude-slg-beta/991b3283-be07-532b-b3c5-8230aedd119b/scratchpad"
def P(lon,lat):
    l=math.radians(lon); p=math.radians(lat); p2=p*p; p4=p2*p2
    x=l*(0.8707-0.131979*p2+p4*(-0.013791+p4*(0.003971*p2-0.001529*p4)))
    y=p*(1.007226+p2*(0.015085+p4*(-0.044475+0.028874*p2-0.005916*p4)))
    return (500+160*x, 260-160*y)
N={'NYC':(-74.05,40.6),'NFK':(-76.3,36.95),'HOU':(-95.0,29.7),'LAX':(-118.25,33.75),'TAC':(-122.42,47.27),
 'ALG':(-5.45,36.1),'PSD':(32.3,31.4),'JED':(39.1,21.45),'NSA':(72.8,18.9),'CMB':(79.8,6.9),'KFK':(56.4,25.35),
 'NKC':(-16.6,18.1),'DKR':(-17.5,14.65),'BJL':(-16.9,13.45),'CKY':(-13.7,9.5),'FNA':(-13.2,8.45),'MLW':(-10.8,6.3),'ABJ':(-4.0,5.25),'TEM':(0.0,5.6),'LFW':(1.25,6.1),'COO':(2.4,6.3),'LOS':(3.4,6.4),'MAL':(8.75,3.75),'KRI':(9.85,2.9),'PNR':(11.8,-4.8),'LAD':(13.2,-8.8),
 'MBA':(39.7,-4.05),'DSM':(39.3,-6.8),'MGQ':(45.35,2.05),'NAC':(40.7,-14.5),'BEW':(34.85,-19.85),'DUR':(31.05,-29.87),'TMM':(49.45,-18.15),'CGP':(91.8,22.25),
 'PIR':(23.6,37.9),'IST':(28.95,41.0),'CND':(28.7,44.15),'ODS':(30.75,46.45),'BEY':(35.5,33.9),'AQB':(35.0,29.5),
 'SOU':(-1.4,50.85),'GDN':(18.65,54.4),'HEL':(24.95,60.15),
 'KHH':(120.25,22.6),'MNL':(120.95,14.55),'CMP':(107.0,10.4),'KOS':(103.5,10.6),'TSN':(117.75,38.95),'UB':(106.9,47.9),
 'KIN':(-76.8,17.95),'LAF':(-72.45,18.8),'CAU':(-69.63,18.4),'MAR':(-82.75,23.0),'PCR':(-87.95,15.85),'STC':(-88.6,15.73),'CTG':(-75.55,10.4),'COL':(-79.9,9.4),'LGU':(-66.93,10.62),'GND':(-61.75,12.05),'POS':(-61.52,10.65),'GEO':(-58.17,6.85),
 'GYE':(-80.0,-2.3),'CLL':(-77.15,-12.05),'SSZ':(-46.3,-24.0),'MVD':(-56.2,-34.9),'PQZ':(-90.8,13.92),'COR':(-87.2,12.45),
 'Lw':(-182,26),'Le':(182,24),'Pw':(-182,30),'Pe':(182,32)}
HUB={'ALG':'Algeciras / Tanger Med','JED':'Jeddah','NSA':'Nhava Sheva','CMB':'Colombo','PIR':'Piraeus','SOU':'Southampton','KHH':'Kaohsiung','KIN':'Kingston','CTG':'Cartagena','COL':'Panama Canal','SSZ':'Santos','TSN':'Tianjin','KFK':'Khor Fakkan'}
GWN={'NYC':'New York / NJ','NFK':'Norfolk','HOU':'Houston','LAX':'Los Angeles'}
# geometry: via point (lon,lat) the curve passes through at its middle; otherwise a gentle symmetric bow
VIA={'NFK>ALG':(-40,41.5),'NYC>ALG':(-40,43),'ALG>PSD':(13,37.6),'PSD>JED':(34.8,27.5),'JED>NSA':(52,10.5),'ALG>PIR':(10,38.6),
 'ALG>NKC':(-14,26),'NKC>DKR':None,'DKR>FNA':(-17,10.5),'FNA>ABJ':(-8.5,4.4),'ABJ>LOS':(0,4.9),'LOS>KRI':(6.5,3.5),'KRI>LAD':(9.5,-3.5),
 'NSA>MBA':(55,4),'MBA>DSM':None,'NSA>MGQ':(58,8),'NSA>CMB':(76,11.5),'CMB>NAC':(58,-8),'NAC>BEW':(40,-18),'BEW>DUR':(35.5,-26),'CMB>TMM':(62,-8),'CMB>CGP':(88.5,13.5),'NSA>KFK':(63,22.8),
 'JED>AQB':(35.6,26.0),'PIR>BEY':(29.5,35.4),'PIR>IST':(25.8,39.6),'IST>CND':(30.2,42.8),'IST>ODS':(31.2,43.5),
 'NYC>SOU':(-40,48.5),'SOU>GDN':(9.5,56.8),'GDN>HEL':(21.5,58.4),
 'LAX>Lw':(-150,32),'Le>KHH':(150,26),'KHH>MNL':(122.4,18.6),'KHH>CMP':(113.5,15),'CMP>KOS':(105,8.6),
 'NFK>COL':(-75,22),'COL>Pw':(-130,21),'Pe>TSN':(140,33),'COL>GYE':(-82.2,3.5),'GYE>CLL':(-80.8,-7.6),
 'HOU>KIN':(-85,21.5),'HOU>PCR':(-89.5,22),'HOU>STC':(-90.3,22),'HOU>MAR':(-88.5,25.5),'NYC>KIN':(-72.5,27),'NFK>CTG':(-72,22),'CTG>COL':(-78,11.4),
 'KIN>LAF':(-74.5,17.6),'KIN>CAU':(-73,16.7),'KIN>LGU':(-71,14),'KIN>GND':(-69,14.6),'GND>POS':None,'POS>GEO':(-59.2,9.3),
 'NYC>SSZ':(-30,6),'SSZ>MVD':(-51.5,-31.5),'LAX>PQZ':(-104,19),'PQZ>COR':(-89,12.4),'KIN>COL':(-78.5,13.5)}
R={'Mauritania':[['NFK','ALG','NKC']],'Gambia':[['NFK','ALG','NKC','DKR']],'Mali':[['NFK','ALG','NKC','DKR']],
 'Guinea':[['NFK','ALG','NKC','DKR','FNA']],'Sierra Leone':[['NFK','ALG','NKC','DKR','FNA']],'Liberia':[['NFK','ALG','NKC','DKR','FNA','ABJ']],
 'Ivory Coast':[['NFK','ALG','NKC','DKR','FNA','ABJ']],'Burkina Faso':[['NFK','ALG','NKC','DKR','FNA','ABJ']],
 'Ghana':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS']],'Togo':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS']],'Benin':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS']],'Nigeria':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS']],
 'Equatorial Guinea':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS','KRI']],'Chad':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS','KRI']],'Central African Republic':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS','KRI']],
 'Angola':[['NFK','ALG','NKC','DKR','FNA','ABJ','LOS','KRI','LAD']],
 'Kenya':[['NFK','ALG','PSD','JED','NSA','MBA']],'Uganda':[['NFK','ALG','PSD','JED','NSA','MBA']],'South Sudan':[['NFK','ALG','PSD','JED','NSA','MBA']],
 'Tanzania':[['NFK','ALG','PSD','JED','NSA','MBA','DSM']],'Burundi':[['NFK','ALG','PSD','JED','NSA','MBA','DSM']],'Zambia':[['NFK','ALG','PSD','JED','NSA','MBA','DSM']],
 'Somalia':[['NFK','ALG','PSD','JED','NSA','MGQ']],'UAE':[['NFK','ALG','PSD','JED','NSA','KFK']],
 'Malawi':[['NFK','ALG','PSD','JED','NSA','CMB','NAC']],'Mozambique':[['NFK','ALG','PSD','JED','NSA','CMB','NAC','BEW']],
 'South Africa':[['NFK','ALG','PSD','JED','NSA','CMB','NAC','BEW','DUR']],'Eswatini':[['NFK','ALG','PSD','JED','NSA','CMB','NAC','BEW','DUR']],'Lesotho':[['NFK','ALG','PSD','JED','NSA','CMB','NAC','BEW','DUR']],
 'Madagascar':[['NFK','ALG','PSD','JED','NSA','CMB','TMM']],'Bangladesh':[['NFK','ALG','PSD','JED','NSA','CMB','CGP']],
 'Jordan':[['NYC','ALG','PSD','JED','AQB']],'Greece':[['NYC','ALG','PIR']],'Lebanon':[['NYC','ALG','PIR','BEY']],
 'Romania':[['NYC','ALG','PIR','IST','CND']],'Ukraine':[['NYC','ALG','PIR','IST','CND']],'Moldova':[['NYC','ALG','PIR','IST','CND']],
 'Poland':[['NYC','SOU','GDN']],'Finland':[['NYC','SOU','GDN','HEL']],
 'Philippines':[['LAX','Lw'],['Le','KHH','MNL']],'Vietnam':[['LAX','Lw'],['Le','KHH','CMP']],'Cambodia':[['LAX','Lw'],['Le','KHH','CMP','KOS']],
 'Mongolia':[['NFK','CTG','COL','Pw'],['Pe','TSN']],
 'Guatemala':[['HOU','STC'],['LAX','PQZ']],'Honduras':[['HOU','STC','PCR']],'El Salvador':[['HOU','STC','PCR'],['LAX','PQZ']],'Nicaragua':[['LAX','PQZ','COR']],
 'Cuba':[['HOU','MAR']],'Jamaica':[['HOU','KIN']],'Dominican Republic':[['HOU','KIN','LAF','CAU']],'Haiti':[['NYC','KIN','LAF']],'Panama':[['NFK','CTG','COL']],
 'Colombia':[['NFK','CTG']],'Venezuela':[['NYC','KIN','LGU']],'Grenada':[['NYC','KIN','LGU','GND']],'Trinidad & Tobago':[['NYC','KIN','LGU','GND','POS']],'Guyana':[['NYC','KIN','LGU','GND','POS','GEO']],
 'Ecuador':[['NFK','CTG','COL','GYE']],'Peru':[['NFK','CTG','COL','GYE','CLL']],'Paraguay':[['NYC','SSZ','MVD']]}
INL={'Mongolia':'rail','Paraguay':'river'}
svg=open(f"{S}/og/hmap.svg").read()
dest={m.group(3):(float(m.group(1)),float(m.group(2))) for m in re.finditer(r'<circle data-s="[^"]*" data-d="[^"]*" cx="([\d.]+)" cy="([\d.]+)" r="[\d.]+" fill="#ffde59"[^>]*><title>([^<]*)</title>',svg)}
CHAINS=[(['ALG','oWA','NKC','DKR','oWA2','FNA','oWA3','ABJ','LOS','KRI','oWA4','LAD'],'West Africa'),
        (['KIN','LGU','GND','POS','GEO'],'Caribbean'),(['CMB','NAC','BEW','DUR'],'Mozambique Channel')]
N.update({'oWA':(-15.5,27),'oWA2':(-16.5,10.5),'oWA3':(-9.5,4.6),'oWA4':(9.3,-2.5)})
use=collections.Counter(); who=collections.defaultdict(set); ports=set(); inland=[]
for c,chains in R.items():
    if c not in dest: continue
    for ch in chains:
        for a,b in zip(ch,ch[1:]): use[(a,b)]+=1; who[(a,b)].add(c)
    last=chains[-1][-1]; ports.add(last); inland.append((c,last))
def seg(a,b):
    A=P(*N[a]); B=P(*N[b]); k=f'{a}>{b}'
    v=VIA.get(k,'x')
    if v not in ('x',None):
        V=P(*v); C=(2*V[0]-(A[0]+B[0])/2, 2*V[1]-(A[1]+B[1])/2)
    else:
        mx,my=(A[0]+B[0])/2,(A[1]+B[1])/2; d=math.hypot(B[0]-A[0],B[1]-A[1])
        C=(mx,my-(0.18*d if v=='x' else 0))
    return f'M{A[0]:.1f} {A[1]:.1f}Q{C[0]:.1f} {C[1]:.1f} {B[0]:.1f} {B[1]:.1f}'
out=[]
mx=max(use.values())
order=sorted(use.items(),key=lambda kv:-kv[1])
paths=''
inchain=set()
for ch,_ in CHAINS:
    real=[x for x in ch if not x.startswith('o')]
    for a,b in zip(real,real[1:]): inchain.add((a,b))
def spline(keys):
    pts=[P(*N[k]) for k in keys]; d='M%.1f %.1f'%pts[0]
    for i in range(len(pts)-1):
        p0=pts[i-1] if i>0 else pts[i]; p1=pts[i]; p2=pts[i+1]; p3=pts[i+2] if i+2<len(pts) else p2
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6); c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        d+='C%.1f %.1f %.1f %.1f %.1f %.1f'%(c1+c2+p2)
    return d
for ch,nm in CHAINS:
    real=[x for x in ch if not x.startswith('o')]
    n=max(use.get((real[0],real[1]),1),1)
    paths+=f'<path pathLength="1" stroke-width="{0.7+1.5*math.sqrt(n/mx):.2f}" d="{spline(ch)}"><title>{nm}</title></path>'
for (a,b),n in order:
    if (a,b) in inchain: continue
    w=0.7+1.5*math.sqrt(n/mx)
    wrap=' stroke="url(#wfl)"' if b=='Lw' or b=='Pw' else (' stroke="url(#wfr)"' if a in('Le','Pe') else '')
    names=', '.join(sorted(who[(a,b)]))
    lbl=f"{GWN.get(a,HUB.get(a,''))} → {HUB.get(b,'')}".strip(' →')
    paths+=f'<path pathLength="1" stroke-width="{w:.2f}"{wrap} d="{seg(a,b)}"><title>{names}</title></path>'
out.append(f'<g class="rr-sea">{paths}</g>')
il=''
for c,p in inland:
    A=P(*N[p]); B=dest[c]
    if math.hypot(A[0]-B[0],A[1]-B[1])<1.5: continue
    k=INL.get(c,'truck'); il+=f'<path class="{k}" d="M{A[0]:.1f} {A[1]:.1f}L{B[0]:.1f} {B[1]:.1f}"><title>{c}: {"rail" if k=="rail" else ("river barge" if k=="river" else "inland by truck")}</title></path>'
out.append(f'<g class="rr-inland">{il}</g>')
out.append('<g class="rr-ports">'+''.join('<circle cx="%.1f" cy="%.1f" r="1.5"/>'%P(*N[p]) for p in ports if p not in HUB)+'</g>')
lab={'ALG':(0,10,'middle'),'PIR':(5,-3,'start'),'JED':(-5,3,'end'),'NSA':(5,-4,'start'),'CMB':(5,5,'start'),'KIN':(-5,-4,'end'),'CTG':(5,5,'start'),'KHH':(5,-3,'start'),'TSN':(5,-3,'start'),'SOU':(-5,-4,'end'),'SSZ':(5,4,'start'),'COL':(-5,7,'end'),'KFK':(5,-3,'start')}
hubs=set(x for ch in R.values() for c in ch for x in c if x in HUB)
hb=''.join(f'<g class="rr-hub"><rect x="{P(*N[k])[0]-2.7:.1f}" y="{P(*N[k])[1]-2.7:.1f}" width="5.4" height="5.4" transform="rotate(45 {P(*N[k])[0]:.1f} {P(*N[k])[1]:.1f})"/><text x="{P(*N[k])[0]+lab[k][0]:.1f}" y="{P(*N[k])[1]+lab[k][1]:.1f}" text-anchor="{lab[k][2]}">{HUB[k]}</text></g>' for k in sorted(hubs))
out.append(f'<g class="rr-hubs">{hb}</g>')
open(f"{S}/rr/real.svgfrag",'w').write('<g id="rr" class="rr">'+''.join(out)+'</g>')
def desc(c): return [' → '.join(GWN.get(x,HUB.get(x)) for x in ch if x in GWN or x in HUB) for ch in R[c] if any(x in GWN for x in ch) or True]
json.dump({c:[' → '.join([GWN.get(x) or HUB.get(x) for x in ch if (x in GWN or x in HUB)]) for ch in R[c]] for c in R if c in dest},open(f"{S}/rr/routes.json",'w'))
print(len(use),'segments')

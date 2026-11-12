import math,re,json
S="/tmp/claude-0/-home-claude-slg-beta/991b3283-be07-532b-b3c5-8230aedd119b/scratchpad"
def P(lon,lat):
    l=math.radians(lon); p=math.radians(lat); p2=p*p; p4=p2*p2
    x=l*(0.8707-0.131979*p2+p4*(-0.013791+p4*(0.003971*p2-0.001529*p4)))
    y=p*(1.007226+p2*(0.015085+p4*(-0.044475+0.028874*p2-0.005916*p4)))
    return (500+160*x, 260-160*y)
W={ # lon,lat
 'NYC':(-74.05,40.6),'NFK':(-76.3,36.95),'HOU':(-95.0,29.7),'LAX':(-118.25,33.75),'OAK':(-122.3,37.8),'TAC':(-122.42,47.27),
 'oNY':(-70,39.8),'oNFK':(-72,36.2),'ATL1':(-50,38.5),'ATL2':(-25,37.2),'ALG':(-5.45,36.1),
 'gHOU':(-92,27),'gYUC':(-86,22.5),'FLS':(-81.5,24.0),'FLS2':(-79.6,26.5),'oFLA':(-74,30),
 'MOR':(-11,33),'CAN':(-15.5,27),'NKC':(-16.6,18.1),'CVE':(-18.5,15.5),'DKR':(-17.5,14.65),'BJL':(-16.9,13.45),'CKY':(-14,9.45),'FNA':(-13.4,8.4),
 'MLW':(-10.85,6.25),'oCI':(-7,4.0),'ABJ':(-4.0,5.1),'TEM':(0.0,5.5),'LFW':(1.25,6.05),'COO':(2.4,6.25),'LOS':(3.4,6.35),'oGG':(5.5,3.3),'KRI':(9.85,2.9),'MAL':(8.7,3.8),
 'oGAB':(8.5,-1.5),'PNR':(11.8,-4.85),'LAD':(13.2,-8.75),
 'ALB':(0,37.0),'SAR':(9.5,37.5),'MLT':(14.55,35.8),'CRT':(22.5,34.9),'PIR':(23.6,37.9),'AEG':(25.3,39.2),'DAR':(26.3,40.1),'IST':(28.9,40.95),'BOS':(29.2,41.35),
 'CND':(28.7,44.15),'ODS':(30.8,46.45),'BEY':(35.45,33.9),'PSD':(32.3,31.4),'SUZ':(32.55,29.8),'RS1':(34.0,27.6),'GAQ':(34.7,28.4),'AQB':(35.0,29.45),'JED':(39.1,21.45),
 'RS2':(41.0,16.5),'BAB':(43.4,12.6),'ADN':(47.5,12.4),'GUA':(51.8,12.2),'ARB':(62,15.5),'NSA':(72.8,18.9),'MUN':(69.7,22.7),
 'oIN':(73.5,12),'CMB':(79.8,6.9),'DON':(80.8,5.6),'BOB':(87.5,15),'CGP':(91.75,22.2),
 'oKE':(55,-1),'MBA':(39.7,-4.05),'DSM':(39.3,-6.8),'oSOM':(50,4),'MGQ':(45.35,2.0),
 'IO1':(62,-6),'IO2':(50,-12.2),'NAC':(40.7,-14.5),'MOZ':(38.5,-18.5),'BEW':(34.85,-19.85),'oMAP':(35.5,-25.5),'DUR':(31.05,-29.87),'TMM':(49.45,-18.15),'oMAD':(52,-12),
 'oUAE':(60,22.5),'HRM':(57.2,24.6),'KFK':(56.4,25.35),
 'NA1':(-50,45),'NA2':(-20,49),'ENG':(-5.5,49.3),'SOU':(-1.4,50.8),'DOV':(1.8,51.05),'NS1':(5.5,53.8),'SKG':(10.4,57.9),'KAT':(11.6,56.6),'ORE':(12.75,55.65),'BAL1':(15.5,55.1),'GDN':(18.65,54.45),
 'BAL2':(20.5,57.5),'GOF':(22.5,59.6),'HEL':(24.95,60.12),
 'oLA':(-128,31),'TP1':(-160,29),'TPW':(-180.5,28),'TPE':(180.5,26),'TP2':(150,24),'KHH':(120.25,22.6),'MNL':(120.9,14.55),'SCS':(114,15),'HPH':(106.8,20.75),'oHPH':(108.5,18.5),
 'CMP':(107.0,10.35),'oCMP':(108.5,9.5),'KOS':(103.5,10.6),'GTH':(104.3,9.0),
 'COL':(-79.9,9.4),'BAL':(-79.55,8.85),'oPAN':(-80,6.5),'PAC1':(-105,12),'PAC2':(-140,22),'TPW2':(-180.5,30),'TPE2':(180.5,32),'TP3':(150,33),'KST':(129.5,33.6),'BUS':(129.05,35.1),'YS1':(124,36.5),'BHS':(121.2,38.4),'TSN':(117.75,38.95),'UB':(106.9,47.9),
 'KIN':(-76.8,17.9),'WIN':(-73.8,20.2),'oHAI':(-73,19.5),'LAF':(-72.45,18.75),'CAU':(-69.63,18.4),'sCUB':(-80,19.0),'MAR':(-82.75,23.05),
 'PCR':(-87.95,15.85),'STC':(-88.6,15.73),'CTG':(-75.55,10.4),'oCTG':(-76.5,12.5),'LGU':(-66.93,10.62),'oVEN':(-68,12.5),'GND':(-61.75,12.05),'POS':(-61.52,10.65),'oTRI':(-60.5,11.2),'GEO':(-58.17,6.85),'oGUY':(-57.5,8.5),
 'oECU':(-81.5,1),'GYE':(-80.0,-2.3),'oPER':(-81.5,-6.5),'CLL':(-77.2,-12.05),
 'oBRA1':(-60,25),'oBRA2':(-34.5,-6),'oBRA3':(-37.3,-15.5),'SSZ':(-46.3,-24.0),'oURU':(-51,-31),'MVD':(-56.2,-34.95),'RIV':(-58.4,-34.0),'PAR1':(-58.8,-28.5),
 'PQZ':(-90.8,13.9),'COR':(-87.2,12.45),'oMEX':(-108,20),'oGUA':(-96,13.5),
}
HUBS={'ALG':'Algeciras / Tanger Med','PIR':'Piraeus','JED':'Jeddah','NSA':'Nhava Sheva','CMB':'Colombo','KIN':'Kingston','CTG':'Cartagena','KHH':'Kaohsiung','TSN':'Tianjin','SOU':'Southampton','SSZ':'Santos','BAL':'Panama Canal','KFK':'Khor Fakkan'}
# sea legs before transshipment: trunk lines from gateways
T={
 'NFK>ALG':['NFK','oNFK','ATL1','ATL2','ALG'],'NYC>ALG':['NYC','oNY','ATL1','ATL2','ALG'],
 'HOU>ALG':['HOU','gHOU','FLS','FLS2','oFLA','ATL1','ATL2','ALG'],
 'NYC>PIR':['NYC','oNY','ATL1','ATL2','ALG','ALB','SAR','MLT','CRT','PIR'],
 'NFK>NSA':['NFK','oNFK','ATL1','ATL2','ALG','ALB','SAR','MLT','CRT','PSD','SUZ','RS1','JED','RS2','BAB','ADN','GUA','ARB','NSA'],
 'NYC>JED':['NYC','oNY','ATL1','ATL2','ALG','ALB','SAR','MLT','CRT','PSD','SUZ','RS1','JED'],
 'NSA>CMB':['NSA','oIN','CMB'],
 'NYC>SOU':['NYC','oNY','NA1','NA2','ENG','SOU'],
 'LAX>KHH':['LAX','oLA','TP1','TPW','|','TPE','TP2','KHH'],
 'NFK>TSN':['NFK','oNFK','oFLA','WIN','oCTG','COL','BAL','oPAN','PAC1','PAC2','TPW2','|','TPE2','TP3','KST','BUS','YS1','BHS','TSN'],
 'HOU>KIN':['HOU','gHOU','gYUC','sCUB','KIN'],
 'NYC>KIN':['NYC','oNY','oFLA','WIN','KIN'],
 'NYC>CTG':['NYC','oNY','oFLA','WIN','oCTG','CTG'],
 'NFK>CTG':['NFK','oNFK','oFLA','WIN','oCTG','CTG'],
 'NYC>SSZ':['NYC','oNY','oBRA1','oBRA2','oBRA3','SSZ'],
}
# per country: list of (trunk keys..., feeder points after the last hub, inland flag)
R={
 'Mauritania':[('NFK>ALG',['ALG','MOR','CAN','NKC'],'land')],
 'Gambia':[('NFK>ALG',['ALG','MOR','CAN','CVE','BJL'],'land')],
 'Mali':[('NFK>ALG',['ALG','MOR','CAN','CVE','DKR'],'land')],
 'Guinea':[('NFK>ALG',['ALG','MOR','CAN','CVE','CKY'],'land')],
 'Sierra Leone':[('NFK>ALG',['ALG','MOR','CAN','CVE','FNA'],'land')],
 'Liberia':[('NFK>ALG',['ALG','MOR','CAN','CVE','FNA','MLW'],'land')],
 'Ivory Coast':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','ABJ'],'land')],
 'Burkina Faso':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','ABJ'],'land')],
 'Ghana':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','TEM'],'land')],
 'Togo':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','TEM','LFW'],'land')],
 'Benin':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','TEM','COO'],'land')],
 'Nigeria':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','TEM','LOS'],'land')],
 'Equatorial Guinea':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','oGG','MAL'],'land')],
 'Chad':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','oGG','KRI'],'land')],
 'Central African Republic':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','oGG','KRI'],'land')],
 'Angola':[('NFK>ALG',['ALG','MOR','CAN','CVE','MLW','oCI','oGG','oGAB','PNR','LAD'],'land')],
 'Kenya':[('NFK>NSA',['NSA','oKE','MBA'],'land')],
 'Uganda':[('NFK>NSA',['NSA','oKE','MBA'],'land')],
 'South Sudan':[('NFK>NSA',['NSA','oKE','MBA'],'land')],
 'Somalia':[('NFK>NSA',['NSA','oSOM','MGQ'],'land')],
 'Tanzania':[('NFK>NSA',['NSA','oKE','DSM'],'land')],
 'Burundi':[('NFK>NSA',['NSA','oKE','DSM'],'land')],
 'Zambia':[('NFK>NSA',['NSA','oKE','DSM'],'land')],
 'Malawi':[('NFK>NSA',['NSA','NSA>CMB'],None),('NSA>CMB',['CMB','IO1','IO2','NAC'],'land')],
 'Mozambique':[('NFK>NSA',['NSA','NSA>CMB'],None),('NSA>CMB',['CMB','IO1','IO2','NAC','MOZ','BEW'],'land')],
 'Madagascar':[('NFK>NSA',['NSA','NSA>CMB'],None),('NSA>CMB',['CMB','IO1','oMAD','TMM'],'land')],
 'South Africa':[('NFK>NSA',['NSA','NSA>CMB'],None),('NSA>CMB',['CMB','IO1','IO2','NAC','MOZ','oMAP','DUR'],'land')],
 'Eswatini':[('NFK>NSA',['NSA','NSA>CMB'],None),('NSA>CMB',['CMB','IO1','IO2','NAC','MOZ','oMAP','DUR'],'land')],
 'Lesotho':[('NFK>NSA',['NSA','NSA>CMB'],None),('NSA>CMB',['CMB','IO1','IO2','NAC','MOZ','oMAP','DUR'],'land')],
 'Bangladesh':[('NFK>NSA',['NSA','NSA>CMB'],None),('NSA>CMB',['CMB','DON','BOB','CGP'],'land')],
 'UAE':[('NFK>NSA',['NSA','oUAE','HRM','KFK'],'land')],
 'Greece':[('NYC>PIR',['PIR'],'land')],
 'Lebanon':[('NYC>PIR',['PIR','BEY'],'land')],
 'Romania':[('NYC>PIR',['PIR','AEG','DAR','IST','BOS','CND'],'land')],
 'Ukraine':[('NYC>PIR',['PIR','AEG','DAR','IST','BOS','ODS'],'land')],
 'Moldova':[('NYC>PIR',['PIR','AEG','DAR','IST','BOS','ODS'],'land')],
 'Jordan':[('NYC>JED',['JED','RS1','GAQ','AQB'],'land')],
 'Poland':[('NYC>SOU',['SOU','DOV','NS1','SKG','KAT','ORE','BAL1','GDN'],'land')],
 'Finland':[('NYC>SOU',['SOU','DOV','NS1','SKG','KAT','ORE','BAL1','BAL2','GOF','HEL'],'land')],
 'Philippines':[('LAX>KHH',['KHH','MNL'],'land')],
 'Vietnam':[('LAX>KHH',['KHH','SCS','oCMP','CMP'],'land')],
 'Cambodia':[('LAX>KHH',['KHH','SCS','oCMP','GTH','KOS'],'land')],
 'Mongolia':[('NFK>TSN',['TSN'],'rail')],
 'Guatemala':[('HOU',['HOU','gHOU','gYUC','STC'],'land'),('LAX',['LAX','oMEX','oGUA','PQZ'],'land')],
 'Honduras':[('HOU',['HOU','gHOU','gYUC','PCR'],'land')],
 'El Salvador':[('HOU',['HOU','gHOU','gYUC','PCR'],'land'),('LAX',['LAX','oMEX','oGUA','PQZ'],'land')],
 'Nicaragua':[('LAX',['LAX','oMEX','oGUA','PQZ','COR'],'land')],
 'Jamaica':[('HOU>KIN',['KIN'],'land')],
 'Cuba':[('HOU',['HOU','gHOU','gYUC','MAR'],'land')],
 'Haiti':[('NYC>KIN',['KIN','oHAI','LAF'],'land')],
 'Dominican Republic':[('HOU>KIN',['KIN','CAU'],'land')],
 'Panama':[('NYC>KIN',['KIN','COL'],'land')],
 'Colombia':[('NFK>CTG',['CTG'],'land')],
 'Venezuela':[('NFK>CTG',['CTG','oVEN','LGU'],'land')],
 'Trinidad & Tobago':[('NYC>KIN',['KIN','oVEN','oTRI','POS'],'land')],
 'Grenada':[('NYC>KIN',['KIN','oVEN','GND'],'land')],
 'Guyana':[('NYC>KIN',['KIN','oVEN','oTRI','oGUY','GEO'],'land')],
 'Ecuador':[('NYC>CTG',['CTG','COL','BAL','oECU','GYE'],'land')],
 'Peru':[('NYC>CTG',['CTG','COL','BAL','oECU','oPER','CLL'],'land')],
 'Paraguay':[('NYC>SSZ',['SSZ','oURU','MVD','RIV','PAR1'],'river')],
}
GWNAME={'NYC':'New York / NJ','NFK':'Norfolk','HOU':'Houston','LAX':'Los Angeles','OAK':'Oakland','TAC':'Tacoma'}
svg=open(f"{S}/og/hmap.svg").read()
dest={m.group(3):(float(m.group(1)),float(m.group(2))) for m in re.finditer(r'<circle data-s="[^"]*" data-d="[^"]*" cx="([\d.]+)" cy="([\d.]+)" r="[\d.]+" fill="#ffde59"[^>]*><title>([^<]*)</title>',svg)}
def smooth(pts):
    if len(pts)<3: return 'M%.1f %.1f'%pts[0]+''.join('L%.1f %.1f'%q for q in pts[1:])
    d='M%.1f %.1f'%pts[0]
    for i in range(len(pts)-1):
        p0=pts[i-1] if i>0 else pts[i]; p1=pts[i]; p2=pts[i+1]; p3=pts[i+2] if i+2<len(pts) else p2
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6); c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        d+='C%.1f %.1f %.1f %.1f %.1f %.1f'%(c1+c2+p2)
    return d
def segs(keys):
    out=[[]]
    for k in keys:
        if k=='|': out.append([]); continue
        out[-1].append(P(*W[k]))
    return [smooth(s) for s in out if len(s)>1]
trunks={}  # unique trunk paths
legs=[]; hubs_used=set(); ports=set(); inland=[]
def path_for(chain): return segs(chain)
for c,routes in R.items():
    if c not in dest: continue
    seen=[]
    for tk,feed,kind in routes:
        if tk in T:
            ch=T[tk]
            if tk not in trunks: trunks[tk]=ch
            for k in ch:
                if k in HUBS: hubs_used.add(k)
            start=feed
        else:
            start=feed
        fe=[x for x in start if x not in T]
        for k in fe:
            if k in HUBS: hubs_used.add(k)
        if len(fe)>1:
            legs.append((c,fe))
        if kind:
            end=W[fe[-1]] if fe else W[T[tk][-1]]
            ports.add(fe[-1] if fe else T[tk][-1])
            inland.append((c,P(*end),dest[c],kind))
# title per country
def describe(c):
    out=[]
    for tk,feed,kind in R[c]:
        if tk in T:
            ch=[x for x in T[tk] if x in HUBS or x in GWNAME]
        else: ch=[tk]
        out.append(' → '.join([GWNAME.get(x,HUBS.get(x,x)) for x in ch]))
    return out
html=[]
html.append('<g class="rr-trunk">'+''.join(f'<path pathLength="1" d="{d}"><title>{GWNAME.get(T[k][0],T[k][0])} → {HUBS.get(T[k][-1],T[k][-1])}</title></path>' for k in trunks for d in segs(T[k]))+'</g>')
html.append('<g class="rr-feed">'+''.join(f'<path pathLength="1" d="{d}"><title>{c}</title></path>' for c,fe in legs for d in segs(fe))+'</g>')
def inl(c,a,b,kind):
    mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
    return f'<path class="{kind}" d="M{a[0]:.1f} {a[1]:.1f}Q{mx:.1f} {my-2:.1f} {b[0]:.1f} {b[1]:.1f}"><title>{c}: {"rail" if kind=="rail" else ("river barge" if kind=="river" else "inland by truck")}</title></path>'
html.append('<g class="rr-inland">'+''.join(inl(*x) for x in inland if math.hypot(x[1][0]-x[2][0],x[1][1]-x[2][1])>1.5)+'</g>')
html.append('<g class="rr-ports">'+''.join('<circle cx="%.1f" cy="%.1f" r="1.4"/>'%P(*W[k]) for k in ports if k not in HUBS)+'</g>')
lab={'ALG':(0,10,'middle'),'PIR':(4,-3,'start'),'JED':(-4,4,'end'),'NSA':(-4,-4,'end'),'CMB':(4,4,'start'),'KIN':(-5,-4,'end'),'CTG':(4,5,'start'),'KHH':(4,-3,'start'),'TSN':(4,-3,'start'),'SOU':(-4,-4,'end'),'SSZ':(4,4,'start'),'BAL':(-5,6,'end'),'MLT':(2,7,'start'),'KFK':(4,-2,'start')}
hb=''
for k in sorted(hubs_used):
    x,y=P(*W[k]); dx,dy,an=lab.get(k,(4,-3,'start'))
    hb+=f'<g class="rr-hub"><rect x="{x-2.6:.1f}" y="{y-2.6:.1f}" width="5.2" height="5.2" transform="rotate(45 {x:.1f} {y:.1f})"/><text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{an}">{HUBS[k]}</text></g>'
html.append('<g class="rr-hubs">'+hb+'</g>')
open(f"{S}/rr/real.svgfrag",'w').write('<g id="rr" class="rr">'+''.join(html)+'</g>')
json.dump({c:describe(c) for c in R if c in dest},open(f"{S}/rr/routes.json",'w'))
print(len(trunks),len(legs),len(inland),sorted(hubs_used))

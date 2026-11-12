"""Swap the generated real-routes layer (real.svgfrag from gen2.py) into index.html."""
import re,sys
frag_path=sys.argv[1]; p=sys.argv[2] if len(sys.argv)>2 else 'index.html'
f=open(frag_path).read(); n=[0]
def tag(m):
    i=n[0]; n[0]+=1
    return f'<path class="rt" data-s="{0.02+i*0.009:.3f}" data-d=".22" pathLength="1"'
f=re.sub(r'<path pathLength="1"',tag,f)
f=f.replace('<g class="rr-inland">','<g class="rr-inland" data-s=".62" data-d=".14">').replace('<g class="rr-ports">','<g class="rr-ports" data-s=".6" data-d=".12">').replace('<g class="rr-hubs">','<g class="rr-hubs" data-s=".55" data-d=".12">').replace('<g id="rr" class="rr">','<g class="rr">')
s=open(p).read()
i=s.index('<g class="rr">'); j=s.index('<g font-family="inherit" font-weight="700" font-size="10"',i)
s=s[:i]+f+s[j:]; open(p,'w').write(s); print('swapped',n[0],'paths')

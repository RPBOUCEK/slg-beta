(opts)=>{
  const vw=innerWidth, vh=innerHeight, Y=scrollY, maxY=document.documentElement.scrollHeight-vh, out=[];
  const visC=new Map();
  const isVis=el=>{ if(visC.has(el)) return visC.get(el); let v=true;
    for(let e=el;e&&e.nodeType===1;e=e.parentElement){ const cs=getComputedStyle(e);
      if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)<0.08){v=false;break;}
      if(e.hasAttribute&&e.getAttribute('opacity')!==null&&parseFloat(e.getAttribute('opacity'))<0.08){v=false;break;} }
    visC.set(el,v); return v; };
  const pnC=new Map();
  const noPtr=el=>{ if(pnC.has(el)) return pnC.get(el); const v=getComputedStyle(el).pointerEvents==='none'; pnC.set(el,v); return v; };
  const fixedOf=el=>{ for(let e=el;e&&e.nodeType===1;e=e.parentElement){ const p=getComputedStyle(e).position; if(p==='fixed'||p==='sticky') return e; } return null; };
  const clip=(el,r)=>{ let L=r.left,T=r.top,R=r.right,B=r.bottom;
    for(let e=el.parentElement;e&&e!==document.documentElement;e=e.parentElement){ const cs=getComputedStyle(e);
      const ox=cs.overflowX!=='visible', oy=cs.overflowY!=='visible';
      if(ox||oy){ const b=e.getBoundingClientRect(); if(ox){L=Math.max(L,b.left);R=Math.min(R,b.right);} if(oy){T=Math.max(T,b.top);B=Math.min(B,b.bottom);} }
      if(cs.position==='fixed') break; }
    L=Math.max(L,0);T=Math.max(T,0);R=Math.min(R,vw);B=Math.min(B,vh);
    return (R-L>1.5&&B-T>1.5)?{left:L,top:T,right:R,bottom:B}:null; };
  const desc=el=>{ let s=el.tagName.toLowerCase(); if(el.id) s+='#'+el.id; const c=(el.getAttribute('class')||'').trim().split(/\s+/).filter(Boolean).slice(0,2); if(c.length) s+='.'+c.join('.');
    const t=(el.textContent||'').replace(/\s+/g,' ').trim().slice(0,40); return t?`${s} "${t}"`:s; };
  const items=[];
  const tw=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,{acceptNode:n=>/\S/.test(n.nodeValue)?1:2});
  const rg=document.createRange();
  for(let n=tw.nextNode();n;n=tw.nextNode()){ const el=n.parentElement; if(!el||el.closest('script,style,noscript,title,#scur,[aria-hidden="true"] title')) continue;
    if(el.closest('svg')&&el.tagName.toLowerCase()==='title') continue;
    if(!isVis(el)) continue; rg.selectNodeContents(n);
    for(const r of rg.getClientRects()){ if(r.width<2||r.height<2) continue; const c=clip(el,r); if(c) items.push({el,r:c,kind:'text'}); } }
  for(const el of document.querySelectorAll('button,a.btn,.navbtn,input,textarea,select,.tile,[role=button],.fbPin,.stn b')){
    if(!isVis(el)) continue; const r=el.getBoundingClientRect(); if(r.width<2||r.height<2) continue; const c=clip(el,r); if(c) items.push({el,r:c,kind:'box'}); }
  const NAV=document.getElementById('nav')||document.querySelector('nav');
  const menuOpen=document.getElementById('menu')&&document.getElementById('menu').classList.contains('open');
  const classify=(itemEl,occ)=>{ // returns true if this overlap should be reported
    if(!occ) return false;
    if(!isVis(occ)) return false;
    if(occ.closest&&occ.closest('#scur')) return false;
    const fi=fixedOf(itemEl), fo=fixedOf(occ);
    if(menuOpen&&(occ.closest('#menu')||occ.id==='scrim')&&!itemEl.closest('#menu')) return false;
    if(fo&&fi!==fo){
      if(NAV&&(fo===NAV||NAV.contains(fo)||fo.contains(NAV))) return Y<=2||(!!fi&&getComputedStyle(fi).position==='sticky'&&Math.abs(fi.getBoundingClientRect().top-(parseFloat(getComputedStyle(fi).top)||0))<1.5);
      if(fo.id==='prog') return false;
      if(!fi) return Y>=maxY-2;  // floating controls: only a problem where the page can't scroll further
    }
    if(fi&&!fo&&!(fo)) return false; // a fixed item drawn under page content cannot happen visually unless z-order bug; skip
    return true; };
  const rel=(a,b)=>a===b||a.contains(b)||b.contains(a);
  // 1) occlusion sampling
  for(const it of items){ if(noPtr(it.el)) continue; const {left:L,top:T,right:R,bottom:B}=it.r;
    const pts=[[(L+R)/2,(T+B)/2],[L+(R-L)*.2,T+(B-T)*.3],[L+(R-L)*.8,T+(B-T)*.3],[L+(R-L)*.2,T+(B-T)*.75],[L+(R-L)*.8,T+(B-T)*.75]];
    let bad=0, occ=null;
    for(const [x,y] of pts){ const top=document.elementFromPoint(x,y); if(!top) continue;
      if(rel(top,it.el)) continue; if(top.closest&&top.closest('svg')&&it.el.closest('svg')===top.closest('svg')) continue;
      // label wrapping/containing relations, e.g. text inside a button whose child is hit
      if(it.el.closest('a,button,label')&&it.el.closest('a,button,label').contains(top)) continue;
      if(classify(it.el,top)){bad++;occ=top;} }
    if(bad>=2||(bad>=1&&(R-L)*(B-T)<200)) out.push({type:'occluded',item:desc(it.el),by:desc(occ),y:Y,r:[L,T,R,B].map(v=>Math.round(v))}); }
  // 2) text over text (catches pointer-events:none layers)
  const tx=items.filter(i=>i.kind==='text');
  tx.sort((a,b)=>a.r.top-b.r.top);
  for(let i=0;i<tx.length;i++){ const a=tx[i];
    for(let j=i+1;j<tx.length&&tx[j].r.top<a.r.bottom;j++){ const b=tx[j]; if(rel(a.el,b.el)) continue;
      const ox=Math.min(a.r.right,b.r.right)-Math.max(a.r.left,b.r.left), oy=Math.min(a.r.bottom,b.r.bottom)-Math.max(a.r.top,b.r.top);
      if(ox<3||oy<3) continue;
      const amin=Math.min((a.r.right-a.r.left)*(a.r.bottom-a.r.top),(b.r.right-b.r.left)*(b.r.bottom-b.r.top));
      if(ox*oy<.18*amin) continue;
      const fa=fixedOf(a.el), fb=fixedOf(b.el);
      if(fa!==fb){ const f=fa||fb, other=fa?b.el:a.el; if(!classify(other,f)) continue; }
      if(menuOpen&&(!!a.el.closest('#menu'))!==(!!b.el.closest('#menu'))) continue;
      out.push({type:'text-overlap',a:desc(a.el),b:desc(b.el),y:Y,ov:[Math.round(ox),Math.round(oy)]}); } }
  // 3) horizontal overflow
  const sw=document.documentElement.scrollWidth;
  if(sw>vw+1){ const cul=[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect(); return r.right>vw+1&&r.width>0&&isVis(e)&&!clip(e,{left:vw+1,top:r.top,right:r.right,bottom:r.bottom});}).slice(0,3).map(desc);
    out.push({type:'h-overflow',sw,vw,cul}); }
  return out; }

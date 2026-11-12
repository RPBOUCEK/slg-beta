# Home journey track (parked Nov 12, 2026)

Scroll-driven shipment track that sat under the three Home tiles (Drayage & trucking / Ocean freight / Inland & on-carriage). Removed from the page at Robertson's request to keep Home simple; kept here to bring back later.

To restore: put the markup back as the last child of `.cols.legs`, and keep the CSS and script below (both are still in `index.html`, dormant: the script exits when `#lsSvg` is missing). An earlier version with truck, train and vessel pictograms is in git at commit 57c77b3.

## Markup
```html
<div class="legscene" aria-hidden="true"><svg id="lsSvg"></svg></div>
```

## CSS
```css
  .legscene{grid-column:1/-1;border-right:1px solid var(--ln);border-bottom:1px solid var(--ln);overflow:hidden}
  .legscene svg{display:block;width:100%;height:168px}
  .legscene .base{fill:none;stroke:var(--ln);stroke-width:1}
  .legscene .trk{fill:none;stroke:var(--fbo);stroke-width:1.5;stroke-linecap:round}
  .legscene .trk.inl,.legscene .done .inl{stroke-dasharray:1 8}
  .legscene .trk.tie{stroke-width:1;stroke-linecap:butt}
  .legscene .done path{fill:none;stroke:var(--g);stroke-width:2.5;stroke-linecap:round}
  .legscene .done .tie{stroke-width:1.25;stroke-linecap:butt}
  .legscene .nd{fill:var(--w);stroke:var(--g);stroke-width:1.5;transition:fill .3s}
  .legscene .nd.hit{fill:var(--b)}
  .legscene .halo{fill:var(--b);opacity:0;transform-box:fill-box;transform-origin:center}
  .legscene .halo.hit{animation:lshalo 1.8s ease-out infinite}
  @keyframes lshalo{0%{opacity:.55;transform:scale(1)}100%{opacity:0;transform:scale(3.4)}}
  .legscene text{font-family:var(--mono);font-size:10px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;fill:var(--cue);transition:fill .3s,opacity .3s}
  .legscene text.hit{fill:var(--g)}
  .legscene text.mode{font-weight:700;opacity:.45}
  .legscene text.mode.hit{opacity:1}
  .legscene .box rect{fill:var(--b);stroke:var(--g);stroke-width:1.5}
  .legscene .box path{fill:none;stroke:var(--g);stroke-width:1;opacity:.45}
  @media(max-width:560px){.legscene svg{height:132px}.legscene text{font-size:9px;letter-spacing:.08em}}
  @media(prefers-reduced-motion:reduce){.legscene .halo.hit{animation:none}}
```

## Script
```js
/* ---------- Home legs: a shipment track. One yellow container travels origin > railhead > port of export > port of discharge > final delivery as the page scrolls. No vehicles: each mode has its own line (road solid, rail with ties, ocean an arc, inland dotted) ---------- */
(function(){
  const box=document.querySelector(".cols.legs"), svg=document.getElementById("lsSvg"); if(!box||!svg) return;
  const legs=[...box.querySelectorAll("article")], scene=svg.closest(".legscene");
  const cl=v=>Math.max(0,Math.min(1,v)), sm=v=>{v=cl(v);return v*v*(3-2*v)};
  let W=0, H=0, Y=0, RISE=0, X=[], XR=0, els=null;
  function build(){
    W=Math.max(300,Math.round(scene.clientWidth)); const small=W<560, pad=small?22:36;
    H=small?132:168; Y=small?82:108; RISE=small?64:96;          /* strip height, line height, arc control offset (peak = RISE/2) */
    const BW=small?36:50, BH=small?15:21;
    X=[pad, W/3, W*2/3, W-pad]; XR=(X[0]+X[1])/2;
    const names=small?["Origin","Export","Discharge","Delivery"]:["Origin","Port of export","Port of discharge","Final delivery"];
    const modes=small?[]:[["Road",(X[0]+XR)/2],["Rail",(XR+X[1])/2],["Ocean",(X[1]+X[2])/2],["Inland",(X[2]+X[3])/2]];
    const road=`M${X[0]} ${Y}H${XR}`, rail=`M${XR} ${Y}H${X[1]}`, sea=`M${X[1]} ${Y}Q${(X[1]+X[2])/2} ${Y-RISE} ${X[2]} ${Y}`, inl=`M${X[2]} ${Y}H${X[3]}`;
    const ties=()=>{ let d=""; for(let x=XR+8;x<X[1]-6;x+=8) d+=`M${x.toFixed(1)} ${Y-3}v6`; return d; };
    const node=k=>(k===1||k===2)?`<path class="nd" d="M${X[k]} ${Y-7}l7 7-7 7-7-7z"/>`:`<circle class="nd" cx="${X[k]}" cy="${Y}" r="5"/>`;
    const anchor=k=>k===0?"start":k===3?"end":"middle", lx=k=>k===0?X[0]-5:k===3?X[3]+5:X[k];
    const st=(BW-8)/5; let ribs=""; for(let i=1;i<=4;i++) ribs+=`M${(-BW/2+4+st*i).toFixed(1)} ${-BH-2}v${BH-8}`;
    svg.style.height=H+"px"; svg.setAttribute("viewBox",`0 0 ${W} ${H}`); svg.setAttribute("preserveAspectRatio","xMidYMid meet");
    svg.innerHTML=`<defs><clipPath id="lsClip"><rect id="lsClipR" x="0" y="0" width="0" height="${H}"/></clipPath></defs>
      <path class="base" d="M${X[1]} ${Y}H${X[2]}"/>
      <path class="trk" d="${road}"/><path class="trk" d="${rail}"/><path class="trk tie" d="${ties()}"/><path class="trk" d="${sea}"/><path class="trk inl" d="${inl}"/>
      <g class="done" clip-path="url(#lsClip)"><path d="${road}"/><path d="${rail}"/><path class="tie" d="${ties()}"/><path d="${sea}"/><path class="inl" d="${inl}"/></g>
      <circle class="halo" cx="${X[3]}" cy="${Y}" r="5"/>
      ${[0,1,2,3].map(node).join("")}<circle class="nd mid" cx="${XR}" cy="${Y}" r="3.5"/>
      ${[0,1,2,3].map(k=>`<text class="stop" x="${lx(k).toFixed(1)}" y="${Y+30}" text-anchor="${anchor(k)}">${names[k]}</text>`).join("")}
      ${small?"":`<text class="mid" x="${XR}" y="${Y+30}" text-anchor="middle">Railhead</text>`}
      ${modes.map(([m,x],i)=>`<text class="mode" data-i="${i}" x="${x.toFixed(1)}" y="22" text-anchor="middle">${m}</text>`).join("")}
      <g class="box" id="lsBox"><rect x="${-BW/2}" y="${-BH-6}" width="${BW}" height="${BH}"/><path d="${ribs}"/></g>`;
    const q=x=>svg.querySelector(x);
    els={clip:q("#lsClipR"), box:q("#lsBox"), nd:[...svg.querySelectorAll(".nd:not(.mid)")], tx:[...svg.querySelectorAll("text.stop")], mid:[...svg.querySelectorAll(".mid")], mode:[...svg.querySelectorAll("text.mode")], halo:q(".halo")};
  }
  let cur=-1;
  const show=n=>{ if(n===cur) return; cur=n; legs.forEach((a,k)=>a.classList.toggle("on",k===n)); };
  function paint(p){                                    /* p: 0..1 across the whole journey */
    const f=cl(p)*3, n=Math.min(2,Math.floor(f)), u=sm(f-n);   /* ease inside each leg so the container settles at every port */
    const x=X[n]+(X[n+1]-X[n])*u, y=n===1?Y-RISE*2*u*(1-u):Y;
    els.box.setAttribute("transform",`translate(${x.toFixed(2)} ${y.toFixed(2)})`);
    els.clip.setAttribute("width",x.toFixed(2));
    const reached=k=>x>=X[k]-.5, seg=n===0?(x<XR?0:1):n+1;
    els.nd.forEach((e,k)=>e.classList.toggle("hit",reached(k))); els.tx.forEach((e,k)=>e.classList.toggle("hit",reached(k)));
    els.mid.forEach(e=>e.classList.toggle("hit",x>=XR-.5)); els.halo.classList.toggle("hit",reached(3));
    els.mode.forEach((e,i)=>e.classList.toggle("hit",i===seg&&!reached(3)));
    show(n); legs.forEach((a,k)=>a.style.setProperty("--lp",(k<n?1:k>n?0:f-n).toFixed(3)));
  }
  build();
  if(matchMedia("(prefers-reduced-motion: reduce)").matches){ paint(.5); addEventListener("resize",()=>{build();paint(.5)}); return; }
  /* the journey follows the page. It starts as the strip rises into view and is finished while the three tiles above are still on screen */
  const A=()=>innerHeight*.97;
  const Z=()=>{ const need=96+box.getBoundingClientRect().height; return Math.min(Math.max(innerHeight*.5,need),innerHeight*.72); };
  const prog=()=>{ const r=scene.getBoundingClientRect(); return cl((A()-r.bottom)/(A()-Z())); };
  let p=prog(), target=p, raf=0;
  const tick=()=>{ p+=(target-p)*.16; if(Math.abs(target-p)<.0008) p=target; paint(p); raf=(p!==target)?requestAnimationFrame(tick):0; };
  const onScroll=()=>{ target=prog(); if(!raf) raf=requestAnimationFrame(tick); };
  addEventListener("scroll",onScroll,{passive:true}); addEventListener("hashchange",()=>setTimeout(onScroll,80));
  addEventListener("resize",()=>{ if(Math.round(scene.clientWidth)!==W) build(); p=target=prog(); paint(p); });
  legs.forEach((a,k)=>a.addEventListener("click",()=>{ /* jump the page to the middle of that leg */
    const want=(k+.5)/3, r=scene.getBoundingClientRect();
    scrollTo({top:scrollY+r.bottom-(A()-want*(A()-Z())),behavior:"smooth"}); }));
  paint(p);
})();
```

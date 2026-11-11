(()=>{
  const role=window.__ROLE||"reviewer";
  const store=window.__STORE=new Map(Object.entries(JSON.parse(sessionStorage.getItem("mockstore")||"{}")));
  const subs=[];
  const save=()=>{sessionStorage.setItem("mockstore",JSON.stringify(Object.fromEntries(store)));subs.forEach(f=>f());};
  const visible=path=>role==="admin"||!(path.startsWith("feedback/"))||path.split("/")[1]===window.__ME;
  const merge=(a,b)=>{const o=Object.assign({},a);for(const[k,v]of Object.entries(b)){o[k]=(v&&typeof v==="object"&&!Array.isArray(v)&&o[k]&&typeof o[k]==="object")?merge(o[k],v):v;}return o;};
  const snapOf=path=>({id:path.split("/").pop(),exists:store.has(path)&&visible(path),data:()=>store.has(path)?JSON.parse(JSON.stringify(store.get(path))):undefined});
  const docRef=path=>({id:path.split("/").pop(),path,
    get:async()=>snapOf(path),
    set:async d=>{store.set(path,d);save();},
    update:async d=>{if(!store.has(path))throw{code:"invalid_argument"};store.set(path,merge(store.get(path),d));save();},
    delete:async()=>{store.delete(path);save();}});
  const colRef=path=>({path,doc:id=>docRef(path+"/"+id),
    onSnapshot:(next)=>{const f=()=>{const docs=[...store.keys()].filter(k=>k.startsWith(path+"/")&&k.split("/").length===path.split("/").length+1&&visible(k)).map(snapOf);next({docs,size:docs.length,empty:!docs.length});};subs.push(f);setTimeout(f,0);return()=>{};},
    get:async()=>({docs:[...store.keys()].filter(k=>k.startsWith(path+"/")).map(snapOf)})});
  const db={doc:docRef,collection:colRef};
  window.__ME=role==="admin"?"u_owner0000000000000000":"u_reviewer00000000000000";
  const user={id:async()=>window.__ME,isOwner:async()=>role==="admin",canEdit:async()=>true,can:async()=>true,
    profiles:async ids=>Object.fromEntries([].concat(ids).map(i=>[i,{id:i,name:i.startsWith("u_rev")?"Corbin":"Robertson"}]))};
  window.claude={use:async n=>n==="db"?db:n==="user"?user:null};
})();

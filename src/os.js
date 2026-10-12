window.OS=(function(){
  var id=(document.documentElement.getAttribute('data-app')||'app');
  var mem={};
  var embedded=false;try{embedded=window.parent&&window.parent!==window}catch(e){}
  function key(k){return 'nexo.'+id+'.'+k}
  function load(k,d){try{var v=localStorage.getItem(key(k));if(v!=null)return JSON.parse(v)}catch(e){}return (k in mem)?mem[k]:d}
  function save(k,v){mem[k]=v;try{localStorage.setItem(key(k),JSON.stringify(v))}catch(e){}}
  function post(msg){msg.nexo=1;msg.app=id;try{if(embedded)window.parent.postMessage(msg,'*')}catch(e){}}
  var box;
  function toast(txt,kind){
    if(embedded)return;
    if(!box){box=document.createElement('div');box.style.cssText='position:fixed;left:50%;top:14px;transform:translateX(-50%);z-index:99999;display:flex;flex-direction:column;gap:6px;align-items:center;pointer-events:none;font:600 13px/1.2 system-ui,sans-serif';document.body.appendChild(box)}
    var t=document.createElement('div');t.textContent=txt;
    t.style.cssText='background:rgba(12,12,16,.88);color:#fff;padding:8px 14px;border-radius:999px;backdrop-filter:blur(6px);box-shadow:0 6px 20px rgba(0,0,0,.25);transition:opacity .4s,transform .4s;transform:translateY(-6px);opacity:0';
    box.appendChild(t);requestAnimationFrame(function(){t.style.opacity=1;t.style.transform='none'});
    setTimeout(function(){t.style.opacity=0;setTimeout(function(){t.remove()},400)},2300);
  }
  var awarded=load('__ach',{});
  return {
    id:id,embedded:embedded,load:load,save:save,
    xp:function(n,why){n=Math.round(n);if(n<=0)return;post({type:'xp',n:n,why:why||''});toast('+'+n+' XP · '+(why||''))},
    achieve:function(code,name,desc){if(awarded[code])return false;awarded[code]=1;save('__ach',awarded);post({type:'ach',code:code,name:name,desc:desc||''});toast('🏆 '+name);return true},
    stat:function(k,v){post({type:'stat',k:k,v:v})}
  };
})();

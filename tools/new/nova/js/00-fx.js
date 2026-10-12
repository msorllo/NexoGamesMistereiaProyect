/* ===== FX: kit premium compartido (copiado en cada app; mantener igual en todas) ===== */
const FX=(()=>{
 const F={t:0,dt:0,tweens:[],shakeA:0,reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,hq:/[?&]hq/.test(location.search)};
 const clock=new THREE.Clock();
 F.lin=h=>new THREE.Color(h).convertSRGBToLinear();
 F.ease={out:t=>1-Math.pow(1-t,3),inOut:t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,back:t=>{const c=1.70158;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2)},elastic:t=>t===0||t===1?t:Math.pow(2,-10*t)*Math.sin((t*10-.75)*2*Math.PI/3)+1,lin:t=>t};
 F.b64=s=>{const b=atob(s),a=new Uint8Array(b.length);for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a.buffer};
 F.init=(o={})=>{
  const canvas=document.getElementById('c');
  const r=new THREE.WebGLRenderer({canvas,antialias:false,powerPreference:'high-performance'});
  r.setPixelRatio(Math.min(devicePixelRatio,2));r.outputEncoding=THREE.sRGBEncoding;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=o.exposure??1;
  r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;
  const scene=new THREE.Scene();scene.background=F.lin(o.bg||'#101010');
  if(o.fog)scene.fog=new THREE.Fog(F.lin(o.fog[0]),o.fog[1],o.fog[2]);
  const pm=new THREE.PMREMGenerator(r);scene.environment=pm.fromScene(new THREE.RoomEnvironment(),.04).texture;
  const camera=new THREE.PerspectiveCamera(o.fov||40,1,.05,300);
  const rt=new THREE.WebGLRenderTarget(4,4,{type:THREE.HalfFloatType,samples:r.capabilities.isWebGL2?4:0});
  const composer=new THREE.EffectComposer(r,rt);composer.addPass(new THREE.RenderPass(scene,camera));
  const b=o.bloom||[.55,.5,.86];const bloom=new THREE.UnrealBloomPass(new THREE.Vector2(256,256),b[0],b[1],b[2]);composer.addPass(bloom);
  composer.addPass(new THREE.ShaderPass(THREE.GammaCorrectionShader));
  Object.assign(F,{renderer:r,scene,camera,composer,bloom});
  const rs=()=>{const w=innerWidth,h=innerHeight;r.setSize(w,h,false);composer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();F.onResize&&F.onResize(w,h)};
  addEventListener('resize',rs);rs();F.resize=rs;
  F.initParticles();return F};
 /* Calidad adaptativa: si va lento, baja resolución y luego quita bloom */
 let fr=[],lvl=0;function quality(){if(lvl>1||F.hq)return;fr.push(F.dt);if(fr.length<90)return;const avg=fr.reduce((a,b)=>a+b)/fr.length;fr=[];if(avg>1/38){lvl++;if(lvl===1)F.renderer.setPixelRatio(1);else F.bloom.enabled=false;F.resize()}}
 /* Tweens */
 F.tween=(obj,to,dur=.5,ease='out',done)=>{const from={};for(const k in to)from[k]=obj[k];const tw={obj,from,to,dur:Math.max(.001,dur),t:0,ease:F.ease[ease]||ease,done};F.tweens=F.tweens.filter(x=>!(x.obj===obj&&Object.keys(to).some(k=>k in x.to)));F.tweens.push(tw);return tw};
 function stepTweens(dt){for(let i=F.tweens.length-1;i>=0;i--){const w=F.tweens[i];w.t+=dt;const p=Math.min(1,w.t/w.dur),e=w.ease(p);for(const k in w.to)w.obj[k]=w.from[k]+(w.to[k]-w.from[k])*e;if(p>=1){F.tweens.splice(i,1);w.done&&w.done()}}}
 /* Partículas: pool único de puntos aditivos */
 const N=1400;let pts,pos,col,vel,life,maxl,gra,drag,pi=0,baseCol;
 F.initParticles=()=>{const g=new THREE.BufferGeometry();pos=new Float32Array(N*3);col=new Float32Array(N*3);vel=new Float32Array(N*3);life=new Float32Array(N);maxl=new Float32Array(N);gra=new Float32Array(N);drag=new Float32Array(N);baseCol=new Float32Array(N*3);
  for(let i=0;i<N;i++)pos[i*3+1]=-999;g.setAttribute('position',new THREE.BufferAttribute(pos,3));g.setAttribute('color',new THREE.BufferAttribute(col,3));
  const c=document.createElement('canvas');c.width=c.height=64;const x=c.getContext('2d');const gr=x.createRadialGradient(32,32,0,32,32,32);gr.addColorStop(0,'#fff');gr.addColorStop(.25,'rgba(255,255,255,.8)');gr.addColorStop(1,'rgba(255,255,255,0)');x.fillStyle=gr;x.fillRect(0,0,64,64);
  pts=new THREE.Points(g,new THREE.PointsMaterial({size:.12,map:new THREE.CanvasTexture(c),vertexColors:true,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,sizeAttenuation:true}));pts.frustumCulled=false;pts.renderOrder=10;F.scene.add(pts);F.points=pts};
 F.burst=(p,o={})=>{const n=o.count||30,c=new THREE.Color(o.color||'#ffffff'),sp=o.speed??2,up=o.up??1;for(let k=0;k<n;k++){const i=pi;pi=(pi+1)%N;const th=Math.random()*Math.PI*2,ph=Math.acos(2*Math.random()-1),s=sp*(.35+Math.random()*.65);
  pos[i*3]=p.x+(o.spread||0)*(Math.random()-.5);pos[i*3+1]=p.y;pos[i*3+2]=p.z+(o.spread||0)*(Math.random()-.5);
  vel[i*3]=Math.sin(ph)*Math.cos(th)*s;vel[i*3+1]=Math.abs(Math.cos(ph))*s*up+(o.lift||0);vel[i*3+2]=Math.sin(ph)*Math.sin(th)*s;
  const j=o.jitter??.15;baseCol[i*3]=c.r*(1-j*Math.random());baseCol[i*3+1]=c.g*(1-j*Math.random());baseCol[i*3+2]=c.b*(1-j*Math.random());
  maxl[i]=life[i]=(o.life||.9)*(.6+Math.random()*.4);gra[i]=o.gravity??-4;drag[i]=o.drag??1.2}};
 function stepParticles(dt){if(!pos)return;for(let i=0;i<N;i++){if(life[i]<=0)continue;life[i]-=dt;const k=Math.max(0,life[i]/maxl[i]);const d=Math.exp(-drag[i]*dt);vel[i*3]*=d;vel[i*3+2]*=d;vel[i*3+1]=vel[i*3+1]*d+gra[i]*dt;
  pos[i*3]+=vel[i*3]*dt;pos[i*3+1]+=vel[i*3+1]*dt;pos[i*3+2]+=vel[i*3+2]*dt;const f=k*k;col[i*3]=baseCol[i*3]*f;col[i*3+1]=baseCol[i*3+1]*f;col[i*3+2]=baseCol[i*3+2]*f;if(life[i]<=0)pos[i*3+1]=-999}
  pts.geometry.attributes.position.needsUpdate=true;pts.geometry.attributes.color.needsUpdate=true}
 /* Sacudida de cámara y vibración */
 F.shake=(a=.08)=>{if(!F.reduced)F.shakeA=Math.max(F.shakeA,a)};
 F.buzz=(ms=12)=>{try{navigator.vibrate&&navigator.vibrate(ms)}catch(e){}};
 /* Audio sintetizado (sin archivos) */
 let ac,master;F.muted=false;
 F.audio=()=>{try{if(!ac){ac=new (window.AudioContext||window.webkitAudioContext)();master=ac.createGain();master.gain.value=.5;master.connect(ac.destination)}if(ac.state==='suspended')ac.resume()}catch(e){}return ac};
 F.tone=(f,d=.2,type='sine',v=.08,at=0,glide)=>{const a=F.audio();if(!a||F.muted)return;const t=a.currentTime+at,o=a.createOscillator(),g=a.createGain();o.type=type;o.frequency.setValueAtTime(f,t);if(glide)o.frequency.exponentialRampToValueAtTime(glide,t+d);g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(v,t+.01);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g).connect(master);o.start(t);o.stop(t+d+.05)};
 F.noise=(d=.3,v=.1,freq=1200,q=.7,at=0,type='bandpass')=>{const a=F.audio();if(!a||F.muted)return;const t=a.currentTime+at,len=Math.ceil(a.sampleRate*d),buf=a.createBuffer(1,len,a.sampleRate),ch=buf.getChannelData(0);for(let i=0;i<len;i++)ch[i]=(Math.random()*2-1)*(1-i/len);const s=a.createBufferSource();s.buffer=buf;const f=a.createBiquadFilter();f.type=type;f.frequency.value=freq;f.Q.value=q;const g=a.createGain();g.gain.value=v;s.connect(f).connect(g).connect(master);s.start(t)};
 /* Número animado en un elemento */
 F.count=(el,to,dur=.6,fmt=v=>Math.round(v))=>{const from=+(el.dataset.v||0);el.dataset.v=to;const o={v:from};F.tween(o,{v:to},dur,'out');const upd=()=>{el.textContent=fmt(o.v);if(o.v!==to&&F.tweens.some(w=>w.obj===o))requestAnimationFrame(upd);else el.textContent=fmt(to)};upd()};
 /* Bucle: pausa en pestaña oculta, dt limitado */
 let raf=0,running=false;F.onFrame=null;
 function frame(){raf=requestAnimationFrame(frame);F.dt=Math.min(.05,Math.max(0,clock.getDelta()));F.t+=F.dt;stepTweens(F.dt);stepParticles(F.dt);F.onFrame&&F.onFrame(F.dt,F.t);
  let sx=0,sy=0;if(F.shakeA>.0005){sx=(Math.random()-.5)*F.shakeA;sy=(Math.random()-.5)*F.shakeA;F.shakeA*=Math.exp(-9*F.dt);F.camera.position.x+=sx;F.camera.position.y+=sy}
  F.composer.render(F.dt);if(sx||sy){F.camera.position.x-=sx;F.camera.position.y-=sy}quality()}
 F.start=()=>{if(running)return;running=true;clock.getDelta();frame()};
 document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(raf);running=false}else F.start()});
 /* Carga del GLB de Blender -> LIB[nombre] */
 F.LIB={};F.get=n=>{const s=F.LIB[n];if(!s)throw new Error('Falta el modelo '+n);return s.clone(true)};
 F.load=(done,fail)=>{new THREE.GLTFLoader().parse(F.b64(GLB),'',g=>{g.scene.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});[...g.scene.children].forEach(c=>F.LIB[c.name]=c);const L=document.getElementById('load');if(L){L.style.opacity=0;setTimeout(()=>L.remove(),600)}done()},e=>{const L=document.getElementById('load');if(L)L.firstElementChild.textContent='No se pudieron cargar los modelos 3D.';fail&&fail(e)})};
 return F})();
/* ===== fin FX ===== */

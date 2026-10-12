(()=>{'use strict';
/* ==== 65-audio.js · NOVA SURGE · música acid procedural, efectos con nombre y locutor ====
 Grafo propio sobre FX.audio(): [pistas]→mus→duck─┐
                                [efectos]→sfx─────┼→master→glue(comp)→limitador→soft-clip(≤0.92)→mute→destino
                                [envíos]→reverb───┘
 Todo el sintetizador vive en Engine(ctx) y sirve para cualquier BaseAudioContext (también Offline, para pruebas). */
const W=window;
const _FX=(typeof FX!=='undefined'&&FX)||null;
const _SND=(typeof SND!=='undefined'&&SND)||W.SND||(W.SND={});
const _MUS=(typeof MUS!=='undefined'&&MUS)||W.MUS||(W.MUS={});
const _SAVE=(typeof SAVE!=='undefined'&&SAVE)||{settings:{music:1,sfx:1,voice:1,shake:1},persist(){}};
const _N=(typeof N!=='undefined'&&N)||null;
const _REG=(typeof REG!=='undefined'&&REG)||null;
const _BUS=(typeof BUS!=='undefined'&&BUS&&typeof BUS.on==='function')?BUS:(()=>{const m={};return{on(e,f){(m[e]=m[e]||[]).push(f)},off(e,f){m[e]=(m[e]||[]).filter(x=>x!==f)},emit(e,d){(m[e]||[]).slice().forEach(f=>{try{f(d)}catch(x){}})}}})();

/* ---------- utilidades musicales ---------- */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const mtof=m=>440*Math.pow(2,(m-69)/12);
const mulberry=a=>()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
const hash=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0};
const tri=x=>{x-=Math.floor(x);return 1-Math.abs(x*2-1)};
/* escalas (semitonos) */
const SC={aeo:[0,2,3,5,7,8,10],dor:[0,2,3,5,7,9,10],phr:[0,1,3,5,7,8,10],hmin:[0,2,3,5,7,8,11],phd:[0,1,4,5,7,8,10],ion:[0,2,4,5,7,9,11]};
/* grados "pentatónicos" dentro de cada escala (para la chatarra) y desplazamiento al acorde mayor más cercano (fanfarrias) */
const PENT={aeo:[0,2,3,4,6],dor:[0,2,3,4,6],phr:[0,2,3,4,6],hmin:[0,2,3,4,7],phd:[0,2,3,4,6],ion:[0,1,2,4,5]};
const BRIGHT={aeo:2,dor:2,phr:2,hmin:5,phd:1,ion:0};
const dm=(sc,root,d)=>{const s=SC[sc]||SC.aeo,o=Math.floor(d/7),i=((d%7)+7)%7;return root+12*o+s[i]};
const CT=[0,2,4,7,9,11,14];            /* tonos del acorde en grados diatónicos */
const vel=c=>c==='X'?1:c==='x'?.72:c==='o'?.4:0;
/* notación de patrón: 16 fichas; '.'=silencio, número=grado, ' sube octava, , baja, ! acento, ~ ligadura (slide) */
const P=str=>{const a=str.trim().split(/\s+/).map(tok=>{if(tok==='.')return null;const m=/^(-?\d+)([',]*)([!~]*)$/.exec(tok);if(!m)return null;let o=0;for(const ch of m[2])o+=ch==="'"?1:-1;return{d:+m[1],o,a:m[3].indexOf('!')>=0,s:m[3].indexOf('~')>=0}});while(a.length<16)a.push(null);return a.slice(0,16)};
const D=s=>(s+'................').slice(0,16);

/* ---------- pistas (tempo/tonalidad del spec §6) ---------- */
const RAW={
 menu:{vol:1.7,bpm:100,root:36,scale:'aeo',wave:'square',cut:230,env:750,res:8,dec:.26,drive:1.3,swing:.12,bassV:.2,pump:.8,kickV:.6,int:1,
  bass:['0 . . 0\' . . 0 . 0 . . 0\' . 2~ 0 .','0 . 0 . . 0\' . 0 . 0 . . 4~ 3 . .'],prog:[[0,-2,2,-1],[0,-2,-4,-1]],
  arp:{pat:['0 . . 1 . . 2 . . 3 . . 2 . 1 .','0 . 1 . 2 . 3 . 4 . 3 . 2 . 1 .'],oct:3,wave:'triangle',cut:1900,dec:.12,v:.1,dbl:false},
  padCut:950,padV:.05,
  dr:{k:'x.......x.......',cl:'....x.......x...',oh:'..o...o...o...o.',ch:'....x.......x...'},
  lay:{pad:0,bass:0,arp:0,oh:0,k:1,ch:1,cl:2}},
 s1:{bpm:128,root:33,scale:'aeo',wave:'sawtooth',cut:300,env:2400,res:16,dec:.17,drive:2.4,swing:.05,pump:.5,int:1,
  bass:['0! 0 0\' 0 2~ 3 0 0\'! . 0 4~ 5 0 0\'! -1 0','0! . 0\' 0~ 2 . 0! 3\' . 0 0\' . 4!~ 3 2 0\''],prog:[[0,0,0,0],[0,0,-2,-1]],
  arp:{pat:['0 . 1 2 . 3 2 . 0 . 1 2 . 3 4 .','3 2 1 0 3 2 1 0 4 3 2 1 4 3 2 1'],oct:2,wave:'square',cut:2200,dec:.07,v:.075},
  dr:{k:'X...X...X...X...',cl:'....X.......X...',oh:'..x...x...x...x.',ch:'xo.oxo.oxo.oxo.o',pc:'.......x......x.'},perc:'rim',
  lay:{k:0,bass:0,oh:0,cl:1,ch:1,arp:1,crash:1,riser:1,fill:1,pc:2}},
 s2:{bpm:136,root:38,scale:'aeo',wave:'square',cut:250,env:3000,res:19,dec:.2,drive:4.2,swing:.1,pump:.5,int:1,
  bass:['0! 0\' . 0 0~ 1 . 0\'! 0 . 3~ 2 0 . 0\'! 5,','0! . 0 0\' . 0 -2~ 0 0! 0\' . 4 . 2~ 3 0'],prog:[[0,0,0,0],[0,0,3,-2]],
  arp:{pat:['0 0\' . 1 . 2 . 1\' 0 . 2 . 1 . 0\' .','0 . . 1 . . 2 . . 3 . . 2 . 1 .'],oct:2,wave:'sawtooth',cut:1700,dec:.08,v:.075},
  dr:{k:'X...X...X...X..x',cl:'....X.......X...',sn:'.......o.o....o.',oh:'..x...x...x...x.',ch:'xo.xxo.xxo.xxo.x',pc:'..x.......x..x..'},perc:'cow',
  lay:{k:0,bass:0,oh:0,cl:1,ch:1,arp:1,crash:1,riser:1,fill:1,pc:2,sn:2}},
 s3:{bpm:140,root:40,scale:'phr',wave:'sawtooth',cut:380,env:1800,res:11,dec:.12,drive:6,swing:0,pump:.55,int:1,snare:true,kHi:190,kDec:.1,
  bass:['0! 0 1~ 0 . 0 0\'! . 0 1 . 0 0\' 1! . 3','0! . 0 . 0\'! . 1 0 0! . 0 . -1~ 0 1 0\''],prog:[[0,0,0,0],[0,0,1,0]],
  arp:{pat:['0 . 0\' . 1 . 0 . 2 . 0\' . 1 . 0 1','0 1 0 2 0 1 0 3 0 1 0 2 0 1 3 2'],oct:2,wave:'square',cut:1500,dec:.06,v:.07},
  dr:{k:'X..xX...X..xX...',cl:'....X.......X...',oh:'......x.......x.',ch:'xoxoxo.oxoxoxo.o',pc:'..x..x....x..x..'},perc:'clang',
  lay:{k:0,bass:0,oh:0,cl:1,ch:1,pc:1,arp:2,crash:1,riser:1,fill:1}},
 s4:{bpm:150,root:42,scale:'aeo',wave:'sawtooth',cut:340,env:3400,res:15,dec:.15,drive:3,swing:.03,pump:.45,int:1,
  bass:['0! 0\' 0 0\' 2~ 0 0\'! 0 4 0\' 0 3~ 2 0\'! 0 -1','0! 0 0\' . 0~ 2 0\'! . 0 0 4\'~ 3\' 0 0\' 2! 0'],prog:[[0,0,0,0],[0,-2,-4,-1]],
  arp:{pat:['0 2 1 3 0 2 1 3 0 2 1 3 2 1 0 4','0\' . 2 . 1\' . 3 . 0\' . 2 . 4 3 2 1'],oct:2,wave:'square',cut:2600,dec:.07,v:.075},
  stab:'...x..x...x..x..',
  dr:{k:'X...X...X...X...',cl:'....X.......X...',oh:'..x...x...x...x.',ch:'xx.xxx.xxx.xxx.x',pc:'..........x..x..'},perc:'tom',
  lay:{k:0,bass:0,oh:0,cl:1,ch:1,arp:1,crash:1,riser:1,fill:1,pc:2,stab:2}},
 final:{bpm:160,root:42,scale:'hmin',wave:'sawtooth',cut:320,env:3600,res:17,dec:.13,drive:5,swing:0,pump:.45,int:2,
  bass:['0! 0 0\' 0 0! 0 0\' 0 0! 0 0\' 0 0! 0 6~ 0\'','0! 0\' 0 0\' 4! 0 3~ 2 0! 0\' 0 0\' 6!~ 0\' 5 4'],prog:[[0,0,0,0],[0,0,-2,-3]],
  arp:{pat:['0 1 2 3 0\' 3 2 1 0 1 2 3 1\' 3 2 1','0 . 0\' . 2 . 0\' 3 0 . 0\' . 2 1 0 .'],oct:2,wave:'square',cut:2400,dec:.06,v:.07},
  stab:'..x..x....x..x..',lead:[[7,9,9,8],[11,9,7,8]],leadOct:1,padCut:1300,padV:.04,
  dr:{k:'X...X...X...X...',cl:'....X.......X...',oh:'..x...x...x...x.',ch:'xx.xxx.xxx.xxx.x',pc:'..............xx'},perc:'tom',
  lay:{k:0,bass:0,oh:0,cl:0,ch:0,arp:1,crash:0,riser:0,fill:0,pc:1},
  phases:{2:{lay:{pad:0,stab:1},drive:1.15,cut:1.15},3:{lay:{pad:0,stab:0,lead:0,ch32:0},bpm:8,drive:1.35,cut:1.35}}},
 victory:{bpm:118,root:42,scale:'ion',wave:'square',cut:500,env:1200,res:7,dec:.2,drive:1.3,swing:.06,pump:.6,int:1,bassV:.22,
  bass:['0 . 0\' . 0 . 0\' 0 0 . 0\' . 0 . 0\' 0','0 . 0\' 0 . 0 0\' . 0 . 0\' 0 . 2~ 0\' .'],prog:[[0,-3,-2,-4],[-4,-3,0,0]],
  arp:{pat:['0 1 2 3 4 3 2 1 0 1 2 3 4 3 2 1','0 2 4 2 1 3 5 3 0 2 4 2 1 3 5 3'],oct:2,wave:'triangle',cut:3000,dec:.1,v:.085},
  bell:'x.......x.......',padCut:1600,padV:.045,
  dr:{k:'X...X...X...X...',cl:'....X.......X...',oh:'..x...x...x...x.',ch:'xo.oxo.oxo.oxo.o'},
  lay:{pad:0,bass:0,arp:0,bell:0,k:0,oh:0,cl:1,ch:1,crash:1,fill:1}}
};
/* JEFE: variante del último sector (misma tónica, escala más tensa, +6 BPM, más capas y más distorsión) */
const BOSSB={bass:['0! 0 0\'! 0 0 0\' 0! 6~ 0\' 0 0 0\'! 4 0 3~ 2','0! 0\' 1 0 0! 0\' 2~ 1 0! 0 0\' 0 4! 3 2~ 1'],
 arp:['0 1 2 3 0\' 3 2 1 0 1 2 3 1\' 3 2 1','0 . 0\' . 2 . 0\' 3 0 . 0\' . 2 1 0 .']};
const mkBoss=b=>{const phd=b.scale==='phr';return Object.assign({},b,{bpm:b.bpm+6,scale:phd?'phd':'hmin',cut:b.cut*1.1,env:b.env*1.2,res:b.res+2,dec:.14,
 drive:Math.min(8,b.drive*1.8),swing:b.swing*.5,int:2,pump:.45,bass:BOSSB.bass,prog:[[0,0,0,0],phd?[0,1,0,-1]:[0,0,-2,-3]],
 arp:Object.assign({},b.arp,{pat:BOSSB.arp,oct:2,dec:.06}),stab:'..x..x....x..x..',padCut:620,padV:.045,
 dr:{k:'X...X...X...X.x.',cl:'....X.......X...',oh:'..x...x...x...x.',ch:'xx.xxx.xxx.xxx.x',pc:b.perc==='clang'?'..x..x....x..x..':'............x.x.'},
 perc:b.perc||'tom',snare:!!b.snare,lay:{k:0,bass:0,oh:0,cl:0,ch:0,arp:1,crash:0,riser:0,fill:0,pc:1,stab:2,pad:2}})};
const build=r=>{const d=Object.assign({},r);d.bass=r.bass.map(s=>Array.isArray(s)?s:P(s));
 if(r.arp)d.arp=Object.assign({},r.arp,{pat:r.arp.pat.map(s=>Array.isArray(s)?s:P(s))});
 d.dr={};for(const k in r.dr)d.dr[k]=D(r.dr[k]);if(r.stab)d.stab=D(r.stab);if(r.bell)d.bell=D(r.bell);return d};
const TR={};for(const k in RAW)TR[k]=build(RAW[k]);
const BOSS={};['s1','s2','s3','s4'].forEach(s=>BOSS[s]=build(mkBoss(RAW[s])));
const TRACKS=['menu','s1','s2','s3','s4','boss','final','victory'];
const defFor=(name,sector)=>name==='boss'?BOSS[sector]||BOSS.s1:TR[name];

/* mezcla: bus de música y de efectos, y ajuste fino por efecto (medido con SND._offline: picos en solitario
   disparo≈0.05 · UI≈0.05-0.12 · explosión m≈0.3 · l≈0.5 · bomba/muerte de jefe≈0.6-0.7) */
const MUSV=.5,FXV=2;
const TRIM={shot:2.8,efire:4.5,hit:2.6,crit:1.4,graze:3.2,pickup:2.7,count:4.5,ui_hover:4.5,ui_click:2.1,ui_back:3,card:1.3,card_pick:2,radio:1.4,
 item:1.2,combo:1.5,od_ready:1.3,star:1.4,shield:1.3,stamp:1.3,ui_buy:1.1,ui_error:1.1,power:1.2,level_up:1.1,explode_s:1.5,explode_m:1.4,explode_l:1.15,
 hurt:1.2,laser_warn:1.35,laser:1.3,emp:1.35,thunder:1.2,alarm:1.15,phase:1.25,od:1.1,bomb:1,boss_die:1,card_legend:.6,gameover:1.2,revive:1.05};

/* curvas de forma de onda */
const mkCurve=f=>{const n=2048,c=new Float32Array(n);for(let i=0;i<n;i++){const x=i/(n-1)*2-1;c[i]=f(x)}return c};
const SHAPE=mkCurve(x=>Math.tanh(3.2*x)/Math.tanh(3.2));
const DIST=mkCurve(x=>Math.tanh(5*x)/Math.tanh(5));
const CLIP=mkCurve(x=>{const a=Math.abs(x),s=x<0?-1:1;return a<=.7?x:s*(.7+.22*Math.tanh((a-.7)/.22))});   /* techo absoluto ≈0.92 */

/* =====================================================================
   ENGINE: sintetizador completo sobre un BaseAudioContext
   ===================================================================== */
function Engine(ctx){
 const E={ctx,tracks:[],voices:[],od:false,key:{root:33,scale:'aeo'}};
 const sr=ctx.sampleRate,R=mulberry(20260924);
 const G=(v,dst)=>{const g=ctx.createGain();g.gain.value=v==null?1:v;if(dst)g.connect(dst);return g};
 const BQ=(type,f,q,dst)=>{const b=ctx.createBiquadFilter();b.type=type;b.frequency.value=f;if(q!=null)b.Q.value=q;if(dst)b.connect(dst);return b};
 const mkBuf=(sec,chs,fn)=>{const n=Math.floor(sr*sec),b=ctx.createBuffer(chs,n,sr);for(let c=0;c<chs;c++)fn(b.getChannelData(c),n,c);return b};
 /* buffers de ruido precalculados UNA vez por contexto */
 E.white=mkBuf(2,1,(d,n)=>{for(let i=0;i<n;i++)d[i]=R()*2-1});
 E.pink=mkBuf(2,1,(d,n)=>{let b0=0,b1=0,b2=0,b3=0,b4=0,b5=0,b6=0;for(let i=0;i<n;i++){const w=R()*2-1;b0=.99886*b0+w*.0555179;b1=.99332*b1+w*.0750759;b2=.969*b2+w*.153852;b3=.8665*b3+w*.3104856;b4=.55*b4+w*.5329522;b5=-.7616*b5-w*.016898;d[i]=(b0+b1+b2+b3+b4+b5+b6+w*.5362)*.11;b6=w*.115926}});
 E.brown=mkBuf(2,1,(d,n)=>{let l=0;for(let i=0;i<n;i++){l=(l+.02*(R()*2-1))/1.02;d[i]=l*3.5}});
 const IR=mkBuf(2.4,2,(d,n)=>{let y=0;const pre=Math.floor(sr*.012);for(let i=0;i<n;i++){if(i<pre){d[i]=0;continue}const k=(i-pre)/(n-pre),a=.85-.7*k;y+=a*((R()*2-1)-y);d[i]=y*Math.pow(1-k,3)}});
 /* cadena maestra */
 E.out=G(1);E.out.connect(ctx.destination);
 const clip=ctx.createWaveShaper();clip.curve=CLIP;clip.connect(E.out);
 const lim=ctx.createDynamicsCompressor();lim.threshold.value=-3;lim.knee.value=0;lim.ratio.value=20;lim.attack.value=.001;lim.release.value=.09;lim.connect(clip);
 const glue=ctx.createDynamicsCompressor();glue.threshold.value=-16;glue.knee.value=8;glue.ratio.value=3;glue.attack.value=.006;glue.release.value=.2;glue.connect(lim);
 E.master=G(.34,glue);
 E.duckG=G(1,E.master);E.mus=G(MUSV,E.duckG);E.fxb=G(FXV,E.master);
 E.revIn=G(1);const conv=ctx.createConvolver();conv.buffer=IR;E.revIn.connect(conv);conv.connect(G(.32,E.master));
 const now=()=>ctx.currentTime;
 const hold=(p,t,est)=>{if(p.cancelAndHoldAtTime){try{p.cancelAndHoldAtTime(t);return}catch(e){}}p.cancelScheduledValues(t);p.setValueAtTime(est,t)};
 E.setVol=(m,s)=>{const t=now();E.mus.gain.setTargetAtTime(MUSV*clamp(m,0,1),t,.05);E.fxb.gain.setTargetAtTime(FXV*clamp(s,0,1),t,.05)};
 E.setMute=b=>{E.out.gain.setTargetAtTime(b?0:1,now(),.03)};
 E.duckUntil=0;
 E.duck=(sec=1,depth=.35)=>{const t=now();if(t+sec<E.duckUntil-.05)return;E.duckUntil=t+sec;const p=E.duckG.gain;hold(p,t,p.value);p.setTargetAtTime(depth,t,.03);p.setTargetAtTime(1,t+sec,.18)};

 /* ---------- ayudantes de síntesis ---------- */
 const osc=(v,type,f,t,d,dst)=>{const o=ctx.createOscillator();o.type=type;o.frequency.setValueAtTime(f,t);o.connect(dst);o.start(t);o.stop(t+d);if(v)v.src.push(o);return o};
 const nz=(v,b,t,d,dst)=>{const s=ctx.createBufferSource();s.buffer=b;s.loop=true;s.connect(dst);s.start(t,R()*1.5);s.stop(t+d);if(v)v.src.push(s);return s};
 const eg=(t,a,pk,tau,dst,hd)=>{const g=G(0,dst),p=g.gain;p.setValueAtTime(0,t);p.linearRampToValueAtTime(pk,t+a);p.setTargetAtTime(0,t+a+(hd||0),tau);return g};
 const xr=(p,a,b,t,d)=>{p.setValueAtTime(a,t);p.exponentialRampToValueAtTime(b,t+d)};
 const shaper=(curve,dst)=>{const w=ctx.createWaveShaper();w.curve=curve;if(dst)w.connect(dst);return w};
 const panner=(pan,dst)=>{if(!pan||!ctx.createStereoPanner)return null;const p=ctx.createStereoPanner();p.pan.value=clamp(pan,-.95,.95);p.connect(dst);return p};
 /* ---------- voces de efectos (máx. 24, roba la más vieja) ---------- */
 const MAXV=24;
 const kill=(v,at)=>{try{v.g.gain.cancelScheduledValues(at);v.g.gain.setTargetAtTime(0,at,.012)}catch(e){}v.src.forEach(s=>{try{s.stop(at+.08)}catch(e){}});v.end=at};
 let trim=1;
 const V=(t,dur,vol,pan,rev)=>{vol*=trim;const n=now();E.voices=E.voices.filter(v=>v.end>n);while(E.voices.length>=MAXV)kill(E.voices.shift(),Math.max(n,t-.002));
  const g=G(vol);const p=panner(pan,E.fxb);g.connect(p||E.fxb);if(rev)g.connect(G(rev,E.revIn));const v={g,t0:t,end:t+dur,src:[]};E.voices.push(v);return v};
 const pan=o=>o.pan!=null?o.pan:o.x!=null?clamp(o.x/9,-.9,.9):0;
 const keyNote=(deg,lo)=>{const k=E.key;let m0=k.root;while(m0<lo)m0+=12;return dm(k.scale,m0,deg)};
 const bright=d=>d+(BRIGHT[E.key.scale]||0);
 const crackle=(v,t,d,n,dst,amp)=>{const g=G(0,dst),h=BQ('highpass',2600,.7,g);nz(v,E.white,t,d+.05,h);const ts=[];for(let i=0;i<n;i++)ts.push(t+R()*d);ts.sort((a,b)=>a-b);ts.forEach(tk=>{g.gain.setValueAtTime(amp*(.3+R()*.7),tk);g.gain.setTargetAtTime(0,tk+.001,.004+R()*.006)})};
 const boom=(v,t,P)=>{const lp=BQ('lowpass',P.lp0,.8,v.g);xr(lp.frequency,P.lp0,P.lp1,t,P.d*.8);nz(v,E.pink,t,P.d+.2,eg(t,.004,P.nv,P.d*.28,lp));
  const s=osc(v,'sine',P.s0,t,P.d+.2,eg(t,.003,P.sv,P.d*.3,v.g));s.frequency.exponentialRampToValueAtTime(P.s1,t+P.d*.6)};

 /* ---------- catálogo de efectos ---------- */
 const X={};
 X.shot=(t,o)=>{if(o.kind==='missile'||o.kind==='misil'){const v=V(t,.16,.04,pan(o)),b=BQ('bandpass',1400,2,v.g);xr(b.frequency,1400,3800,t,.12);nz(v,E.white,t,.15,eg(t,.01,1,.04,b));return}
  const v=V(t,.1,.042,pan(o)),j=1+(R()-.5)*.09,fl=BQ('lowpass',2900+R()*700,1.4,v.g);
  const s=osc(v,'square',1320*j,t,.08,eg(t,.002,1,.016,fl));s.frequency.exponentialRampToValueAtTime(690*j,t+.045)};
 X.efire=(t,o)=>{const v=V(t,.08,.022,pan(o)),s=osc(v,'triangle',760+R()*80,t,.08,eg(t,.002,1,.02,v.g));s.frequency.exponentialRampToValueAtTime(380,t+.06)};
 X.hit=(t,o)=>{const v=V(t,.12,.085,pan(o)),b=BQ('bandpass',2300+R()*700,1.4,v.g);nz(v,E.white,t,.06,eg(t,.001,1,.012,b));
  const s=osc(v,'triangle',440+R()*40,t,.09,eg(t,.001,.7,.02,v.g));s.frequency.exponentialRampToValueAtTime(150,t+.06)};
 X.crit=(t,o)=>{const v=V(t,1,.085,pan(o),.25),f=1150+R()*90;
  [[1,1,.3],[1.007,.7,.32],[2.76,.5,.16],[5.4,.28,.09],[8.93,.15,.05]].forEach(([r,a,tau])=>osc(v,'sine',f*r,t,1,eg(t,.001,a*.5,tau,v.g)));
  nz(v,E.white,t,.03,eg(t,.001,.8,.006,BQ('bandpass',3200,1,v.g)))};
 const BOOM={s:{d:.35,lp0:3200,lp1:260,s0:170,s1:48,sv:.55,nv:.6,vol:.16,rev:.06},m:{d:.8,lp0:2600,lp1:140,s0:130,s1:36,sv:.75,nv:.65,vol:.22,rev:.18},l:{d:1.6,lp0:2200,lp1:70,s0:95,s1:28,sv:.9,nv:.7,vol:.3,rev:.3}};
 ['s','m','l'].forEach(z=>{X['explode_'+z]=(t,o)=>{const Q=BOOM[z],v=V(t,Q.d+.4,Q.vol,pan(o),Q.rev);boom(v,t,Q);if(z!=='s')crackle(v,t+.02,Q.d*.8,z==='l'?16:7,v.g,.3)}});
 X.pickup=(t,o)=>{const c=Math.max(0,o.chain|0)%10,pn=PENT[E.key.scale]||PENT.aeo,f=mtof(keyNote(pn[c%5]+7*Math.floor(c/5),66));
  const v=V(t,.3,.06,pan(o),.1);osc(v,'sine',f,t,.3,eg(t,.002,.9,.07,v.g));osc(v,'triangle',f*2,t,.15,eg(t,.002,.25,.03,v.g))};
 X.graze=(t,o)=>{const v=V(t,.06,.04,pan(o));osc(v,'sine',3600+((o.count|0)%6)*140,t,.06,eg(t,.001,.8,.009,v.g));nz(v,E.white,t,.03,eg(t,.001,.5,.004,BQ('highpass',7000,.7,v.g)))};
 X.power=(t,o)=>{const v=V(t,.8,.1,0,.2),fl=BQ('lowpass',3800,2,v.g);[0,2,4,7].forEach((dg,i)=>{const tt=t+i*.055;osc(v,'square',mtof(keyNote(bright(dg),60)),tt,.35,eg(tt,.002,.5,.07,fl))});
  const s=osc(v,'sine',300,t,.5,eg(t,.02,.35,.12,v.g));s.frequency.exponentialRampToValueAtTime(1500,t+.35)};
 X.item=(t,o)=>{const v=V(t,.45,.075,pan(o),.15);[0,4].forEach((dg,i)=>{const tt=t+i*.06;osc(v,'triangle',mtof(keyNote(bright(dg),72)),tt,.4,eg(tt,.002,.8,.09,v.g))})};
 X.bomb=(t,o)=>{const v=V(t,2.6,.34,0,.35),ti=t+.12;
  const sw=G(0,v.g),hp=BQ('highpass',300,.7,sw);xr(hp.frequency,4000,300,t,.12);nz(v,E.pink,t,.13,hp);sw.gain.setValueAtTime(.001,t);sw.gain.exponentialRampToValueAtTime(.55,ti);sw.gain.setValueAtTime(0,ti+.004);
  const s=osc(v,'sine',70,ti,2,eg(ti,.005,1,.5,v.g));s.frequency.exponentialRampToValueAtTime(26,ti+1.4);
  const lp=BQ('lowpass',5000,.7,v.g);xr(lp.frequency,5000,180,ti,1.6);nz(v,E.brown,ti,2,eg(ti,.005,.9,.45,lp));nz(v,E.white,ti,.6,eg(ti,.002,.35,.12,lp));
  crackle(v,ti+.05,1.2,18,v.g,.25)};
 X.od=(t,o)=>{const v=V(t,1.7,.22,0,.25),td=t+.46;
  const bp=BQ('bandpass',400,4,v.g);xr(bp.frequency,400,5000,t,.45);const rg=G(0,bp);rg.gain.setValueAtTime(0,t);rg.gain.linearRampToValueAtTime(.4,t+.45);rg.gain.setValueAtTime(0,td);
  const s=osc(v,'sawtooth',180,t,.47,rg);s.frequency.exponentialRampToValueAtTime(1400,t+.45);nz(v,E.white,t,.47,rg);
  const sb=osc(v,'sine',120,td,1,eg(td,.003,1,.25,v.g));sb.frequency.exponentialRampToValueAtTime(38,td+.5);
  const lp=BQ('lowpass',3000,.7,v.g);xr(lp.frequency,3000,200,td,.6);nz(v,E.pink,td,.9,eg(td,.003,.6,.2,lp));
  const z=osc(v,'square',880,td,.3,eg(td,.002,.25,.06,v.g));z.frequency.exponentialRampToValueAtTime(110,td+.2)};
 X.alarm=(t,o)=>{const dur=2,v=V(t,dur+.2,.13,0,.12),bp=BQ('bandpass',1300,1.2,v.g),sh=shaper(DIST,bp),g=G(0,sh),p=g.gain;
  p.setValueAtTime(0,t);p.linearRampToValueAtTime(.55,t+.03);p.setValueAtTime(.55,t+dur-.15);p.linearRampToValueAtTime(0,t+dur);
  const a=osc(v,'square',740,t,dur,g),b=osc(v,'sawtooth',744,t,dur,g);
  for(let k=1;k<8;k++){const tk=t+k*.25,f=k%2?554:740,pf=k%2?740:554;[a,b].forEach((q,j)=>{q.frequency.setValueAtTime(pf*(j?1.005:1),tk);q.frequency.exponentialRampToValueAtTime(f*(j?1.005:1),tk+.05)})}
  const dr=osc(v,'sawtooth',46,t,dur,eg(t,.05,.35,.5,BQ('lowpass',300,1,v.g),dur-.4))};
 X.phase=(t,o)=>{const v=V(t,1.5,.24,0,.35);boom(v,t,{d:.5,lp0:2500,lp1:200,s0:110,s1:35,sv:.9,nv:.6});
  const c=osc(v,'sine',1600,t,1.2,eg(t,.005,.35,.25,v.g));c.frequency.exponentialRampToValueAtTime(200,t+.8);
  const m=osc(v,'sine',230,t,1.2,G(900,c.frequency))};
 X.boss_die=(t,o)=>{const v=V(t,4.8,.36,0,.5);
  nz(v,E.brown,t,4.6,eg(t,.06,1,1.1,BQ('lowpass',220,.7,v.g),.4));
  const s=osc(v,'sine',62,t,4,eg(t,.01,.8,1,v.g,.3));s.frequency.exponentialRampToValueAtTime(24,t+3);
  [0,.25,.5,.8,1.1,1.45,1.8,2.2,2.6].forEach((dt,i)=>{const tk=t+dt,p=panner(i%2?.5:-.5,v.g)||v.g,lp=BQ('lowpass',3000,.7,p);xr(lp.frequency,3000,300,tk,.4);nz(v,E.pink,tk,.6,eg(tk,.003,.55,.12,lp))});
  for(let i=0;i<20;i++){const tk=t+.5+R()*3,p=panner(R()*1.6-.8,v.g)||v.g;nz(v,E.white,tk,.05,eg(tk,.001,.25,.012,BQ('bandpass',1500+R()*3500,3,p)))}
  const tb=t+2.9;const b=osc(v,'sine',90,tb,1.8,eg(tb,.004,1,.6,v.g));b.frequency.exponentialRampToValueAtTime(25,tb+1.2);
  const lp=BQ('lowpass',4000,.7,v.g);xr(lp.frequency,4000,120,tb,1.4);nz(v,E.pink,tb,1.8,eg(tb,.004,.8,.4,lp))};
 X.hurt=(t,o)=>{const v=V(t,.4,.2,0,.1),lp=BQ('lowpass',1800,1,v.g),sh=shaper(DIST,lp);
  const s=osc(v,'sawtooth',260,t,.3,eg(t,.002,.7,.07,sh));s.frequency.exponentialRampToValueAtTime(70,t+.25);
  nz(v,E.white,t,.15,eg(t,.001,.6,.04,BQ('highpass',1000,.7,v.g)))};
 X.shield=(t,o)=>{const v=V(t,.7,.12,0,.2);[660,990].forEach(f=>{const s=osc(v,'triangle',f,t,.7,eg(t,.01,.5,.18,v.g));osc(v,'sine',18,t,.7,G(30,s.frequency))});
  osc(v,'sine',2640,t,.3,eg(t,.002,.25,.08,v.g))};
 X.emp=(t,o)=>{const v=V(t,1,.16,0,.15),bp=BQ('bandpass',900,.8,v.g);const c=osc(v,'square',1200,t,.7,eg(t,.003,.7,.2,bp));c.frequency.exponentialRampToValueAtTime(60,t+.5);
  osc(v,'square',47,t,.7,G(400,c.frequency));crackle(v,t,.8,14,v.g,.3)};
 X.thunder=(t,o)=>{const v=V(t,2.4,.26,o.pan!=null?o.pan:R()*.8-.4,.4),hp=BQ('highpass',1200,.7,v.g);
  nz(v,E.white,t,.2,eg(t,.001,1,.03,hp));nz(v,E.white,t+.05,.2,eg(t+.05,.001,.7,.04,hp));
  const g=G(0,BQ('lowpass',300,.7,v.g)),p=g.gain;p.setValueAtTime(0,t);p.linearRampToValueAtTime(.9,t+.06);for(let k=1;k<9;k++)p.setTargetAtTime((.9-.1*k)*(.5+R()*.5),t+.06+k*.18,.06);p.setTargetAtTime(0,t+1.7,.25);nz(v,E.brown,t,2.3,g)};
 X.laser_warn=(t,o)=>{const v=V(t,1.1,.08,pan(o)),g=G(.5,v.g);const tr=osc(v,'square',14,t,1.05,G(.5,g.gain));
  const s=osc(v,'sine',420,t,1.05,eg(t,.05,.8,.1,g,.8));s.frequency.linearRampToValueAtTime(1500,t+.95)};
 X.laser=(t,o)=>{const v=V(t,1,.12,pan(o),.2),lp=BQ('lowpass',5000,1,v.g);const c=osc(v,'sawtooth',2400,t,.9,eg(t,.005,.7,.15,lp,.35));c.frequency.exponentialRampToValueAtTime(180,t+.55);
  osc(v,'sine',310,t,.9,G(1200,c.frequency));nz(v,E.white,t,.6,eg(t,.005,.25,.2,BQ('bandpass',3000,1,v.g)))};
 X.ui_hover=(t,o)=>{const v=V(t,.05,.03,0);osc(v,'sine',1800,t,.05,eg(t,.001,1,.012,v.g))};
 X.ui_click=(t,o)=>{const v=V(t,.1,.05,0),lp=BQ('lowpass',4000,.7,v.g);osc(v,'square',1100,t,.05,eg(t,.001,.8,.018,lp));osc(v,'square',1650,t+.035,.05,eg(t+.035,.001,.6,.018,lp))};
 X.ui_back=(t,o)=>{const v=V(t,.14,.06,0),s=osc(v,'triangle',880,t,.12,eg(t,.002,1,.03,v.g));s.frequency.exponentialRampToValueAtTime(520,t+.08)};
 X.ui_buy=(t,o)=>{const v=V(t,.5,.08,0,.2);[1318.5,1760,2637].forEach((f,i)=>{const tt=t+i*.07;osc(v,'triangle',f,tt,.3,eg(tt,.002,.8,.1,v.g))});nz(v,E.white,t,.3,eg(t,.01,.2,.08,BQ('highpass',7000,.7,v.g)))};
 X.ui_error=(t,o)=>{const v=V(t,.3,.08,0),lp=BQ('lowpass',1200,.7,v.g);[0,.12].forEach(dt=>osc(v,'square',150,t+dt,.1,eg(t+dt,.003,.8,.03,lp,.05)))};
 X.card=(t,o)=>{const d=o.flip?.14:.24,v=V(t,d+.1,.09,pan(o)),bp=BQ('bandpass',700,1.3,v.g);xr(bp.frequency,700,3200,t,d);nz(v,E.white,t,d+.05,eg(t,d*.35,1,d*.3,bp));
  osc(v,'triangle',1400,t+d*.8,.05,eg(t+d*.8,.001,.5,.01,v.g))};
 X.card_pick=(t,o)=>{const v=V(t,.5,.09,0,.2),lp=BQ('lowpass',2600,1,v.g);[0,2,4].forEach(dg=>osc(v,'sawtooth',mtof(keyNote(bright(dg),60)),t,.45,eg(t,.004,.3,.12,lp)))};
 X.card_legend=(t,o)=>{const v=V(t,3,.2,0,.55),sum=G(1),out=G(1,v.g);
  [[800,450,1,8],[1150,800,.55,8],[2900,2830,.3,9]].forEach(([a,b,gn,q])=>{const f=BQ('bandpass',a,q,G(gn,out));f.frequency.setValueAtTime(a,t);f.frequency.linearRampToValueAtTime(b,t+1.6);sum.connect(f)});
  const ch=[0,2,4,7].map(dg=>keyNote(bright(dg),55)),g=eg(t,.35,1.4,.45,sum,1.45),lg=G(7);osc(v,'sine',5,t,3,lg);
  ch.forEach(m=>[-9,0,9].forEach(dt=>{const s=osc(v,'sawtooth',mtof(m),t,3,g);s.detune.value=dt;lg.connect(s.detune)}));
  const pn=PENT[E.key.scale]||PENT.aeo;for(let i=0;i<6;i++){const tt=t+.1+i*.12,f=mtof(keyNote(pn[(i*2)%5]+7*(i>2?1:0),78));osc(v,'sine',f,tt,.9,eg(tt,.002,.22,.3,v.g));osc(v,'sine',f*2.01,tt,.5,eg(tt,.002,.08,.12,v.g))}
  nz(v,E.white,t,2.5,eg(t,.5,.05,.5,BQ('highpass',8000,.7,v.g),.5))};
 X.stamp=(t,o)=>{const v=V(t,.4,.3,0,.12),s=osc(v,'sine',140,t,.35,eg(t,.002,1,.08,v.g));s.frequency.exponentialRampToValueAtTime(45,t+.15);
  nz(v,E.pink,t,.2,eg(t,.001,.6,.05,BQ('lowpass',1200,.7,v.g)));nz(v,E.white,t,.08,eg(t,.001,.4,.02,BQ('bandpass',2200,1,v.g)))};
 X.star=(t,o)=>{const n=o.n|0,v=V(t,.7,.09,0,.3),pn=PENT[E.key.scale]||PENT.aeo,f=mtof(keyNote(pn[(n*2)%5]+7*Math.floor(n*2/5),76));
  osc(v,'sine',f,t,.6,eg(t,.002,.8,.22,v.g));osc(v,'sine',f*2,t,.4,eg(t,.002,.3,.12,v.g));nz(v,E.white,t,.1,eg(t,.001,.2,.03,BQ('highpass',9000,.7,v.g)))};
 X.level_up=(t,o)=>{const v=V(t,1.1,.12,0,.25),lp=BQ('lowpass',3000,1.5,v.g);[0,2,4,7].forEach((dg,i)=>{const tt=t+i*.08,m=keyNote(bright(dg),60),last=i===3;
  osc(v,'square',mtof(m),tt,last?.9:.2,eg(tt,.003,.45,last?.25:.06,lp,last?.25:0));osc(v,'sawtooth',mtof(m)*1.003,tt,last?.9:.2,eg(tt,.003,.3,last?.25:.06,lp,last?.25:0))})};
 X.count=(t,o)=>{const v=V(t,.03,.025,0);osc(v,'square',2400,t,.03,eg(t,.001,1,.005,v.g))};
 X.combo=(t,o)=>{const mu=Math.max(2,o.mult|0),v=V(t,.6,.12,0,.2),lp=BQ('lowpass',1200,4,v.g);xr(lp.frequency,1200,4000+mu*300,t,.25);
  const base=Math.min(4,Math.floor(Math.log2(mu)));[0,2,4].forEach(dg=>{const m=keyNote(bright(dg+base),57);osc(v,'sawtooth',mtof(m),t,.5,eg(t,.004,.3,.14,lp));osc(v,'sawtooth',mtof(m)*1.006,t,.5,eg(t,.004,.2,.14,lp))})};
 X.radio=(t,o)=>{const v=V(t,.25,.05,0);nz(v,E.white,t,.13,eg(t,.002,1,.04,BQ('bandpass',1800,2,v.g)));osc(v,'sine',1000,t+.12,.08,eg(t+.12,.002,.6,.02,v.g))};
 X.od_ready=(t,o)=>{const v=V(t,.6,.06,0,.2);[0,4].forEach((dg,i)=>{const tt=t+i*.09,s=osc(v,'sine',mtof(keyNote(bright(dg),72)),tt,.45,eg(tt,.003,.8,.12,v.g));osc(v,'sine',9,tt,.45,G(12,s.frequency))})};
 X.revive=(t,o)=>{const v=V(t,1.2,.16,0,.35),g=G(0,v.g),p=g.gain;p.setValueAtTime(.001,t);p.exponentialRampToValueAtTime(.7,t+.5);p.setTargetAtTime(0,t+.5,.15);
  const bp=BQ('bandpass',500,2,g);xr(bp.frequency,500,5000,t,.5);nz(v,E.white,t,.8,bp);X.power(t+.45,o)};
 X.gameover=(t,o)=>{const v=V(t,2.4,.14,0,.4),lp=BQ('lowpass',1400,1,v.g);[7,5,3,0].forEach((dg,i)=>{const tt=t+i*.32,m=keyNote(dg,48),last=i===3;
  osc(v,'sawtooth',mtof(m),tt,last?1.6:.4,eg(tt,.01,.5,last?.5:.12,lp,last?.3:.12));osc(v,'sawtooth',mtof(m)*.995,tt,last?1.6:.4,eg(tt,.01,.35,last?.5:.12,lp,last?.3:.12))})};
 E.sfxNames=Object.keys(X);
 E.sfx=(name,o,t)=>{const f=X[name];if(!f)return false;o=o||{};trim=(TRIM[name]||1)*(o.vol!=null?clamp(+o.vol||0,0,2):1);try{f(t==null?now()+.005:t,o)}finally{trim=1}return true};

 /* =================== MÚSICA =================== */
 const nzS=(b,t,d,dst,off)=>{const s=ctx.createBufferSource();s.buffer=b;s.loop=true;s.connect(dst);s.start(t,off==null?R()*1.5:off);s.stop(t+d);return s};
 E.startTrack=(name,d,t0,fade,o)=>{o=o||{};
  const I={name,d,bpm:d.bpm,step:0,next:t0,t0,fade:Math.max(.02,fade),endAt:1e9,phase:1,int:o.intensity!=null?o.intensity:d.int,rng:mulberry(hash(name)),prev:null,lastF:mtof(d.root),sweep:1,cutM:1,lastOH:null,lay:Object.assign({},d.lay)};
  I.fad=G(0,E.mus);I.fadR=G(0,E.revIn);[I.fad,I.fadR].forEach(g=>{g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(1,t0+I.fade)});
  I.mix=G(d.vol||1,I.fad);I.rs=G(1,I.fadR);I.drums=G(1,I.mix);I.pump=G(1,I.mix);
  I.bo=ctx.createOscillator();I.bo.type=d.wave;I.bo.frequency.value=mtof(d.root);
  I.bf=BQ('lowpass',d.cut,d.res);I.bv=G(0);I.pre=G(d.drive*.16);I.sh=shaper(SHAPE);I.bout=G(d.bassV||.24,I.pump);
  I.bo.connect(I.bf);I.bf.connect(I.bv);I.bv.connect(I.pre);I.pre.connect(I.sh);I.sh.connect(I.bout);I.bo.start(t0);
  I.arpB=G(1,I.pump);I.dly=ctx.createDelay(2);I.dly.delayTime.value=3*60/d.bpm/4;I.fb=G(.36);I.dlf=BQ('lowpass',2600,.7);
  I.arpB.connect(I.dly);I.dly.connect(I.dlf);I.dlf.connect(I.fb);I.fb.connect(I.dly);I.dlf.connect(G(.4,I.pump));
  E.tracks.push(I);return I};
 E.stopTrack=(I,t,fade)=>{if(I.endAt<1e9)return;fade=Math.max(.05,fade);I.endAt=t+fade;
  [I.fad,I.fadR].forEach(g=>{const p=g.gain;hold(p,t,clamp((t-I.t0)/I.fade,0,1));p.setTargetAtTime(0,t,fade/4)});try{I.bo.stop(I.endAt+.3)}catch(e){}};
 E.setPhase=(I,p)=>{p=clamp(p|0,1,3);if(p===I.phase)return;I.phase=p;const d=I.d,t=Math.max(now(),I.next-.001);
  if(d.phases){for(let k=2;k<=p;k++){const ph=d.phases[k];if(!ph)continue;Object.assign(I.lay,ph.lay||{});if(ph.bpm)I.bpm=d.bpm+ph.bpm;if(ph.drive)I.pre.gain.setTargetAtTime(d.drive*.16*ph.drive,t,.1);if(ph.cut)I.cutM=ph.cut}}
  else{I.cutM=1+.15*(p-1);I.pre.gain.setTargetAtTime(d.drive*.16*(1+.2*(p-1)),t,.1);if(p>=3)I.lay.ch32=0}
  I.dly.delayTime.setValueAtTime(3*60/I.bpm/4,t)};
 E.pump=until=>{for(const I of E.tracks){let g=0;while(I.next<until&&I.next<I.endAt&&g++<256){try{sched(I,I.step,I.next)}catch(e){}I.step++;I.next+=60/I.bpm/4}}};
 E.resync=t=>{for(const I of E.tracks){if(I.next<t-.15){const sd=60/I.bpm/4,k=Math.ceil((t-I.next)/sd);I.step+=k;I.next+=k*sd}}};
 E.gc=()=>{const n=now();E.tracks=E.tracks.filter(I=>{if(n>I.endAt+.8){try{I.fad.disconnect();I.fadR.disconnect()}catch(e){}return false}return true})};

 /* instrumentos */
 const nl=(I,m)=>{if(E.noteLog)E.noteLog.push(m)};
 function kick(I,t,v){const d=I.d,g=G(0,I.drums),o=ctx.createOscillator();o.type='sine';
  o.frequency.setValueAtTime(d.kHi||170,t);o.frequency.exponentialRampToValueAtTime(58,t+.055);o.frequency.exponentialRampToValueAtTime(d.kLo||44,t+.28);
  const p=g.gain;p.setValueAtTime(0,t);p.linearRampToValueAtTime(v*(d.kickV||.95),t+.002);p.setTargetAtTime(0,t+.07,d.kDec||.12);o.connect(g);o.start(t);o.stop(t+.7);
  const c=G(0,I.drums);nzS(E.white,t,.03,BQ('highpass',2200,.7,c));c.gain.setValueAtTime(v*.25,t);c.gain.setTargetAtTime(0,t+.001,.006);
  if(d.pump){const q=I.pump.gain;q.setValueAtTime(d.pump,t);q.setTargetAtTime(1,t+.015,.08)}}
 function hat(I,t,v,open){const g=G(0,I.drums);nzS(E.white,t,open?.7:.12,BQ('highpass',open?6800:8200,.8,g));
  const p=g.gain;p.setValueAtTime(v*(open?.2:.14),t);p.setTargetAtTime(0,t+.002,open?.085:.017);
  if(open)I.lastOH={g,t};else if(I.lastOH&&I.lastOH.t<t){I.lastOH.g.gain.setTargetAtTime(0,t,.006);I.lastOH=null}}
 function clap(I,t,v){const g=G(0,I.drums);g.connect(G(.35,I.rs));nzS(E.white,t,.4,BQ('bandpass',1150,1.3,g));const p=g.gain,a=v*.6;
  for(let k=0;k<3;k++){const tk=t+k*.0105;p.setValueAtTime(a,tk);p.setTargetAtTime(0,tk+.001,.0035)}p.setValueAtTime(a*.85,t+.032);p.setTargetAtTime(0,t+.033,.075)}
 function snare(I,t,v){const g=G(1,I.drums);g.connect(G(.25,I.rs));const og=G(0,g),o=ctx.createOscillator();o.type='triangle';
  o.frequency.setValueAtTime(215,t);o.frequency.exponentialRampToValueAtTime(165,t+.06);o.connect(og);og.gain.setValueAtTime(v*.5,t);og.gain.setTargetAtTime(0,t+.002,.04);o.start(t);o.stop(t+.3);
  const ng=G(0,g);nzS(E.white,t,.35,BQ('highpass',1400,.7,ng));ng.gain.setValueAtTime(v*.45,t);ng.gain.setTargetAtTime(0,t+.002,.055)}
 function perc(I,t,v,type){const g=G(0,I.drums),p=g.gain;
  if(type==='tom'){const o=ctx.createOscillator();o.type='sine';o.frequency.setValueAtTime(200,t);o.frequency.exponentialRampToValueAtTime(95,t+.18);o.connect(g);o.start(t);o.stop(t+.4);p.setValueAtTime(v*.5,t);p.setTargetAtTime(0,t+.01,.09);return}
  if(type==='rim'){const b=BQ('bandpass',1700,3,g);const o=ctx.createOscillator();o.type='triangle';o.frequency.value=1700;o.connect(b);o.start(t);o.stop(t+.06);nzS(E.white,t,.03,b);p.setValueAtTime(v*.28,t);p.setTargetAtTime(0,t+.001,.012);return}
  const fr=type==='cow'?[545,815]:[311,457,733,1063],b=BQ('bandpass',type==='cow'?800:1800,type==='cow'?2:2.5,g);if(type==='clang')g.connect(G(.3,I.rs));
  fr.forEach(f=>{const o=ctx.createOscillator();o.type='square';o.frequency.value=f;o.connect(b);o.start(t);o.stop(t+.3)});p.setValueAtTime(v*(type==='cow'?.16:.14),t);p.setTargetAtTime(0,t+.003,type==='cow'?.06:.07)}
 function crash(I,t,v){const g=G(0,I.drums);g.connect(G(.3,I.rs));nzS(E.white,t,2.5,BQ('highpass',4200,.7,g));g.gain.setValueAtTime(.16*v,t);g.gain.setTargetAtTime(0,t+.005,.5)}
 function riser(I,t,dur){const g=G(0,I.mix);g.connect(G(.3,I.rs));const b=BQ('bandpass',500,4,g);xr(b.frequency,500,6500,t,dur);nzS(E.white,t,dur+.02,b);
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.09,t+dur-.01);g.gain.setValueAtTime(0,t+dur)}
 function acid(I,t,m,acc,slIn,slOut,sd){nl(I,m);const d=I.d,f=mtof(m),o=I.bo.frequency,fl=I.bf.frequency,g=I.bv.gain,od=E.od;
  if(slIn){o.setValueAtTime(I.lastF,t);o.exponentialRampToValueAtTime(f,t+Math.min(.07,sd*.7));if(acc)g.setTargetAtTime(1,t,.004)}
  else{o.setValueAtTime(f,t);const base=Math.min(7000,d.cut*I.sweep*I.cutM*(od?2.1:1)),peak=Math.min(13000,base+d.env*(acc?1.5:1)*(od?1.3:1));
   fl.setValueAtTime(peak,t);fl.setTargetAtTime(base,t+.003,acc?d.dec*.6:d.dec);g.setTargetAtTime(acc?1:.62,t,.002)}
  if(!slOut)g.setTargetAtTime(0,t+sd*.62,.012);I.lastF=f}
 function arp(I,t,m,acc,sd,vm){nl(I,m);const A=I.d.arp,f=mtof(m),g=G(0,I.arpB),fl=BQ('lowpass',A.cut,A.q||4,g),cut=A.cut*(E.od?1.6:1)*(acc?1.35:1);
  const o1=ctx.createOscillator();o1.type=A.wave||'square';o1.frequency.value=f;o1.connect(fl);
  const o2=ctx.createOscillator();o2.type='sawtooth';o2.frequency.value=f;o2.detune.value=7;o2.connect(fl);
  fl.frequency.setValueAtTime(cut*2.6,t);fl.frequency.setTargetAtTime(cut,t,.05);
  const p=g.gain;p.setValueAtTime(0,t);p.linearRampToValueAtTime((A.v||.08)*(vm||1)*(acc?1.2:.85),t+.003);p.setTargetAtTime(0,t+.01,A.dec||.07);
  o1.start(t);o2.start(t);o1.stop(t+.5);o2.stop(t+.5)}
 function chord(d,c,lo,hi){return[0,2,4].map(k=>{let m=dm(d.scale,d.root,c+k);while(m<lo)m+=12;while(m>=hi)m-=12;return m}).sort((a,b)=>a-b)}
 function pad(I,t,notes,dur){notes.forEach(m=>nl(I,m));const d=I.d,g=G(0,I.pump),fl=BQ('lowpass',d.padCut||1100,.6,g);g.connect(G(.5,I.rs));
  notes.forEach(m=>[-8,8].forEach(dt=>{const o=ctx.createOscillator();o.type='sawtooth';o.frequency.value=mtof(m);o.detune.value=dt;o.connect(fl);o.start(t);o.stop(t+dur+1.4)}));
  const a=Math.min(.7,dur*.3),pv=d.padV||.045,p=g.gain;p.setValueAtTime(0,t);p.linearRampToValueAtTime(pv,t+a);p.setValueAtTime(pv,t+dur-.05);p.setTargetAtTime(0,t+dur-.05,.35)}
 function stab(I,t,notes,v){notes.forEach(m=>nl(I,m));const g=G(0,I.pump),fl=BQ('lowpass',3200,2,g);g.connect(G(.25,I.rs));xr(fl.frequency,3200*(E.od?1.4:1),700,t,.15);
  notes.concat([notes[0]+12]).forEach(m=>{const o=ctx.createOscillator();o.type='sawtooth';o.frequency.value=mtof(m);o.connect(fl);o.start(t);o.stop(t+.5)});
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.05*v,t+.003);g.gain.setTargetAtTime(0,t+.01,.09)}
 function lead(I,t,m,dur){nl(I,m);const g=G(0,I.pump),fl=BQ('lowpass',2800,2,g);g.connect(G(.3,I.rs));g.connect(I.dly);
  const l=ctx.createOscillator();l.frequency.value=5.5;const lg=G(9);l.connect(lg);l.start(t);l.stop(t+dur+.6);
  [['square',0],['sawtooth',5]].forEach(([w,dt])=>{const o=ctx.createOscillator();o.type=w;o.frequency.value=mtof(m);o.detune.value=dt;lg.connect(o.detune);o.connect(fl);o.start(t);o.stop(t+dur+.6)});
  const p=g.gain;p.setValueAtTime(0,t);p.linearRampToValueAtTime(.07,t+.03);p.setValueAtTime(.07,t+dur-.08);p.setTargetAtTime(0,t+dur-.08,.08)}
 function bell(I,t,m){nl(I,m);const g=G(1,I.mix);g.connect(G(.4,I.rs));const f=mtof(m);[[1,.07,.35],[2,.03,.2],[3.01,.015,.1]].forEach(([r,a,tau])=>{const o=ctx.createOscillator();o.type='sine';o.frequency.value=f*r;const e=G(0,g);o.connect(e);e.gain.setValueAtTime(0,t);e.gain.linearRampToValueAtTime(a,t+.002);e.gain.setTargetAtTime(0,t+.002,tau);o.start(t);o.stop(t+1.4)})}

 /* un paso de 1/16 del secuenciador */
 function sched(I,s,t){
  const d=I.d,sd=60/I.bpm/4,bar=s>>4,st=s&15,ph=bar>>3,pv=ph&1,ib=bar&7,lay=I.lay,it=I.int+(E.od?.5:0);
  const L=k=>lay[k]!=null&&lay[k]<=it;
  const tt=t+((st&1)?d.swing*sd:0),c=d.prog[pv][bar&3],fill=ib===7&&L('fill');
  I.sweep=.62+.8*tri(s/256);
  const kc=d.dr.k[st];if(L('k')&&kc!=='.'&&!(fill&&st>12))kick(I,t,vel(kc));
  if(fill&&st>=12)snare(I,tt,.3+.17*(st-12));
  else{const cc=d.dr.cl[st];if(L('cl')&&cc!=='.')(d.snare?snare:clap)(I,tt,vel(cc))}
  if(d.dr.sn&&L('sn')&&d.dr.sn[st]!=='.')snare(I,tt,vel(d.dr.sn[st]));
  const dbl=E.od||L('ch32');
  if(L('ch')||dbl){const hc=d.dr.ch[st];if(hc!=='.'||dbl){hat(I,tt,hc!=='.'?vel(hc):.45,0);if(dbl)hat(I,tt+sd/2,.4,0)}}
  const oc=d.dr.oh[st];if(L('oh')&&oc!=='.')hat(I,tt,vel(oc),1);
  if(d.dr.pc&&L('pc')&&d.dr.pc[st]!=='.')perc(I,tt,vel(d.dr.pc[st]),d.perc);
  if(st===0&&ib===0&&bar>0&&L('crash'))crash(I,t,1);
  if(st===0&&ib===7&&L('riser'))riser(I,t,16*sd);
  if(L('bass')){const tok=d.bass[pv%d.bass.length][st];
   if(tok){acid(I,tt,dm(d.scale,d.root,tok.d+c)+12*tok.o,tok.a,!!(I.prev&&I.prev.s),tok.s,sd);I.prev=tok}
   else{I.prev=null;if(I.int>=2&&(st&1)&&I.rng()<.12)acid(I,tt,dm(d.scale,d.root,c)+12,false,false,false,sd)}}
  if(d.arp&&L('arp')){const ap=d.arp.pat[(ph>>1)%d.arp.pat.length][st];
   if(ap){const m=dm(d.scale,d.root,c+CT[ap.d%CT.length])+12*(d.arp.oct+ap.o);arp(I,tt,m,ap.a||st%4===0,sd);if(I.int>=2&&d.arp.dbl!==false&&!(st&1))arp(I,tt,m+12,false,sd,.45)}}
  if(L('pad')&&st===0)pad(I,t,chord(d,c,55,67),16*sd);
  if(L('stab')&&d.stab&&d.stab[st]!=='.')stab(I,tt,chord(d,c,60,72),vel(d.stab[st]));
  if(L('lead')&&d.lead&&st===0)lead(I,t,dm(d.scale,d.root,d.lead[pv][bar&3])+12*(d.leadOct||1),16*sd);
  if(L('bell')&&d.bell&&d.bell[st]!=='.'){const ch=chord(d,c,72,84);bell(I,tt,ch[(bar+(st>>3))%3])}
 }
 return E;
}

/* =====================================================================
   ANÁLISIS (pruebas): pico, RMS, bandas, cruces por cero y croma
   ===================================================================== */
const PCN=['Do','Do#','Re','Re#','Mi','Fa','Fa#','Sol','Sol#','La','La#','Si'];
function analyze(buf,chroma){const chs=[];for(let c=0;c<buf.numberOfChannels;c++)chs.push(buf.getChannelData(c));const n=buf.length,sr=buf.sampleRate,nc=chs.length;
 let pk=0,ss=0,lo=0,hi=0,zc=0,y=0,hp=0,px=0,prev=0,sil=0,win=0,ws=0;const al=1-Math.exp(-2*Math.PI*150/sr),ah=Math.exp(-2*Math.PI*4000/sr),mono=new Float32Array(n);
 for(let i=0;i<n;i++){let x=0;for(let c=0;c<nc;c++){const v=chs[c][i];x+=v;ss+=v*v;const a=v<0?-v:v;if(a>pk)pk=a}x/=nc;mono[i]=x;
  y+=al*(x-y);lo+=y*y;hp=ah*(hp+x-px);px=x;hi+=hp*hp;if((x>=0)!==(prev>=0))zc++;prev=x;ws+=x*x;if(++win===2048){if(Math.sqrt(ws/2048)<.001)sil++;win=0;ws=0}}
 const tot=ss/nc+1e-12,r={peak:+pk.toFixed(4),rms:+Math.sqrt(ss/(n*nc)).toFixed(4),rmsDb:+(20*Math.log10(Math.sqrt(ss/(n*nc))+1e-9)).toFixed(1),
  low:+(lo/tot).toFixed(3),high:+(hi/tot).toFixed(3),zcr:+(zc/n*sr).toFixed(0),silent:+(sil/Math.max(1,Math.floor(n/2048))).toFixed(2)};
 if(chroma){const e=new Array(12).fill(0);for(let m=36;m<84;m++){const f=mtof(m),k=2*Math.cos(2*Math.PI*f/sr);let s1=0,s2=0;for(let i=0;i<n;i+=1){const s0=mono[i]+k*s1-s2;s2=s1;s1=s0}e[m%12]+=Math.sqrt(Math.max(0,s1*s1+s2*s2-k*s1*s2))/n}
  const mx=Math.max(...e);r.chroma=e.map(v=>+(v/mx).toFixed(2));r.top=e.map((v,i)=>[v,i]).sort((a,b)=>b[0]-a[0]).slice(0,4).map(x=>PCN[x[1]]).join(' ')}
 return r}

/* =====================================================================
   ESTADO EN VIVO: contexto compartido, ajustes, secuenciador en tiempo real
   ===================================================================== */
let E=null,timer=0,pending=null,cur=null,curName=null,lastSector='s1',intensity=null,od=false,lastMute=null,lastSet='',weSusp=false,setTick=0;
const LIM={shot:.1,efire:.25,hit:.045,crit:.07,graze:.05,pickup:.035,explode_s:.045,explode_m:.08,explode_l:.15,ui_hover:.04,count:.03,card:.05,star:.08,
 alarm:1.5,boss_die:1,bomb:.3,od:.5,hurt:.25,laser_warn:.25,laser:.15,thunder:.3,emp:.3,phase:.5,power:.15,item:.08,combo:.2,radio:.4,card_pick:.2,card_legend:.8,level_up:.5,stamp:.1,ui_click:.03,ui_back:.05,ui_buy:.08,ui_error:.1,revive:.5,gameover:1,od_ready:.5,shield:.15};
const lastT={};
const muted=()=>!!(_FX&&_FX.muted);
const S=()=>{if(!_SAVE.settings||typeof _SAVE.settings!=='object')_SAVE.settings={music:1,sfx:1,voice:1,shake:1};return _SAVE.settings};
const num=v=>v===false?0:v===true||v==null?1:clamp(+v||0,0,1);
function applySettings(){const s=S(),k=num(s.music)+'|'+num(s.sfx)+'|'+num(s.voice);if(k===lastSet)return;lastSet=k;if(E)E.setVol(num(s.music),num(s.sfx));if(!num(s.voice))try{W.speechSynthesis&&W.speechSynthesis.cancel()}catch(e){}}
function getCtx(){try{if(_FX&&_FX.audio)return _FX.audio()}catch(e){}try{if(!getCtx.own){const A=W.AudioContext||W.webkitAudioContext;if(A)getCtx.own=new A()}if(getCtx.own&&getCtx.own.state==='suspended')getCtx.own.resume()}catch(e){}return getCtx.own||null}
function tick(){if(!E)return;try{const ctx=E.ctx,m=muted();if(m!==lastMute){lastMute=m;E.setMute(m);if(m)try{W.speechSynthesis&&W.speechSynthesis.cancel()}catch(e){}}
 if(++setTick>=20){setTick=0;applySettings()}
 if(ctx.state!=='running')return;E.resync(ctx.currentTime);E.pump(ctx.currentTime+.12);E.gc();sayQueue()}catch(e){}}
function boot(ctx){if(E||!ctx)return;try{E=Engine(ctx)}catch(e){E=null;return}lastMute=null;lastSet='';applySettings();tick();timer=setInterval(tick,25);
 if(pending){const p=pending;pending=null;MUSapi.play(p.name,p.o)}}
function unlock(){if(E){rmUnlock();return}const ctx=getCtx();if(!ctx)return;try{if(ctx.state==='suspended')ctx.resume()}catch(e){}boot(ctx);if(E)rmUnlock()}
const UEV=['pointerdown','keydown','touchstart','mousedown'];
function rmUnlock(){UEV.forEach(ev=>W.removeEventListener(ev,unlock,true))}
UEV.forEach(ev=>W.addEventListener(ev,unlock,{capture:true,passive:true}));
document.addEventListener('visibilitychange',()=>{try{if(!E)return;const ctx=E.ctx;if(document.hidden){if(ctx.state==='running'){weSusp=true;ctx.suspend()}try{W.speechSynthesis&&W.speechSynthesis.cancel()}catch(e){}}
 else if(weSusp){weSusp=false;ctx.resume()}}catch(e){}});

/* ---------- MUS ---------- */
const sectorOf=n=>{n=+n;return n>=1&&n<=4?'s'+n:null};
const MUSapi={
 play(name,o){o=o||{};if(TRACKS.indexOf(name)<0)return false;if(/^s[1-4]$/.test(name))lastSector=name;
  if(!E){pending={name,o};return true}
  const ctx=E.ctx,t=ctx.currentTime+.05;
  if(cur&&curName===name&&cur.endAt>=1e9&&!o.restart){if(o.intensity!=null)MUSapi.intensity(o.intensity);return true}
  const fade=o.fade!=null?o.fade:cur?1.5:.6;if(cur)E.stopTrack(cur,ctx.currentTime,fade);
  const d=defFor(name,lastSector);cur=E.startTrack(name,d,t,fade,{intensity:o.intensity!=null?clamp(+o.intensity,0,2):d.int});curName=name;intensity=cur.int;
  E.key={root:d.root,scale:d.scale};E.od=od;if(ctx.state==='running')E.pump(ctx.currentTime+.12);return true},
 stop(fade){pending=null;if(E&&cur){E.stopTrack(cur,E.ctx.currentTime,fade==null?1:+fade||.05)}cur=null;curName=null;return true},
 intensity(v){if(v==null)return intensity;intensity=clamp(+v||0,0,2);if(cur)cur.int=intensity;return intensity},
 duck(sec,depth){if(E)E.duck(sec==null?1:+sec,depth==null?.35:depth)},
 od(on){od=!!on;if(E)E.od=od},
 phase(p){if(E&&cur){const n=Math.max(cur.phase+1,p|0);E.setPhase(cur,n)}},
 current(){return curName},
 tracks:TRACKS.slice()
};
Object.assign(_MUS,MUSapi);

/* ---------- LOCUTOR ---------- */
const SP={last:-1e9,pick:null,loaded:false,queue:null,lastTxt:{}};
function loadVoices(){try{const vs=W.speechSynthesis.getVoices()||[];SP.loaded=vs.length>0;const es=vs.filter(v=>/^es[-_]ES/i.test(v.lang)),male=/pablo|jorge|diego|enrique|carlos|alvaro|álvaro|juan|raul|raúl|male|hombre/i;SP.pick=es.find(v=>male.test(v.name))||es[0]||vs.find(v=>/^es/i.test(v.lang))||null}catch(e){SP.pick=null}}
try{if(W.speechSynthesis){loadVoices();if(W.speechSynthesis.addEventListener)W.speechSynthesis.addEventListener('voiceschanged',loadVoices);else W.speechSynthesis.onvoiceschanged=loadVoices}}catch(e){}
function say(text,o){o=o||{};try{if(!text||muted()||!num(S().voice))return false;const ss=W.speechSynthesis;if(!ss||typeof W.SpeechSynthesisUtterance!=='function')return false;
 if(!SP.pick)loadVoices();if(!SP.pick)return false;const nw=performance.now();
 if(nw-SP.last<2500||ss.speaking||ss.pending){if(o.queue)SP.queue={text,until:nw+4000};return false}
 const u=new W.SpeechSynthesisUtterance(text);u.voice=SP.pick;u.lang=SP.pick.lang;u.pitch=.7;u.rate=1.1;u.volume=clamp(num(S().voice),0,1);
 SP.last=nw;const est=.6+text.length*.065;MUSapi.duck(est,.45);u.onend=()=>{SP.last=Math.max(SP.last,performance.now()-1500)};ss.speak(u);return true}catch(e){return false}}
function sayQueue(){const q=SP.queue;if(!q)return;const nw=performance.now();if(nw>q.until){SP.queue=null;return}if(say(q.text))SP.queue=null}
const LINES={boss_warn:['¡Alerta! Jefe detectado','¡Alerta! Jefe detectado. Firma térmica enorme','¡Alerta! Contacto hostil a las doce'],
 od_start:['¡Sobrecarga!','¡Sobrecarga activada!','¡Sobrecarga! A tope'],c4:['Combo brutal','¡Combo brutal!'],c5:['¡Imparable!','¡Imparable, piloto!'],c8:['¡Leyenda!','¡Eres una leyenda!'],
 boss_die:['Jefe abatido','Jefe abatido. Buen trabajo','Jefe abatido. Chatarra de la buena'],sector_clear:['Sector despejado','Sector despejado. Seguimos','Sector despejado. Buen vuelo'],
 gameover:['Misión fallida','Misión fallida. Volveremos'],victory:['Nova ha caído','Nova ha caído. Buen vuelo, piloto']};
const line=k=>{const a=LINES[k]||[k],l=SP.lastTxt[k];let i=Math.floor(Math.random()*a.length);if(a.length>1&&a[i]===l)i=(i+1)%a.length;SP.lastTxt[k]=a[i];return a[i]};

/* ---------- SND ---------- */
function play(name,o){try{if(!E||muted()||!num(S().sfx))return false;o=o||{};const ctx=E.ctx;if(ctx.state!=='running')return false;const n=ctx.currentTime,lim=LIM[name];
 if(lim&&lastT[name]!=null&&n-lastT[name]<lim&&n>=lastT[name])return false;lastT[name]=n;return E.sfx(name,o,n+.005+(+o.at||0))}catch(e){return false}}
async function offline(kind,name,secs,o){o=o||{};const OAC=W.OfflineAudioContext||W.webkitOfflineAudioContext;if(!OAC)throw new Error('sin OfflineAudioContext');
 secs=+secs||1;const ctx=new OAC(2,Math.ceil(44100*secs),44100),e=Engine(ctx);let d=null;
 if(kind==='music'||kind==='mix'){d=defFor(name,o.sector||'s1');e.key={root:d.root,scale:d.scale};e.noteLog=[];
  const I=e.startTrack(name,d,.02,.02,{intensity:o.intensity});if(o.od)e.od=true;if(o.phase)e.setPhase(I,o.phase);if(o.startBar)I.step=o.startBar*16;e.pump(secs)}
 if(kind==='mix'){/* prueba de estrés: todo a la vez sobre la música */
  for(let t=.05;t<secs;t+=.1)e.sfx('shot',{x:Math.sin(t*3)*6},t);for(let t=.1;t<secs;t+=.07)e.sfx(t%.5<.25?'hit':'crit',{x:1},t);
  ['bomb','alarm','boss_die','od','card_legend','thunder','phase'].forEach((n,i)=>e.sfx(n,{},.2+i*.35));for(let i=0;i<14;i++)e.sfx('explode_'+'sml'[i%3],{x:i-7},.1+i*.21)}
 else if(kind!=='music'){if(!e.sfx(name,o,.02))throw new Error('efecto desconocido '+name)}
 const buf=await ctx.startRendering(),r=analyze(buf,kind==='music'&&o.chroma!==false);
 if(d&&e.noteLog){const sc=SC[d.scale]||SC.aeo,pcs=[...new Set(e.noteLog.map(m=>((m%12)+12)%12))].sort((x,y)=>x-y);
  r.notes=e.noteLog.length;r.scale=PCN[d.root%12]+' '+d.scale+' '+d.bpm+'bpm';r.pcs=pcs.map(x=>PCN[x]).join(' ');r.outOfScale=pcs.filter(x=>sc.indexOf(((x-d.root)%12+12)%12)<0).map(x=>PCN[x])}
 return r}
const SNDapi={
 play,say,
 settings(o){const s=S();if(o&&typeof o==='object'){['music','sfx','voice'].forEach(k=>{if(k in o)s[k]=o[k]});try{_SAVE.persist&&_SAVE.persist()}catch(e){}lastSet='';}applySettings();return{music:s.music,sfx:s.sfx,voice:s.voice}},
 names:()=>E?E.sfxNames.slice():['shot','hit','crit','explode_s','explode_m','explode_l','pickup','graze','power','bomb','od','alarm','phase','boss_die','hurt','shield','emp','thunder','laser_warn','laser','ui_hover','ui_click','ui_back','ui_buy','ui_error','card','card_legend','stamp','star','level_up','count','combo','radio','od_ready','revive','gameover','efire','item','card_pick'],
 state:()=>({ready:!!E,ctx:E?E.ctx.state:'none',time:E?+E.ctx.currentTime.toFixed(2):0,track:curName,intensity,od,phase:cur?cur.phase:0,tracks:E?E.tracks.length:0,voices:E?E.voices.length:0,muted:muted(),out:E?+E.out.gain.value.toFixed(2):0,pending:pending&&pending.name,voice:SP.pick?SP.pick.lang:null,settings:SNDapi.settings()}),
 unlock,
 _offline:offline,
 _analyze:analyze
};
Object.assign(_SND,SNDapi);
if(_N){try{_N.audioTest=(kind,name,secs,o)=>offline(kind,name,secs,o);_N.audio=()=>SNDapi.state()}catch(e){}}

/* =====================================================================
   ENGANCHES DEL BUS
   ===================================================================== */
const on=(ev,fn)=>{try{_BUS.on(ev,d=>{try{fn(d||{})}catch(e){}})}catch(e){}};
const ex=d=>{const e=d.e||{};const v=d.x!=null?d.x:e.x!=null?e.x:e.p&&e.p.x!=null?e.p.x:e.pos&&e.pos.x!=null?e.pos.x:e.mesh&&e.mesh.position?e.mesh.position.x:e.obj&&e.obj.position?e.obj.position.x:null;return typeof v==='number'?v:null};
const BIG={portador:1,centinela:1,escudero:1,caza:1,torreta:1,saltador:1};
const sizeOf=s=>{if(typeof s==='number')return s<1.2?'s':s<2.6?'m':'l';s=String(s||'s').toLowerCase();return s[0]==='l'||s==='g'||s==='big'?'l':s[0]==='m'?'m':'s'};
let lastMult=1,lastPow=0,bossTok=0;
on('shot',d=>play(d.kind==='laser'||d.kind==='lanza'?'laser':'shot',{kind:d.kind}));
on('enemy_fire',d=>{if(Math.random()<.5)play('efire',{x:d.x})});
on('hit',d=>play(d.crit?'crit':'hit',{x:ex(d)}));
on('kill',d=>{const t=d.type||(d.e&&d.e.type)||'',z=d.boss?'l':(d.elite||BIG[t]||(t==='asteroide'&&(d.size==='g'||(d.e&&d.e.size==='g'))))?'m':'s';play('explode_'+z,{x:d.x!=null?d.x:ex(d)})});
on('explode',d=>play('explode_'+sizeOf(d.size),{x:d.x}));
on('hurt',()=>play('hurt'));
on('shield',()=>play('shield'));
on('graze',d=>play('graze',{count:d.count}));
on('pickup',d=>{const k=String(d.kind||'').toLowerCase();
 if(k==='p'||k==='power'||k==='potencia'){const t0=performance.now();setTimeout(()=>{if(lastPow<t0)play('item')},70);return}
 if(k==='b'||k==='r'||k==='bomba'||k==='bomb'||k==='reparacion'||k==='repair'||k==='item')return void play('item');
 play('pickup',{chain:d.chain})});
on('power',d=>{lastPow=performance.now();play('power',{level:d.level})});
on('bomb',()=>{play('bomb');MUSapi.duck(1.3,.3)});
on('od_ready',()=>play('od_ready'));
on('od_start',()=>{play('od');MUSapi.od(true);say(line('od_start'))});
on('od_end',()=>MUSapi.od(false));
on('combo',d=>{const m=+d.mult||1;if(m>lastMult){play('combo',{mult:m});if(m>=8)say(line('c8'));else if(m>=5)say(line('c5'));else if(m>=4)say(line('c4'))}lastMult=m});
on('hazard_warn',d=>play('laser_warn',{kind:d.kind,x:d.x}));
on('emp',()=>play('emp'));
on('lightning',d=>play('thunder',{x:d.x}));
on('boss_warn',()=>{play('alarm');MUSapi.duck(2.4,.35);say(line('boss_warn'),{queue:true})});
on('boss_start',d=>{bossTok++;const n=d.id==='nova'?'final':'boss';MUSapi.play(n,{fade:.8,restart:!!(cur&&curName===n&&cur.phase>1)})});
on('boss_phase',d=>{play('phase');MUSapi.phase(d.phase);MUSapi.duck(.6,.5)});
on('boss_die',d=>{play('boss_die');MUSapi.duck(3,.3);say(line('boss_die'),{queue:true});const tok=++bossTok;
 if(d.id==='nova')MUSapi.stop(3.5);else setTimeout(()=>{if(tok===bossTok&&(curName==='boss'||curName==='final'))MUSapi.play(lastSector,{intensity:0,fade:3})},3200)});
on('level_start',d=>{bossTok++;lastMult=1;let lv=d.level,mus=null,sec=null;
 if(lv!=null&&typeof lv!=='object'&&_REG&&_REG.levels){const L=_REG.levels;const f=Array.isArray(L)?(L[lv]||L.find&&L.find(x=>x&&(x.id===lv||x.n===lv))):L[lv];if(f)lv=f}
 if(lv&&typeof lv==='object'){mus=lv.music;sec=sectorOf(lv.sector)}
 else if(typeof lv==='number')sec=sectorOf(Math.floor(clamp(lv,0,11)/3)+1);
 if(!sec&&d.sector)sec=sectorOf(d.sector);if(sec)lastSector=sec;
 if(mus==='boss'||mus==='final'||(mus&&TRACKS.indexOf(mus)<0))mus=null;
 MUSapi.play(mus||sec||lastSector,{intensity:1,fade:1.2});MUSapi.intensity(1);MUSapi.od(false)});
on('level_clear',()=>{play('level_up');MUSapi.intensity(0);MUSapi.od(false)});
on('sector_clear',()=>say(line('sector_clear'),{queue:true}));
on('player_die',()=>{play('explode_l');play('hurt');MUSapi.duck(1.5,.4);MUSapi.od(false)});
on('revive',()=>play('revive'));
on('gameover',()=>{MUSapi.stop(2);play('gameover');say(line('gameover'),{queue:true})});
on('victory',()=>{MUSapi.play('victory',{fade:2});say(line('victory'),{queue:true})});
on('radio',()=>play('radio'));
on('screen',d=>{const n=String(d.name||'').toLowerCase();
 if(/^(title|portada|menu|map|mapa|sectores|hangar|codex|codice|códice|settings|ajustes)$/.test(n))MUSapi.play('menu',{fade:1.2});
 else if(n==='victory'||n==='victoria'||n==='credits'||n==='creditos')MUSapi.play('victory',{fade:1.5})});
on('mod_pick',d=>{const r=String(d.rarity||'').toLowerCase();play(/leg/.test(r)?'card_legend':'card_pick')});
const UIK={hover:'ui_hover',click:'ui_click',back:'ui_back',buy:'ui_buy',error:'ui_error',card_in:'card',card_flip:'card',card_pick:'card_pick',stamp:'stamp',count:'count',star:'star'};
on('ui',d=>{const n=UIK[d.kind];if(n)play(n,{flip:d.kind==='card_flip',n:d.n!=null?d.n:d.i})});
})();

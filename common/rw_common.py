"""Shared display code + invariant check for the Readers-Writers programs (no synchronization logic)."""
IDLE, WAIT, READ, WRITE = "Idle", "Waiting", "Reading", "Writing"


def setstate(kind, i, st, **extra):
    def f(s):
        s[kind][i] = st
        s.update(extra)
    return f


def check(s):
    """Mutual-exclusion invariant checked after every state change."""
    w = s["writers"].count(WRITE); r = s["readers"].count(READ)
    if w > 1 or (w and r):
        return f"{w} writer(s) and {r} reader(s) inside the critical section"
    return None


BODY = """<div id="board"></div><div class="legend" id="legend"></div>"""
CSS = """.col{margin-bottom:14px}.col h3{margin:4px 0;font-size:14px}.cards{display:flex;gap:8px;flex-wrap:wrap}
.card{width:96px;padding:10px 6px;border-radius:8px;color:#fff;text-align:center;font-size:13px;transition:background .2s}
.card b{display:block;font-size:16px}#res{padding:14px;border-radius:10px;border:3px solid #444;text-align:center;font-size:14px;transition:all .2s}
#res b{font-size:26px}"""
RW_JS = r"""
const COL={Idle:'#9aa5b1',Waiting:'#f2b134',Reading:'#22a05a',Writing:'#d6455d'};
let RC=[],WC=[];
function setup(){
  const nr=INITIAL.readers.length, nw=INITIAL.writers.length;
  $('board').innerHTML='<div class="col"><h3>Readers</h3><div class="cards" id="rd"></div></div>'
   +'<div class="col"><h3>Shared resource (critical section)</h3><div id="res"></div></div>'
   +'<div class="col"><h3>Writers</h3><div class="cards" id="wr"></div></div><p id="sem" style="font:12px ui-monospace,monospace"></p>';
  for(let i=0;i<nr;i++){const d=document.createElement('div');d.className='card';$('rd').appendChild(d);RC.push(d);}
  for(let i=0;i<nw;i++){const d=document.createElement('div');d.className='card';$('wr').appendChild(d);WC.push(d);}
  $('legend').innerHTML=Object.entries(COL).map(([k,v])=>`<span><i style="background:${v}"></i>${k}</span>`).join('');
}
function render(s,e){
  s.readers.forEach((st,i)=>{RC[i].style.background=COL[st];RC[i].innerHTML='<b>R'+i+'</b>'+st;});
  s.writers.forEach((st,i)=>{WC[i].style.background=COL[st];WC[i].innerHTML='<b>W'+i+'</b>'+st;});
  const nW=s.writers.filter(x=>x=='Writing').length, nR=s.readers.filter(x=>x=='Reading').length;
  const waitR=s.readers.filter(x=>x=='Waiting').length, waitW=s.writers.filter(x=>x=='Waiting').length;
  const r=$('res'); r.style.background=nW?'#fde2e7':nR?'#dcf5e6':'#fff'; r.style.borderColor=nW?'#d6455d':nR?'#22a05a':'#444';
  r.innerHTML='value = <b>'+s.value+'</b><br>'+(nW?'being WRITTEN (exclusive)':nR?'being READ by '+nR+' reader(s) (shared)':'free');
  $('sem').textContent='read_count='+s.readcount+'   wrt='+((nW||nR)?0:1)+(nW?' (held by writer)':nR?' (held by readers)':'')
    +'   waiting: '+waitR+' reader(s), '+waitW+' writer(s)'+(e&&e.bad?'   !! VIOLATION':'');
}
"""

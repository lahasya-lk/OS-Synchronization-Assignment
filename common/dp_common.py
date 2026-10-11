"""Shared display code + invariant check for the Dining Philosophers programs (no synchronization logic)."""
N = 4
THINK, HUNGRY, BACKOFF, ACQ, EAT, REL = ("Thinking", "Hungry", "Backing off",
                                          "Acquiring Forks", "Eating", "Releasing Forks")


def check(s):
    """Invariant: two neighbours never eat together; a chopstick has one owner."""
    for i in range(N):
        if s["phil"][i] == EAT and s["phil"][(i + 1) % N] == EAT:
            return f"P{i} and P{(i+1)%N} eating together"
    return None


BODY = """<svg id="svg" viewBox="0 0 500 500" style="width:100%;max-width:560px"></svg>
<div class="legend" id="legend"></div>"""

JS = r"""
const COL={'Thinking':'#9aa5b1','Hungry':'#f2b134','Backing off':'#e8743b','Acquiring Forks':'#3b82f6','Eating':'#22a05a','Releasing Forks':'#8b5cf6'};
const NS='http://www.w3.org/2000/svg', C=250, R=170;
const ang=i=>(-90+90*i)*Math.PI/180, pol=(r,a)=>[C+r*Math.cos(a),C+r*Math.sin(a)];
const el=(t,at,p)=>{const e=document.createElementNS(NS,t);for(const k in at)e.setAttribute(k,at[k]);(p||$('svg')).appendChild(e);return e;};
let P=[],F=[];
function setup(){
  el('circle',{cx:C,cy:C,r:105,fill:'#f1e4cf',stroke:'#c9b28f','stroke-width':3});
  for(let k=0;k<4;k++){F.push(el('line',{'stroke-linecap':'round','stroke-width':7}));}
  for(let i=0;i<4;i++){const [x,y]=pol(R,ang(i));
    const c=el('circle',{cx:x,cy:y,r:42,stroke:'#333','stroke-width':2});
    const t1=el('text',{x:x,y:y-4,'text-anchor':'middle','font-size':15,'font-weight':700,fill:'#fff'});
    const t2=el('text',{x:x,y:y+13,'text-anchor':'middle','font-size':10,fill:'#fff'});
    P.push({c,t1,t2});}
  $('legend').innerHTML=Object.entries(COL).map(([k,v])=>`<span><i style="background:${v}"></i>${k}</span>`).join('')
    +'<span>Chopstick k sits between P(k-1) and P(k); it moves to its owner when taken.</span>';
}
function render(s,e){
  for(let i=0;i<4;i++){P[i].c.setAttribute('fill',COL[s.phil[i]]);P[i].t1.textContent='P'+i;
    P[i].t2.textContent=s.phil[i]+(s.tries[i]?' #'+s.tries[i]:'');}
  for(let k=0;k<4;k++){ // chopstick k is between philosopher k and k+1 (indices mod 4)
    const a=ang(k)+Math.PI/4, o=s.fork[k]; let m=pol(118,a), col='#555';
    if(o!==null){const q=pol(R,ang(o)); m=[m[0]+(q[0]-m[0])*0.55, m[1]+(q[1]-m[1])*0.55]; col=COL[s.phil[o]];}
    const dx=Math.cos(a)*22, dy=Math.sin(a)*22, l=F[k];
    l.setAttribute('x1',m[0]-dx);l.setAttribute('y1',m[1]-dy);l.setAttribute('x2',m[0]+dx);l.setAttribute('y2',m[1]+dy);
    l.setAttribute('stroke',col);}
  const txt=el_status(s); $('status').textContent=txt;
}
function el_status(s){return 'Chopstick owners: '+s.fork.map((o,k)=>'C'+k+'='+(o===null?'free':'P'+o)).join('  ');}
"""

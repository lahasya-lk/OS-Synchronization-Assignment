"""
sim_common.py - shared helpers used by BOTH programs.

Recorder : thread-safe event recorder. Every state change made by the real
           synchronization code is logged here together with a snapshot of the
           whole system state. This trace is the ONLY input of the HTML page.
build_page: embeds the recorded trace (JSON) in a self-contained HTML player.
"""
import copy, json, os, threading, time


class Recorder:
    def __init__(self, initial_state, check=None):
        self._lock = threading.Lock()          # protects trace + state
        self._t0 = time.monotonic()
        self.state = initial_state
        self.initial = copy.deepcopy(initial_state)
        self.events = []
        self.violations = []
        self._check = check                    # optional invariant checker

    def log(self, actor, msg, update=None):
        """Apply `update(state)` and append an event with a state snapshot."""
        with self._lock:
            if update:
                update(self.state)
            bad = self._check(self.state) if self._check else None
            t = time.monotonic() - self._t0
            if bad:
                self.violations.append(bad)
            self.events.append({"t": round(t, 3), "actor": actor, "msg": msg,
                                "bad": bool(bad), "state": copy.deepcopy(self.state)})
            print(f"[{t:6.2f}s] {actor:>4}: {msg}" + (f"   <-- VIOLATION: {bad}" if bad else ""))


PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>__TITLE__</title>
<style>
 body{font-family:system-ui,Arial,sans-serif;margin:0;padding:16px;background:#f6f7f9;color:#1b1f24}
 h1{font-size:20px;margin:0 0 4px} p.sub{margin:0 0 12px;color:#555;font-size:13px}
 .wrap{display:flex;gap:16px;flex-wrap:wrap}
 .panel{background:#fff;border:1px solid #d8dce2;border-radius:10px;padding:12px}
 #stage{flex:1 1 520px;min-width:320px}
 #side{flex:1 1 320px;min-width:280px}
 .ctl{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
 button,select{padding:6px 12px;border:1px solid #aab;border-radius:6px;background:#fff;cursor:pointer}
 #slider{width:100%} #log{height:360px;overflow:auto;font:12px/1.5 ui-monospace,Consolas,monospace}
 .row{padding:2px 6px;border-radius:4px;cursor:pointer} .row.active{background:#dbeafe;font-weight:600}
 .row.bad{color:#b91c1c} .legend span{display:inline-block;margin:2px 10px 2px 0;font-size:12px}
 .legend i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:4px;vertical-align:-1px}
 __CSS__
</style></head><body>
<h1>__TITLE__</h1><p class="sub">__SUB__ &middot; generated from the execution trace of the program (__N__ events)</p>
<div class="wrap">
 <div id="stage" class="panel">__BODY__</div>
 <div id="side" class="panel">
  <div class="ctl"><button id="play">&#9654; Start</button><button id="step">Step</button>
   <button id="reset">Reset</button>
   <select id="speed"><option value="0.5">0.5x</option><option value="1" selected>1x</option>
   <option value="2">2x</option><option value="4">4x</option></select>
   <span id="pos"></span><span id="time"></span></div>
  <input type="range" id="slider" min="0" max="0" value="0">
  <div id="log"></div></div>
</div>
<script>
const EV = __EVENTS__, INITIAL = __INITIAL__;
let idx=-1, timer=null, playing=false;
const $ = id => document.getElementById(id);
__JS__
function show(k){
  idx=k; const e=EV[k]; render(e.state,e);
  $('slider').value=k; $('pos').textContent=(k+1)+'/'+EV.length; $('time').textContent=e.t.toFixed(2)+'s';
  document.querySelectorAll('.row.active').forEach(r=>r.classList.remove('active'));
  const r=$('r'+k); r.classList.add('active'); r.scrollIntoView({block:'nearest'});
}
function resetAll(){ stop(); idx=-1; render(INITIAL,null); $('slider').value=0; $('pos').textContent='0/'+EV.length; $('time').textContent='';
  document.querySelectorAll('.row.active').forEach(r=>r.classList.remove('active')); }
function stop(){ playing=false; clearTimeout(timer); $('play').innerHTML='&#9654; Start'; }
function tick(){
  if(idx>=EV.length-1){ stop(); return; }
  show(idx+1);
  if(idx<EV.length-1){ const dt=(EV[idx+1].t-EV[idx].t)*1000/parseFloat($('speed').value);
    timer=setTimeout(tick, Math.min(Math.max(dt,40),1500)); } else stop();
}
$('play').onclick=()=>{ if(playing){stop();return;} if(idx>=EV.length-1) resetAll();
  playing=true; $('play').innerHTML='&#10074;&#10074; Pause'; tick(); };
$('step').onclick=()=>{ stop(); if(idx<EV.length-1) show(idx+1); };
$('reset').onclick=resetAll;
$('slider').max=EV.length-1; $('slider').oninput=e=>{ stop(); show(parseInt(e.target.value)); };
EV.forEach((e,k)=>{ const d=document.createElement('div'); d.className='row'+(e.bad?' bad':''); d.id='r'+k;
  d.textContent=e.t.toFixed(2).padStart(6)+'s  '+e.actor.padEnd(4)+' '+e.msg; d.onclick=()=>{stop();show(k);}; $('log').appendChild(d); });
setup(); resetAll();
</script></body></html>"""


def build_page(path, title, sub, recorder, body_html, js, css=""):
    page = (PAGE.replace("__TITLE__", title).replace("__SUB__", sub)
            .replace("__N__", str(len(recorder.events))).replace("__BODY__", body_html)
            .replace("__CSS__", css).replace("__JS__", js)
            .replace("__EVENTS__", json.dumps(recorder.events))
            .replace("__INITIAL__", json.dumps(recorder.initial)))
    import os
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"\nHTML simulation written to: {path}")


def default_out(filename):
    """<repo>/generated_html/<filename>, independent of the current working directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "generated_html", filename)


import {PII_COLS} from './data.js';
import {readFile, normalize, detectSnapshot, sanitize, coreKpis, compareKpis, fieldDiff, availableNameCol} from './logic.js';

const state = {
  base:null, baseName:null, baseDate:null,
  cur:null, curName:null, curDate:null
};

const el = (sel)=>document.querySelector(sel);
const content = el('#content');

function setNow(){
  const now = new Date();
  el('#now').textContent = `Nu: ${now.toLocaleDateString('nl-NL')} ${now.toLocaleTimeString('nl-NL',{hour:'2-digit',minute:'2-digit'})}`;
}
setNow(); setInterval(setNow, 30_000);

function updateHeader(){
  el('#nameBase').textContent = state.baseName || '—';
  el('#nameCur').textContent = state.curName || '—';
  el('#pillBase').textContent = state.baseDate ? fmtDate(state.baseDate) : 'Onbekend';
  el('#pillCur').textContent = state.curDate ? fmtDate(state.curDate) : 'Onbekend';
  const ok = (state.base && state.cur);
  el('#pillStatus').textContent = ok? 'Bestanden geladen' : 'Upload links de bestanden';
}

function fmtDate(d){
  try{ return d.toLocaleDateString('nl-NL'); }catch{ return 'Onbekend'; }
}

// File handlers
el('#fileBase').addEventListener('change', async (e)=>{
  const f = e.target.files[0]; if(!f) return;
  const {rows, name} = await readFile(f);
  const norm = normalize(rows);
  state.base = norm.rows;
  state.baseName = name;
  state.baseDate = detectSnapshot(norm.rows);
  updateHeader();
  render();
});
el('#fileCur').addEventListener('change', async (e)=>{
  const f = e.target.files[0]; if(!f) return;
  const {rows, name} = await readFile(f);
  const norm = normalize(rows);
  state.cur = norm.rows;
  state.curName = name;
  state.curDate = detectSnapshot(norm.rows);
  updateHeader();
  render();
});

// Manual dates
el('#dateBase').addEventListener('change', e=>{
  state.baseDate = e.target.value? new Date(e.target.value) : null;
  updateHeader();
});
el('#dateCur').addEventListener('change', e=>{
  state.curDate = e.target.value? new Date(e.target.value) : null;
  updateHeader();
});

// Routing
document.querySelectorAll('.menu-item').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('.menu-item').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    el('#pageTitle').textContent = btn.textContent;
    render(btn.dataset.page);
  });
});

function render(page='dashboard'){
  if(page==='dashboard') return renderDashboard();
  if(page==='klantenkaart') return renderKlantenkaart();
  if(page==='vergelijker') return renderVergelijker();
  if(page==='advanced') return renderAdvanced();
}

function needUploads(){
  if(!state.base || !state.cur){
    content.innerHTML = `<div class="card notice">Upload eerst <b>Nulmeting</b> en <b>Actueel</b> (xlsx/csv) in de zijbalk.</div>`;
    return true;
  }
  return false;
}

// Dashboard
function metric(label, value, delta=null){
  return `
  <div class="card metric">
    <div class="label">${label}</div>
    <div class="value">${value}</div>
    ${delta!==null? `<div class="delta">${delta>0? '▲':''}${delta}</div>`:''}
  </div>`;
}

function renderDashboard(){
  if(needUploads()) return;
  const baseS = sanitize(state.base);
  const curS = sanitize(state.cur);
  const b = coreKpis(baseS);
  const c = coreKpis(curS);
  const d = compareKpis(b,c);

  const pct = (v)=> v===null? '—' : `${v.toFixed(1)}%`;

  content.innerHTML = `
    <div class="grid kpi4">
      ${metric('Aantal clubs (actueel)', c.total_clubs, d.total_clubs ?? 0)}
      ${metric('Totaal leden', c.members_sum, d.members_sum ?? 0)}
      ${metric('Totaal vrijwilligers', c.volunteers_sum, d.volunteers_sum ?? 0)}
      ${metric('% met kantine', pct(c.has_canteen_pct), (d.has_canteen_pct??0).toFixed(1)+'%')}
    </div>
    <div class="card">
      <h3>Top-3 Gemeenten (actueel)</h3>
      <div class="list">${c.top_municipality || '—'}</div>
    </div>
    <div class="card">
      <h3>Top-3 Sporten (actueel)</h3>
      <div class="list">${c.top_sport || '—'}</div>
    </div>
  `;
}

// Klantenkaart
function renderKlantenkaart(){
  if(!state.cur){
    content.innerHTML = `<div class="card notice">Upload eerst het <b>Actueel</b> bestand.</div>`;
    return;
  }
  const rows = state.cur;
  const cols = Object.keys(rows[0]||{});
  const nameCol = 'name';

  const holder = document.createElement('div');
  holder.innerHTML = `
    <div class="card">
      <div class="actions">
        <input class="input" id="q" placeholder="Zoek op naam..." />
        <button class="btn" id="btnClear">Leeg</button>
      </div>
    </div>
    <div id="detail"></div>
  `;
  content.innerHTML = '';
  content.appendChild(holder);

  const q = holder.querySelector('#q');
  const btnClear = holder.querySelector('#btnClear');
  const detail = holder.querySelector('#detail');

  btnClear.onclick = ()=>{ q.value=''; show(''); };
  q.oninput = ()=> show(q.value);

  function show(text){
    const opts = rows.filter(r=> (r[nameCol]||'').toLowerCase().includes((text||'').toLowerCase())).slice(0,50);
    if(opts.length===0){ detail.innerHTML = `<div class="card notice">Geen resultaten…</div>`; return; }
    // Selecteer eerste match
    const r = opts[0];
    const list = Object.entries(r).filter(([k,v])=> String(v).trim()!=='' ).map(([k,v])=> 
      `<div class="kv"><div class="k">${k}</div><div class="v">${v}</div></div>`).join('');
    detail.innerHTML = `<div class="card"><h3>${r[nameCol]||'—'}</h3>${list}</div>`;
  }
  show('');
}

// Vergelijker
function renderVergelijker(){
  if(!state.cur){
    content.innerHTML = `<div class="card notice">Upload eerst het <b>Actueel</b> bestand.</div>`;
    return;
  }
  const rows = state.cur;
  const nameCol = 'name';
  const names = [...new Set(rows.map(r=>r[nameCol]).filter(Boolean))];

  content.innerHTML = `
    <div class="card">
      <div class="actions">
        <select class="input" id="a">${names.map(n=>`<option>${n}</option>`).join('')}</select>
        <select class="input" id="b">${names.map(n=>`<option>${n}</option>`).join('')}</select>
      </div>
    </div>
    <div id="cmp"></div>
  `;

  const aSel = el('#a'); const bSel = el('#b'); const out = el('#cmp');
  function go(){
    if(aSel.value===bSel.value){ out.innerHTML = `<div class="card notice">Kies twee verschillende clubs.</div>`; return; }
    const a = rows.find(r=>r[nameCol]===aSel.value) || {};
    const b = rows.find(r=>r[nameCol]===bSel.value) || {};
    const dif = fieldDiff(a,b);
    const lines = Object.entries(dif).map(([k,v])=>`<div>• <b>${k.replaceAll('_',' ')}</b>: ${v}</div>`).join('');
    out.innerHTML = `<div class="card"><h3>${aSel.value} ↔ ${bSel.value}</h3><div class="list">${lines}</div></div>`;
  }
  aSel.onchange=go; bSel.onchange=go; go();
}

// Advanced
function renderAdvanced(){
  if(!state.cur){
    content.innerHTML = `<div class="card notice">Upload eerst het <b>Actueel</b> bestand.</div>`;
    return;
  }
  const rows = sanitize(state.cur);
  const municipalities = [...new Set(rows.map(r=>r.municipality).filter(Boolean))];
  const sports = [...new Set(rows.map(r=>r.sport).filter(Boolean))];

  content.innerHTML = `
    <div class="card">
      <div class="actions">
        <label>Filter Gemeente</label>
        <select class="input" id="fltM" multiple>${municipalities.map(m=>`<option>${m}</option>`).join('')}</select>
        <label>Filter Sport</label>
        <select class="input" id="fltS" multiple>${sports.map(s=>`<option>${s}</option>`).join('')}</select>
        <label>KPI</label>
        <select class="input" id="metric">
          <option>Aantal clubs</option>
          <option>Totaal leden</option>
          <option>Gemiddelde leden/club</option>
          <option>Totaal vrijwilligers</option>
          <option>Gemiddelde vrijwilligers/club</option>
          <option>% met kantine</option>
        </select>
        <label>Groepeer op (max 2)</label>
        <select class="input" id="groupBy" multiple>
          <option>municipality</option>
          <option>sport</option>
          <option>federation</option>
        </select>
        <button class="btn" id="btnRun">Toon inzicht</button>
      </div>
    </div>
    <div id="advOut"></div>
  `;

  const getMulti = (sel)=> [...el(sel).selectedOptions].map(o=>o.value);

  el('#btnRun').onclick = ()=>{
    const fltM = getMulti('#fltM'), fltS = getMulti('#fltS');
    const metric = el('#metric').value;
    const groups = getMulti('#groupBy').slice(0,2);

    let work = rows.slice();
    if(fltM.length) work = work.filter(r=> fltM.includes(r.municipality));
    if(fltS.length) work = work.filter(r=> fltS.includes(r.sport));

    const compute = (arr)=>{
      if(metric==='Aantal clubs') return arr.length;
      if(metric==='Totaal leden') return arr.reduce((a,r)=>a+(r.members_count||0),0);
      if(metric==='Gemiddelde leden/club'){
        const vals = arr.map(r=>r.members_count).filter(v=>Number.isFinite(v));
        return vals.length? (vals.reduce((a,b)=>a+b,0)/vals.length) : 0;
      }
      if(metric==='Totaal vrijwilligers') return arr.reduce((a,r)=>a+(r.volunteers_count||0),0);
      if(metric==='Gemiddelde vrijwilligers/club'){
        const vals = arr.map(r=>r.volunteers_count).filter(v=>Number.isFinite(v));
        return vals.length? (vals.reduce((a,b)=>a+b,0)/vals.length) : 0;
      }
      if(metric==='% met kantine') return arr.length? (arr.filter(r=>r.has_canteen===true).length/arr.length*100):0;
      return 0;
    };

    if(groups.length===0){
      const v = compute(work);
      el('#advOut').innerHTML = `<div class="card"><h3>Resultaat</h3><div class="value">${typeof v==='number'? (Number.isInteger(v)? v : v.toFixed(1)) : v}</div></div>`;
    }else{
      // per groep tekstregels
      const totals = work.length||1;
      const map = new Map();
      work.forEach(r=>{
        const key = groups.map(g=> r[g]||'Onbekend').join(' · ');
        if(!map.has(key)) map.set(key, []);
        map.get(key).push(r);
      });
      let lines = '';
      [...map.entries()].forEach(([k,arr])=>{
        const v = compute(arr);
        const pct = arr.length/totals*100;
        const vtxt = (typeof v==='number'? (Number.isInteger(v)? v : v.toFixed(1)) : v);
        lines += `<div>• <b>${k}</b>: ${vtxt} · ${arr.length} clubs · ${pct.toFixed(1)}% van totaal</div>`;
      });
      el('#advOut').innerHTML = `<div class="card"><h3>Resultaten</h3><div class="list">${lines||'_Geen resultaten_'}</div></div>`;
    }
  };
}

render();

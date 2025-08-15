
import {PII_COLS, canonize, parseBoolean, toNumber} from './data.js';

export function readFile(file){
  return new Promise((resolve,reject)=>{
    const reader = new FileReader();
    reader.onload = e => {
      const data = new Uint8Array(e.target.result);
      let wb;
      try{
        wb = XLSX.read(data, {type:'array'});
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        const json = XLSX.utils.sheet_to_json(ws, {defval:''});
        resolve({rows:json, name:file.name});
      }catch(err){
        // try CSV simple parse
        try{
          const text = new TextDecoder().decode(data);
          const lines = text.split(/\r?\n/).filter(Boolean);
          const headers = lines[0].split(';').length>1 ? lines[0].split(';') : lines[0].split(',');
          const rows = lines.slice(1).map(line=>{
            const cells = line.split(';').length>1 ? line.split(';') : line.split(',');
            const obj = {};
            headers.forEach((h,i)=>{ obj[h]=cells[i]||''; });
            return obj;
          });
          resolve({rows, name:file.name});
        }catch(e2){
          reject(e2);
        }
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

export function normalize(rows){
  if(!rows || rows.length===0) return {rows:[], columns:[]};
  const colsOrig = Object.keys(rows[0]);
  const map = {};
  colsOrig.forEach(c=> map[c] = canonize(c));
  const rowsCanon = rows.map(r=>{
    const o = {};
    Object.entries(r).forEach(([k,v])=>{
      const ck = map[k];
      if(ck==='has_canteen'){
        const b = parseBoolean(v);
        o[ck] = (b===null? false : b);
      }else if(['members_count','volunteers_count','membership_fee'].includes(ck)){
        o[ck] = toNumber(v);
      }else{
        o[ck] = (v===undefined || v===null) ? '' : String(v).trim();
      }
    });
    return o;
  });
  return {rows:rowsCanon, columns:[...new Set(Object.values(map))]};
}

export function detectSnapshot(rows){
  for(const r of rows){
    if(r.snapshot_date){
      const d = new Date(r.snapshot_date);
      if(!isNaN(d)) return d;
    }
  }
  return null;
}

export function sanitize(rows){
  return rows.map(r=>{
    const o = {...r};
    for(const k of PII_COLS) delete o[k];
    return o;
  });
}

export function availableNameCol(columns){
  // After canonize, prefer name
  if(columns.includes('name')) return 'name';
  // fallback: first column
  return columns[0] || 'name';
}

// KPIs
export function coreKpis(rows){
  const total = rows.length;
  const sum = (key)=> rows.reduce((a,r)=> a + (Number.isFinite(r[key])? r[key] : 0), 0);
  const avg = (key)=> {
    const vals = rows.map(r=>Number.isFinite(r[key])? r[key] : null).filter(v=>v!==null);
    if(vals.length===0) return null;
    return vals.reduce((a,b)=>a+b,0)/vals.length;
  };
  const canteenPct = rows.length? (rows.filter(r=>r.has_canteen===true).length/rows.length*100) : null;

  const top3text = (key)=>{
    const map = new Map();
    rows.forEach(r=>{
      const k = (r[key] || 'Onbekend');
      map.set(k, (map.get(k)||0)+1);
    });
    const total = rows.length||1;
    return [...map.entries()].sort((a,b)=>b[1]-a[1]).slice(0,3)
      .map(([k,c])=> `${k}: ${c} (${(c/total*100).toFixed(1)}%)`).join(' · ') || '-';
  };

  return {
    total_clubs: total,
    members_sum: sum('members_count') || 0,
    members_avg: avg('members_count'),
    volunteers_sum: sum('volunteers_count') || 0,
    volunteers_avg: avg('volunteers_count'),
    has_canteen_pct: canteenPct,
    top_municipality: top3text('municipality'),
    top_sport: top3text('sport')
  };
}

export function compareKpis(b, c){
  const d = {};
  for(const k of Object.keys(b)){
    if(typeof b[k]==='number' && typeof c[k]==='number'){
      d[k] = c[k]-b[k];
    }
  }
  return d;
}

export function fieldDiff(a, b){
  const nonPII = ['name','sport','municipality','federation','street','postal_code','city','has_canteen','members_count','volunteers_count','membership_fee'];
  const out = {};
  for(const col of nonPII){
    const va = a[col] ?? ''; const vb = b[col] ?? '';
    out[col] = (String(va)===String(vb)) ? '—' : `${va} → ${vb}`;
  }
  return out;
}

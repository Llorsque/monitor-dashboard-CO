
export const PII_COLS = new Set(['contact_person','email','phone','role']);

export const SYNONYMS = {
  // name
  'clubnaam':'name','club':'name','vereniging':'name','organisatie':'name','naam':'name','relatie':'name',
  // sport
  'sport':'sport','sporttak':'sport',
  // municipality / city
  'gemeente':'municipality','municipality':'municipality',
  'plaats':'city','stad':'city','woonplaats':'city','dorp':'city',
  // federation
  'sportsbond':'federation','bond':'federation','federatie':'federation',
  // address
  'straat + huisnummer':'street','straat en huisnummer':'street','adres':'street','straat':'street','huisnummer':'street',
  'postcode':'postal_code',
  // contact / pii
  'contactpersoon':'contact_person','contact persoon':'contact_person','contact':'contact_person',
  'e-mail':'email','email':'email','mail':'email',
  'telefoonnummer':'phone','telefoon':'phone','mobiel':'phone','gsm':'phone',
  'functie':'role','rol':'role',
  // booleans
  'eigen kantine':'has_canteen','kantine':'has_canteen',
  // numerics
  'aantal leden':'members_count','leden':'members_count',
  'aantal vrijwilligers':'volunteers_count','vrijwilligers':'volunteers_count',
  'contributie':'membership_fee','lidmaatschap':'membership_fee',
  // snapshot
  'peildatum':'snapshot_date','stand per':'snapshot_date','datum':'snapshot_date'
};

export function canonize(col){
  const key = String(col||'').trim().toLowerCase();
  return SYNONYMS[key] || key;
}

export function parseBoolean(v){
  const t = String(v||'').trim().toLowerCase();
  if(['ja','true','1','yes','y'].includes(t)) return true;
  if(['nee','false','0','no','n'].includes(t)) return false;
  return null;
}

export function toNumber(v){
  if(v===null || v===undefined || v==='') return null;
  const n = Number(String(v).replace(',','.'));
  return Number.isFinite(n) ? n : null;
}

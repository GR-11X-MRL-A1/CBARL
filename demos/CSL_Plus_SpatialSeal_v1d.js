// CSL_Plus_SpatialSeal_v1d.js — GR-11X-MRL-A1
// Scriptable-compatible (no TextEncoder). Includes robust file picker + spatial resonance.
// Schema v1.3

// ---------- helpers ----------
function toUTF8Array(str){const out=[];for(let i=0;i<str.length;i++){let c=str.charCodeAt(i);
if(c<128)out.push(c);else if(c<2048){out.push((c>>6)|192,(c&63)|128);}
else if(c<55296||c>=57344){out.push((c>>12)|224,((c>>6)&63)|128,(c&63)|128);}
else{i++;c=65536+(((str.charCodeAt(i-1)&1023)<<10)|(str.charCodeAt(i)&1023));
out.push((c>>18)|240,((c>>12)&63)|128,((c>>6)&63)|128,(c&63)|128);} }
return new Uint8Array(out);}
async function sha384(bytes){
  try{ return bytesToHex(await Crypto.digest(Crypto.Algorithm.SHA384, bytes)); }
  catch(e){ try{ const h512=await Crypto.digest(Crypto.Algorithm.SHA512, bytes); return bytesToHex(h512.slice(0,48)); }
  catch(err){ let sum=0;for(const b of bytes) sum=(sum*131+b)>>>0;const arr=new Uint8Array(48);
  for(let i=0;i<48;i++){arr[i]=(sum>>>((i%4)*8))&0xff; sum=(sum*2654435761)>>>0;} return bytesToHex(arr);} } }
function bytesToHex(u8){return Array.from(u8).map(b=>b.toString(16).padStart(2,'0')).join('');}
function nowISO(d=new Date()){const z=n=>String(n).padStart(2,'0');const tz=-d.getTimezoneOffset();
const s=(tz>=0?'+':'-')+z(Math.floor(Math.abs(tz)/60))+':'+z(Math.abs(tz)%60);
return d.getFullYear()+'-'+z(d.getMonth()+1)+'-'+z(d.getDate())+'T'+z(d.getHours())+':'+z(d.getMinutes())+':'+z(d.getSeconds())+s;}
function sanitizeSlug(s){return (s||'artifact').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,80);}
function humanBytes(n){const u=['B','KB','MB','GB'];let i=0;while(n>=1024&&i<u.length-1){n/=1024;i++;}return `${n.toFixed(1)} ${u[i]}`;}

// ---------- main ----------
const fm = FileManager.iCloud();
let payloadBytes, payloadLabel="", payloadSize="";

// choose source
const pick = new Alert(); pick.title="CSL-Plus Spatial Seal"; pick.message="Choose sealing source.";
pick.addAction("Pick a file"); pick.addAction("Enter text payload");
const mode = await pick.presentAlert();

if(mode===0){
  // BEGIN PICK-A-FILE
  const picked = await DocumentPicker.open();                 // may be [string] or string
  let path = Array.isArray(picked) ? picked[0] : picked;
  if(!path || typeof path!=='string') throw new Error("No file selected.");
  await fm.downloadFileFromiCloud(path);

  // Try text first
  let dataStr = fm.readString(path);
  if (dataStr == null) {
    const data = fm.read(path); const raw = data.toRawString(); // bytes 0–255
    const bytes = new Uint8Array(raw.length);
    for (let i=0;i<raw.length;i++) bytes[i] = raw.charCodeAt(i) & 0xff;
    payloadBytes = bytes;
  } else {
    payloadBytes = toUTF8Array(dataStr);
  }
  payloadLabel = String(fm.fileName(path,true) || "artifact");
  payloadSize  = humanBytes(payloadBytes.length);
  // END PICK-A-FILE
} else {
  const a=new Alert(); a.title="Enter Payload Text"; a.addTextField("Text to seal");
  a.addTextField("Optional Artifact Title"); a.addAction("OK"); await a.present();
  const text=a.textFieldValue(0)||""; payloadBytes=toUTF8Array(text);
  payloadLabel=a.textFieldValue(1)||"payload.txt"; payloadSize=humanBytes(payloadBytes.length);
}

// timestamps
const t = new Alert(); t.title="Timestamps"; t.addTextField("t_in ISO", nowISO()); t.addTextField("t_out ISO", nowISO());
t.addAction("Continue"); await t.present(); const t_in=t.textFieldValue(0), t_out=t.textFieldValue(1);
const durMs=Math.max(0, new Date(t_out)-new Date(t_in));

// spatial + planetary
const m=new Alert(); m.title="Spatial & Planetary";
m.addTextField("Facing azimuth (0–359)","180");
m.addTextField("Location (logical)","Johnson City, NY (logical)");
m.addTextField("Planetary Day","Mercury");
m.addTextField("Planetary Hour","Venus");
m.addTextField("Flow","Venus→Mercury");
m.addTextField("Moon","13° Aries");
m.addTextField("Nakshatra","Bharaṇī");
m.addTextField("Vector Quality","Right Action through Speech");
m.addTextField("Notes","Sealed during ADA correspondence; resonance alignment.");
m.addAction("Seal"); await m.present();
const facing_deg=parseInt(m.textFieldValue(0)||"0",10);
const location_str=m.textFieldValue(1), planetary_day=m.textFieldValue(2), planetary_hour=m.textFieldValue(3);
const planetary_flow=m.textFieldValue(4), moon=m.textFieldValue(5), nakshatra=m.textFieldValue(6);
const vector_quality=m.textFieldValue(7), notes=m.textFieldValue(8);

// hashes + blocks
const payloadHash=await sha384(payloadBytes);
const s1_content=payloadHash;
const s2_lite_input=JSON.stringify({t_in,t_out,durMs,location:location_str})+payloadHash;
const s2_lite=await sha384(toUTF8Array(s2_lite_input));

const csl_plus={
  schema:"CSL-Plus@GR-11X-MRL-A1/v1.3",
  t_in,t_out,duration_ms:durMs,
  location:location_str,facing_deg,
  planetary_day,planetary_hour,planetary_flow,moon,nakshatra,
  vector_quality,artifact:payloadLabel,artifact_size:payloadSize,
  hashes:{payload_sha384:payloadHash,s1_content,s2_lite},
  notes
};

const bangLines=[
"!BEGIN BANGCHECK",
`!RPP ${payloadLabel} (${payloadSize})`,
`!CSL ${csl_plus.schema}`,
`!S1_CONTENT ${s1_content}`,
`!S2_LITE ${s2_lite}`,
`!ANCHORS Day=${planetary_day} Hour=${planetary_hour} Flow=${planetary_flow} Moon=${moon} Nakshatra=${nakshatra}`,
`!SPATIAL Facing=${facing_deg}° Loc=${location_str}`,
`!VECTOR ${vector_quality}`,
`!NOTES ${notes}`,
"!END BANGCHECK"
];
const bangBlock=bangLines.join("\n");
const bangHash=await sha384(toUTF8Array(bangBlock));

// write outputs
const today=new Date();
const base=`[${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}]_CSL-PLUS_${sanitizeSlug(payloadLabel)}`;
const outJsonPath=fm.joinPath(fm.documentsDirectory(),`${base}.json`);
const outTxtPath =fm.joinPath(fm.documentsDirectory(),`${base}.txt`);
fm.writeString(outJsonPath, JSON.stringify(csl_plus,null,2));
fm.writeString(outTxtPath, `${bangBlock}\n!SHA384-BLOCK ${bangHash}\n\nANNEX: ${new Date().toISOString().replace('.000','')} · ${payloadHash} · ${bangHash} · ${payloadLabel}`);
Pasteboard.copy(`${bangBlock}\n!SHA384-BLOCK ${bangHash}`);
QuickLook.present(outTxtPath);

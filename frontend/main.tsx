import React,{useEffect,useState} from "react"
import {createRoot} from "react-dom/client"
import {MapContainer,TileLayer,CircleMarker,Popup} from "react-leaflet"
import "leaflet/dist/leaflet.css"
import "./styles.css"

const API=import.meta.env.VITE_API_URL||"http://localhost:8000"

const dict:any={
 en:{home:"Dashboard",risk:"AI Risk Forecast",map:"Live Map",rescue:"Rescue",volunteers:"Volunteers",sos:"SOS",report:"Report",settings:"Settings",safe:"Safe Places",title:"Predict Risk. Protect People. Coordinate Rescue. Save Lives.",riskNow:"Current risk",people:"People at risk",safePeople:"People safe",unconfirmed:"Not yet confirmed safe",forecast:"7-day AI-assisted forecast",official:"Official alerts take priority over AI assessment.",getRisk:"Refresh risk assessment",sendSOS:"SEND SOS",reportIncident:"Report incident",register:"Register volunteer"},
 te:{home:"డాష్‌బోర్డ్",risk:"AI ప్రమాద అంచనా",map:"లైవ్ మ్యాప్",rescue:"రెస్క్యూ",volunteers:"వాలంటీర్లు",sos:"SOS",report:"నివేదించు",settings:"సెట్టింగ్స్",safe:"సురక్షిత ప్రదేశాలు",title:"ప్రమాదాన్ని అంచనా వేయండి. ప్రజలను రక్షించండి.",riskNow:"ప్రస్తుత ప్రమాదం",people:"ప్రమాదంలో ప్రజలు",safePeople:"సురక్షిత ప్రజలు",unconfirmed:"ఇంకా నిర్ధారించబడలేదు",forecast:"7 రోజుల AI సహాయక అంచనా",official:"అధికారిక హెచ్చరికలకు ప్రాధాన్యత ఉంటుంది.",getRisk:"ప్రమాద అంచనాను రిఫ్రెష్ చేయండి",sendSOS:"SOS పంపండి",reportIncident:"ప్రమాదాన్ని నివేదించండి",register:"వాలంటీర్ నమోదు"},
 hi:{home:"डैशबोर्ड",risk:"AI जोखिम पूर्वानुमान",map:"लाइव मैप",rescue:"बचाव",volunteers:"स्वयंसेवक",sos:"SOS",report:"रिपोर्ट",settings:"सेटिंग्स",safe:"सुरक्षित स्थान",title:"जोखिम का अनुमान लगाएं। लोगों की रक्षा करें।",riskNow:"वर्तमान जोखिम",people:"जोखिम में लोग",safePeople:"सुरक्षित लोग",unconfirmed:"अभी पुष्टि नहीं हुई",forecast:"7-दिन AI-सहायित पूर्वानुमान",official:"आधिकारिक चेतावनियों को प्राथमिकता है.",getRisk:"जोखिम अपडेट करें",sendSOS:"SOS भेजें",reportIncident:"घटना रिपोर्ट करें",register:"स्वयंसेवक पंजीकरण"}
}
const languages=["en","te","hi","ta","kn","ml","mr","bn","gu","or"]

type Risk={combined_hazard_score:number,combined_level:string,ai_risk_forecast:any,earthquake_signal:any,resource_estimate:any,rescue_priority_example:number,disclaimer:string}

function App(){
 const [lang,setLang]=useState(localStorage.getItem("lang")||"en")
 const [dark,setDark]=useState(localStorage.getItem("theme")!=="light")
 const [tab,setTab]=useState("home")
 const [pos,setPos]=useState({lat:16.5449,lon:80.5150})
 const [risk,setRisk]=useState<Risk|null>(null)
 const [loading,setLoading]=useState(false)
 const [sos,setSos]=useState("")
 const [reports,setReports]=useState<any[]>([])
 const [volunteers,setVolunteers]=useState<any[]>([])
 const t=dict[lang]||dict.en

 useEffect(()=>{localStorage.setItem("lang",lang)},[lang])
 useEffect(()=>{localStorage.setItem("theme",dark?"dark":"light");document.documentElement.dataset.theme=dark?"dark":"light"},[dark])
 useEffect(()=>{navigator.geolocation?.getCurrentPosition(p=>setPos({lat:p.coords.latitude,lon:p.coords.longitude}))},[])
 useEffect(()=>{loadRisk();loadReports();loadVolunteers()},[pos.lat,pos.lon])

 async function loadRisk(){
   setLoading(true)
   try{const r=await fetch(`${API}/api/risk/combined?lat=${pos.lat}&lon=${pos.lon}&population=25000&vulnerability=62`);setRisk(await r.json())}
   catch(e){console.error(e)}
   finally{setLoading(false)}
 }
 async function loadReports(){try{setReports(await (await fetch(`${API}/api/reports`)).json())}catch{}}
 async function loadVolunteers(){try{setVolunteers(await (await fetch(`${API}/api/volunteers`)).json())}catch{}}

 async function triggerSOS(){
   const name=prompt("Your name")||"Anonymous"
   try{
     const r=await fetch(`${API}/api/sos`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,latitude:pos.lat,longitude:pos.lon,message:"Emergency SOS from SURAKSHA AI"})})
     const d=await r.json(); setSos(`SOS #${d.id} active at ${pos.lat.toFixed(4)}, ${pos.lon.toFixed(4)}`)
   }catch{setSos("Could not reach the server. Keep emergency services accessible and retry when connected.")}
 }
 async function report(){
   const type=prompt("Disaster type (Flood/Earthquake/Cyclone/etc.)")||"Other"
   const sev=Number(prompt("Severity 1-5","3")||3)
   const desc=prompt("Describe what you see")||""
   await fetch(`${API}/api/reports`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({disaster_type:type,severity:sev,latitude:pos.lat,longitude:pos.lon,description:desc})})
   await loadReports(); alert("Report submitted.")
 }
 async function addVolunteer(){
   const name=prompt("Name")||"Volunteer"
   const skill=prompt("Skill (first aid, boat, driver, rescue, medical)")||"general"
   await fetch(`${API}/api/volunteers`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,skill,latitude:pos.lat,longitude:pos.lon})})
   await loadVolunteers()
 }
 const level=risk?.combined_level||"GREEN"
 const score=risk?.combined_hazard_score??0

 return <div className="app">
  <header className="topbar">
   <div className="brand"><span className="logo">✚</span><div><b>SURAKSHA AI</b><small>Predict Risk • Protect People</small></div></div>
   <div className="top-actions">
    <select value={lang} onChange={e=>setLang(e.target.value)}>{languages.map(x=><option key={x} value={x}>{x.toUpperCase()}</option>)}</select>
    <button className="icon" onClick={()=>setDark(!dark)} aria-label="Toggle theme">{dark?"☀":"☾"}</button>
   </div>
  </header>
  <div className="layout">
   <aside className="sidebar">
    {[[ "home","⌂",t.home],["risk","◉",t.risk],["map","⌖",t.map],["rescue","⚕",t.rescue],["volunteers","♙",t.volunteers],["report","!",t.report],["settings","⚙",t.settings]].map(([id,ic,label])=>
      <button className={tab===id?"nav active":"nav"} onClick={()=>setTab(id)}><span>{ic}</span>{label}</button>)}
    <div className="side-sos"><button onClick={triggerSOS}>{t.sos}</button></div>
   </aside>
   <main className="content">
    <section className="hero">
      <div><p className="eyebrow">INTELLIGENT DISASTER MANAGEMENT</p><h1>{t.title}</h1><p className="muted">AI-assisted risk assessment + GIS + population vulnerability + rescue coordination</p></div>
      <div className={"risk-badge "+level.toLowerCase()}><strong>{score}</strong><span>{level}</span></div>
    </section>

    {tab==="home" && <div className="page">
      <div className="grid cards">
       <div className="card stat"><span>{t.riskNow}</span><strong>{score}/100</strong><em>{level}</em></div>
       <div className="card stat"><span>{t.people}</span><strong>25,000</strong><em>estimate</em></div>
       <div className="card stat"><span>{t.safePeople}</span><strong>18,420</strong><em>check-ins</em></div>
       <div className="card stat"><span>{t.unconfirmed}</span><strong>6,580</strong><em>status unknown</em></div>
      </div>
      <div className="grid main-grid">
       <div className="card">
        <div className="card-head"><h2>{t.forecast}</h2><button onClick={loadRisk}>{loading?"Loading…":t.getRisk}</button></div>
        {risk?<><div className="bars">
          <div><label>Flood <b>{risk.ai_risk_forecast.flood_score}</b></label><div className="bar"><i style={{width:`${risk.ai_risk_forecast.flood_score}%`}}/></div></div>
          <div><label>Storm / wind <b>{risk.ai_risk_forecast.storm_score}</b></label><div className="bar"><i style={{width:`${risk.ai_risk_forecast.storm_score}%`}}/></div></div>
          <div><label>Earthquake signal <b>{risk.earthquake_signal.score}</b></label><div className="bar"><i style={{width:`${risk.earthquake_signal.score}%`}}/></div></div>
        </div><ul className="factors">{risk.ai_risk_forecast.factors.map((x:string)=><li key={x}>{x}</li>)}</ul>
        <p className="notice">{risk.disclaimer}</p></>:<p>Loading live weather and earthquake data…</p>}
       </div>
       <div className="card">
        <h2>WHO NEEDS HELP FIRST?</h2><div className="priority">{risk?.rescue_priority_example??"—"}<span>Priority score</span></div>
        <p>Example priority combines hazard, population exposure, vulnerability, accessibility and urgency.</p>
        <button className="primary" onClick={()=>setTab("rescue")}>Open rescue dashboard</button>
       </div>
      </div>
      <div className="card map-card"><div className="card-head"><h2>{t.map}</h2><span className="muted">{pos.lat.toFixed(4)}, {pos.lon.toFixed(4)}</span></div><Map pos={pos} reports={reports}/></div>
    </div>}

    {tab==="risk" && <div className="page"><div className="card"><h2>AI Risk Forecast</h2><p>Location: {pos.lat.toFixed(4)}, {pos.lon.toFixed(4)}</p>{risk&&<div className="risk-detail"><h3>{risk.combined_level} · {risk.combined_hazard_score}/100</h3><p>Forecast window: {risk.ai_risk_forecast.forecast_window}</p><p>Confidence: {risk.ai_risk_forecast.confidence}</p><h3>Contributing factors</h3><ul>{risk.ai_risk_forecast.factors.map((x:string)=><li key={x}>{x}</li>)}</ul><p className="notice">{risk.disclaimer}</p></div>}</div><div className="card"><h2>Recent USGS earthquakes</h2><Earthquakes/></div></div>}

    {tab==="map" && <div className="page"><div className="card map-card"><h2>Live GIS Map</h2><Map pos={pos} reports={reports} full/></div></div>}

    {tab==="rescue" && <div className="page"><div className="grid cards"><div className="card stat"><span>High priority zones</span><strong>12</strong></div><div className="card stat"><span>Teams required</span><strong>{risk?.resource_estimate.rescue_teams??"—"}</strong></div><div className="card stat"><span>Ambulances required</span><strong>{risk?.resource_estimate.ambulances??"—"}</strong></div><div className="card stat"><span>Medical teams</span><strong>{risk?.resource_estimate.medical_teams??"—"}</strong></div></div><div className="grid main-grid"><div className="card"><h2>Resource prediction</h2>{risk&&Object.entries(risk.resource_estimate).map(([k,v])=><div className="resource" key={k}><span>{k.replaceAll("_"," ")}</span><b>{String(v)}</b></div>)}</div><div className="card"><h2>Priority formula</h2><p>Hazard + Exposure + Vulnerability + Location + Real-Time Status</p><div className="priority large">{risk?.rescue_priority_example??"—"}<span>Example P1/P2 priority score</span></div></div></div></div>}

    {tab==="volunteers" && <div className="page"><div className="card"><div className="card-head"><h2>Volunteer Network</h2><button onClick={addVolunteer}>{t.register}</button></div><p>{volunteers.length} registered volunteer(s). Required vs available can be connected to live incidents.</p>{volunteers.map(v=><div className="list" key={v.id}><b>{v.name}</b><span>{v.skill}</span><span>{v.available?"AVAILABLE":"BUSY"}</span></div>)}</div></div>}

    {tab==="report" && <div className="page"><div className="card form-card"><h2>{t.reportIncident}</h2><p>Your current location: {pos.lat.toFixed(5)}, {pos.lon.toFixed(5)}</p><button className="primary" onClick={report}>Submit disaster report</button><h3>Recent reports</h3>{reports.map(r=><div className="list" key={r.id}><b>{r.disaster_type}</b><span>Severity {r.severity}/5</span><span>{r.latitude.toFixed(3)}, {r.longitude.toFixed(3)}</span></div>)}</div></div>}

    {tab==="settings" && <div className="page"><div className="card"><h2>{t.settings}</h2><p>Theme and language persist in localStorage.</p><p>Current language: <b>{lang.toUpperCase()}</b></p><p>Current theme: <b>{dark?"Dark":"Light"}</b></p><p>API: <code>{API}</code></p></div><div className="card"><h2>Emergency mode</h2><p>Use SOS, current location, safe-place guidance and emergency contacts first during an active emergency.</p><button className="sos-button" onClick={triggerSOS}>{t.sendSOS}</button>{sos&&<p className="success">{sos}</p>}</div></div>}
   </main>
  </div>
  <footer>Data: Open-Meteo weather forecasts • USGS earthquake feeds • SURAKSHA AI assessment engine • Official alerts always take priority</footer>
 </div>
}

function Map({pos,reports,full=false}:{pos:{lat:number,lon:number},reports:any[],full?:boolean}){
 return <MapContainer center={[pos.lat,pos.lon]} zoom={full?6:10} className={full?"map full":"map"} scrollWheelZoom>
   <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
   <CircleMarker center={[pos.lat,pos.lon]} radius={10}><Popup>Your current location</Popup></CircleMarker>
   {reports.map(r=><CircleMarker key={r.id} center={[r.latitude,r.longitude]} radius={8}><Popup>{r.disaster_type} · severity {r.severity}</Popup></CircleMarker>)}
 </MapContainer>
}

function Earthquakes(){
 const [data,setData]=useState<any[]>([])
 useEffect(()=>{fetch(`${API}/api/earthquakes`).then(r=>r.json()).then(x=>setData(x.features||[])).catch(()=>{})},[])
 return <div>{data.slice(0,8).map(f=><div className="list" key={f.id}><b>M{f.properties.mag?.toFixed?.(1)??f.properties.mag}</b><span>{f.properties.place}</span><span>{new Date(f.properties.time).toLocaleString()}</span></div>)}</div>
}
createRoot(document.getElementById("root")!).render(<App/>)

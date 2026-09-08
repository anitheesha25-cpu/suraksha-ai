from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from .config import settings
from .db import Base, engine, get_db
from .models import User, SOSAlert, IncidentReport, Volunteer, Resource
from .schemas import RegisterIn, SOSIn, ReportIn, VolunteerIn
from .services import get_weather, get_earthquakes, calculate_weather_risk, earthquake_risk, rescue_priority, resource_estimate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SURAKSHA AI API", version="1.0.0")
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"name":"SURAKSHA AI API","status":"online","docs":"/docs"}

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/api/users/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.phone == payload.phone))
    if user:
        for k,v in payload.model_dump().items():
            setattr(user,k,v)
    else:
        user = User(**payload.model_dump())
        db.add(user)
    db.commit(); db.refresh(user)
    return {"id":user.id, "name":user.name, "phone":user.phone}

@app.get("/api/users/{user_id}")
def get_user(user_id:int, db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,"User not found")
    return {"id":user.id,"name":user.name,"phone":user.phone,"email":user.email,"language":user.language,"latitude":user.latitude,"longitude":user.longitude}

@app.post("/api/sos")
def create_sos(payload:SOSIn, db:Session=Depends(get_db)):
    item=SOSAlert(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return {"id":item.id,"status":item.status,"created_at":item.created_at}

@app.get("/api/sos/active")
def active_sos(db:Session=Depends(get_db)):
    rows=db.scalars(select(SOSAlert).where(SOSAlert.status=="ACTIVE").order_by(SOSAlert.created_at.desc())).all()
    return [{"id":x.id,"name":x.name,"latitude":x.latitude,"longitude":x.longitude,"message":x.message,"status":x.status,"created_at":x.created_at} for x in rows]

@app.post("/api/reports")
def report(payload:ReportIn, db:Session=Depends(get_db)):
    item=IncidentReport(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item)
    return {"id":item.id,"status":"RECEIVED"}

@app.get("/api/reports")
def reports(db:Session=Depends(get_db)):
    rows=db.scalars(select(IncidentReport).order_by(IncidentReport.created_at.desc())).all()
    return [{"id":x.id,"disaster_type":x.disaster_type,"severity":x.severity,"latitude":x.latitude,"longitude":x.longitude,"description":x.description,"created_at":x.created_at} for x in rows]

@app.get("/api/weather")
async def weather(lat:float, lon:float):
    return await get_weather(lat,lon)

@app.get("/api/risk/forecast")
async def risk_forecast(lat:float, lon:float):
    weather = await get_weather(lat,lon)
    return {"location":{"latitude":lat,"longitude":lon},"assessment":calculate_weather_risk(weather),"weather":weather}

@app.get("/api/earthquakes")
async def earthquakes():
    data=await get_earthquakes()
    return {"metadata":data.get("metadata",{}),"features":data.get("features",[])}

@app.get("/api/risk/earthquake")
async def earthquake(lat:float, lon:float):
    data=await get_earthquakes()
    return earthquake_risk(lat,lon,data.get("features",[]))

@app.get("/api/risk/combined")
async def combined_risk(lat:float, lon:float, population:int=1000, vulnerability:float=40):
    weather=await get_weather(lat,lon)
    wa=calculate_weather_risk(weather)
    eq=earthquake_risk(lat,lon,(await get_earthquakes()).get("features",[]))
    hazard=max(wa["overall_score"],eq["score"])
    priority=rescue_priority(hazard,vulnerability,min(100,population/100),50,50)
    resources=resource_estimate(population, max(1, round(hazard/20)))
    return {
        "location":{"latitude":lat,"longitude":lon},
        "ai_risk_forecast":wa,
        "earthquake_signal":eq,
        "combined_hazard_score":round(hazard,1),
        "combined_level":"RED" if hazard>=70 else "YELLOW" if hazard>=40 else "GREEN",
        "rescue_priority_example":priority,
        "resource_estimate":resources,
        "disclaimer":"AI-assisted risk assessment, not a guaranteed disaster prediction. Official alerts take priority."
    }

@app.post("/api/volunteers")
def add_volunteer(payload:VolunteerIn, db:Session=Depends(get_db)):
    v=Volunteer(**payload.model_dump()); db.add(v); db.commit(); db.refresh(v)
    return {"id":v.id,"status":"REGISTERED"}

@app.get("/api/volunteers")
def volunteers(db:Session=Depends(get_db)):
    rows=db.scalars(select(Volunteer).order_by(Volunteer.id.desc())).all()
    return [{"id":v.id,"name":v.name,"skill":v.skill,"latitude":v.latitude,"longitude":v.longitude,"available":v.available} for v in rows]

@app.get("/api/resources")
def resources(db:Session=Depends(get_db)):
    rows=db.scalars(select(Resource).order_by(Resource.name)).all()
    if not rows:
        seed=[Resource(name=n,required=0,available=0) for n in ["Rescue Teams","Ambulances","Boats","Buses","Medical Teams","Water (L)","Food Meals"]]
        db.add_all(seed); db.commit(); rows=seed
    return [{"id":r.id,"name":r.name,"required":r.required,"available":r.available} for r in rows]

@app.post("/api/ai/priority")
def priority(hazard:float, vulnerability:float, exposure:float, accessibility:float=50, urgency:float=50):
    return {"priority_score":rescue_priority(hazard,vulnerability,exposure,accessibility,urgency),"formula":"Hazard + Exposure + Vulnerability + Location + Real-Time Status"}

@app.post("/api/ai/resources")
def resources_ai(affected_population:int, severity:int):
    return resource_estimate(affected_population,severity)

@app.post("/api/ocr")
async def ocr(file: UploadFile = File(...)):
    # Architecture hook: production OCR should use a real OCR provider/model.
    # We intentionally do not fabricate extracted identity information.
    return {"status":"NOT_CONFIGURED","filename":file.filename,"message":"OCR adapter is ready; connect a verified OCR service/model before extracting personal data."}

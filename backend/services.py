from math import exp, sqrt
import httpx
from .config import settings

async def get_weather(lat: float, lon: float):
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": ",".join([
            "temperature_2m","relative_humidity_2m","precipitation",
            "precipitation_probability","rain","showers","wind_speed_10m",
            "wind_gusts_10m","surface_pressure","visibility","weather_code"
        ]),
        "forecast_days": 7,
        "timezone": "auto"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(settings.open_meteo_base, params=params)
        r.raise_for_status()
        return r.json()

async def get_earthquakes():
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(settings.usgs_feed)
        r.raise_for_status()
        return r.json()

def _norm(value, low, high):
    if value <= low: return 0.0
    if value >= high: return 1.0
    return (value-low)/(high-low)

def calculate_weather_risk(weather: dict):
    h = weather.get("hourly", {})
    precip = h.get("precipitation", [])[:168]
    prob = h.get("precipitation_probability", [])[:168]
    wind = h.get("wind_gusts_10m", [])[:168]
    rain = h.get("rain", [])[:168]
    temp = h.get("temperature_2m", [])[:168]
    pressure = h.get("surface_pressure", [])[:168]

    max_hourly_rain = max(precip or [0])
    max_rain = max(rain or [0])
    max_prob = max(prob or [0])
    max_gust = max(wind or [0])
    min_pressure = min(pressure or [1013])

    # Explainable heuristic assessment, not a guaranteed prediction.
    flood = 100 * (0.55*_norm(max_hourly_rain, 10, 70) + 0.30*_norm(max_prob, 50, 95) + 0.15*_norm(max_rain, 10, 60))
    storm = 100 * (0.75*_norm(max_gust, 45, 120) + 0.25*_norm(max_prob, 60, 95))
    extreme = 100 * max(
        _norm(max_gust, 50, 120),
        _norm(max_hourly_rain, 15, 80),
        _norm(abs((max(temp or [25])[0] if False else max(temp or [25])) - 30), 8, 18)
    )
    pressure_signal = 100 * _norm(1013-min_pressure, 8, 35)
    overall = min(100, 0.45*flood + 0.40*storm + 0.15*pressure_signal)

    def level(s):
        return "RED" if s >= 70 else "YELLOW" if s >= 40 else "GREEN"

    return {
        "overall_score": round(overall, 1),
        "overall_level": level(overall),
        "flood_score": round(flood, 1),
        "storm_score": round(storm, 1),
        "extreme_weather_score": round(extreme, 1),
        "pressure_signal": round(pressure_signal, 1),
        "forecast_window": "next 7 days",
        "confidence": "Moderate" if overall >= 40 else "Low–Moderate",
        "factors": [
            f"Maximum forecast hourly precipitation: {max_hourly_rain:.1f} mm",
            f"Maximum precipitation probability: {max_prob:.0f}%",
            f"Maximum wind gust: {max_gust:.0f} km/h",
            f"Minimum forecast surface pressure: {min_pressure:.0f} hPa"
        ],
        "sources": ["Open-Meteo forecast"]
    }

def earthquake_risk(lat, lon, features):
    # Distance-weighted seismic signal from recent USGS earthquakes.
    scores = []
    nearby = []
    for f in features:
        try:
            lon2, lat2, depth = f["geometry"]["coordinates"]
            mag = f["properties"].get("mag") or 0
            dlat = (lat2-lat)*111
            dlon = (lon2-lon)*111*__import__("math").cos(__import__("math").radians(lat))
            km = sqrt(dlat*dlat + dlon*dlon)
            if km <= 800:
                signal = max(0, (mag-2.5)/4.5) * exp(-km/250) * 100
                scores.append(signal)
                nearby.append({"magnitude": mag, "place": f["properties"].get("place"), "distance_km": round(km,1), "time": f["properties"].get("time")})
        except Exception:
            continue
    score = min(100, max(scores or [0]))
    return {
        "score": round(score,1),
        "level": "RED" if score >= 70 else "YELLOW" if score >= 40 else "GREEN",
        "nearby_events": sorted(nearby, key=lambda x: x["distance_km"])[:8],
        "source": "USGS real-time earthquake GeoJSON"
    }

def rescue_priority(hazard, vulnerability, exposure, accessibility=50, urgency=50):
    score = min(100, 0.30*hazard + 0.25*vulnerability + 0.20*exposure + 0.10*(100-accessibility) + 0.15*urgency)
    return round(score, 1)

def resource_estimate(affected_population: int, severity: int):
    factor = max(0.2, min(1.0, severity/5))
    return {
        "rescue_teams": max(1, round(affected_population/80*factor)),
        "ambulances": max(1, round(affected_population/180*factor)),
        "boats": max(0, round(affected_population/250*factor)),
        "buses": max(1, round(affected_population/300*factor)),
        "medical_teams": max(1, round(affected_population/250*factor)),
        "water_liters": round(affected_population*3*factor),
        "food_meals": round(affected_population*3*factor)
    }

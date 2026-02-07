import os
from typing import Optional, Dict, Any
from fastapi import HTTPException
import httpx
from datetime import datetime

# from app.core.config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherService:

    @staticmethod
    async def get_weather(city: str, country_code: Optional[str] = None) -> Dict[str, Any]:

        if not OPENWEATHER_API_KEY:
            raise HTTPException(status_code=500, detail="API key not configured")

        location = f"{city},{country_code}" if country_code else city

        async with httpx.AsyncClient(timeout=30.0) as client:

            geo_response = await client.get(
                "http://api.openweathermap.org/geo/1.0/direct",
                params={
                    "q": location,
                    "limit": 1,
                    "appid": OPENWEATHER_API_KEY
                }
            )

            geo_data = geo_response.json()
            if not geo_data:
                raise HTTPException(status_code=404, detail=f"City '{city}' not found")

            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]

            weather_response = await client.get(
                f"{OPENWEATHER_BASE_URL}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric"
                }
            )

            data = weather_response.json()

            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "weather": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "timestamp": datetime.fromtimestamp(data["dt"]).isoformat()
            }

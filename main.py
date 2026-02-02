# main.py - Complete Weather MCP Server
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import time
import uuid
import httpx
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

app = FastAPI(
    title="Weather MCP Server",
    description="MCP server with weather tool for AWS QuickSight",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
temp_storage = {}

# Weather Service
class WeatherService:
    @staticmethod
    async def get_weather(city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        """Get current weather for a city"""
        if not OPENWEATHER_API_KEY:
            raise HTTPException(status_code=500, detail="OpenWeatherMap API key not configured")
        
        try:
            location = f"{city},{country_code}" if country_code else city
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get coordinates
                geo_response = await client.get(
                    "http://api.openweathermap.org/geo/1.0/direct",
                    params={"q": location, "limit": 1, "appid": OPENWEATHER_API_KEY}
                )
                
                if geo_response.status_code != 200:
                    raise HTTPException(status_code=geo_response.status_code, detail="Geocoding API error")
                
                geo_data = geo_response.json()
                if not geo_data:
                    raise HTTPException(status_code=404, detail=f"City '{city}' not found")
                
                # Get weather
                lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
                weather_response = await client.get(
                    f"{OPENWEATHER_BASE_URL}/weather",
                    params={
                        "lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY,
                        "units": "metric", "lang": "en"
                    }
                )
                
                weather_data = weather_response.json()
                
                return {
                    "city": weather_data.get("name", city),
                    "country": weather_data.get("sys", {}).get("country", ""),
                    "temperature": round(weather_data["main"]["temp"], 1),
                    "feels_like": round(weather_data["main"]["feels_like"], 1),
                    "humidity": weather_data["main"]["humidity"],
                    "weather": weather_data["weather"][0]["main"],
                    "description": weather_data["weather"][0]["description"].capitalize(),
                    "wind_speed": weather_data["wind"]["speed"],
                    "icon": f"https://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@2x.png",
                    "sunrise": datetime.fromtimestamp(weather_data["sys"]["sunrise"]).strftime('%H:%M:%S'),
                    "sunset": datetime.fromtimestamp(weather_data["sys"]["sunset"]).strftime('%H:%M:%S'),
                }
                
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# MCP Tools Endpoints
@app.post("/api/tools/list")
async def list_tools():
    tools = [
        {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name (e.g., 'London')"},
                    "country_code": {"type": "string", "description": "Optional country code", "default": ""}
                },
                "required": ["city"]
            }
        },
        {
            "name": "get_weather_forecast",
            "description": "Get weather forecast for a city",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "description": "Number of forecast days (1-5)", "default": 3}
                },
                "required": ["city"]
            }
        },
        {
            "name": "compare_weather",
            "description": "Compare weather between two cities",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "city1": {"type": "string", "description": "First city"},
                    "city2": {"type": "string", "description": "Second city"}
                },
                "required": ["city1", "city2"]
            }
        }
    ]
    return JSONResponse({"tools": tools})

@app.post("/api/tools/call")
async def call_tool(request: Request):
    try:
        data = await request.json()
        tool_name = data.get("name")
        arguments = data.get("arguments", {})
        
        weather_service = WeatherService()
        
        if tool_name == "get_weather":
            city = arguments.get("city")
            country_code = arguments.get("country_code", "")
            
            if not city:
                raise HTTPException(status_code=400, detail="City parameter is required")
            
            weather_data = await weather_service.get_weather(city, country_code)
            
            response_text = f"""
🌤️ **Weather in {weather_data['city']}, {weather_data['country']}**

**Current Conditions:**
• Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
• Weather: {weather_data['weather']} ({weather_data['description']})
• Humidity: {weather_data['humidity']}%
• Wind: {weather_data['wind_speed']} m/s

**Today:**
• Sunrise: {weather_data['sunrise']}
• Sunset: {weather_data['sunset']}
            """
            
            return JSONResponse({
                "content": [{"type": "text", "text": response_text.strip()}]
            })
        
        elif tool_name == "compare_weather":
            city1, city2 = arguments.get("city1"), arguments.get("city2")
            
            if not city1 or not city2:
                raise HTTPException(status_code=400, detail="Both cities are required")
            
            weather1 = await weather_service.get_weather(city1)
            weather2 = await weather_service.get_weather(city2)
            
            warmer_city = city1 if weather1["temperature"] > weather2["temperature"] else city2
            temp_diff = abs(weather1["temperature"] - weather2["temperature"])
            
            response_text = f"""
🌡️ **Weather Comparison**

**{city1}:**
• Temperature: {weather1['temperature']}°C
• Conditions: {weather1['weather']}
• Humidity: {weather1['humidity']}%

**{city2}:**
• Temperature: {weather2['temperature']}°C  
• Conditions: {weather2['weather']}
• Humidity: {weather2['humidity']}%

**Comparison:**
• {warmer_city} is {temp_diff:.1f}°C warmer
• Humidity difference: {abs(weather1['humidity'] - weather2['humidity'])}%
            """
            
            return JSONResponse({
                "content": [{"type": "text", "text": response_text.strip()}]
            })
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MCP SSE Endpoint
@app.get("/sse")
async def mcp_sse_endpoint(request: Request):
    async def event_generator():
        yield f"data: {json.dumps({'type': 'mcp_connected', 'server': 'Weather MCP', 'timestamp': time.time()})}\n\n"
        
        while True:
            yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
            await asyncio.sleep(30)
    
    return Response(
        content=event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# OAuth Endpoints
@app.get("/oauth/authorize")
async def oauth_authorize(
    response_type: str = "code",
    client_id: str = None,
    redirect_uri: str = None,
    state: str = None
):
    if not client_id or not redirect_uri:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    auth_code = str(uuid.uuid4())
    temp_storage[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "created_at": time.time()
    }
    
    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"
    
    return RedirectResponse(url=redirect_url)

@app.post("/oauth/token")
async def oauth_token(request: Request):
    try:
        form_data = await request.form()
        grant_type = form_data.get("grant_type")
        code = form_data.get("code")
        redirect_uri = form_data.get("redirect_uri")
        client_id = form_data.get("client_id")
        
        if grant_type != "authorization_code":
            raise HTTPException(status_code=400, detail="Unsupported grant type")
        
        if code not in temp_storage:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        code_data = temp_storage.pop(code)
        
        if code_data["client_id"] != client_id or code_data["redirect_uri"] != redirect_uri:
            raise HTTPException(status_code=400, detail="Invalid client or redirect URI")
        
        return JSONResponse({
            "access_token": f"mcp_token_{uuid.uuid4().hex}",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": f"mcp_refresh_{uuid.uuid4().hex}",
            "scope": "weather:read"
        })
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health Check
@app.get("/health")
async def health_check():
    api_status = "not_configured"
    if OPENWEATHER_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{OPENWEATHER_BASE_URL}/weather",
                    params={"q": "London", "appid": OPENWEATHER_API_KEY},
                    timeout=5.0
                )
                api_status = "working" if response.status_code == 200 else "error"
        except:
            api_status = "error"
    
    return JSONResponse({
        "status": "healthy",
        "weather_api": api_status,
        "endpoints": ["/sse", "/oauth/authorize", "/oauth/token", "/api/tools/list", "/api/tools/call", "/health"]
    })

@app.get("/")
async def root():
    return {
        "service": "Weather MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/sse",
            "oauth_authorize": "/oauth/authorize",
            "oauth_token": "/oauth/token",
            "tools": "/api/tools/list",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
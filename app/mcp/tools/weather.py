from app.mcp.server import mcp
from app.services.weather_service import WeatherService


@mcp.tool()
async def get_weather(city: str, country_code: str = "") -> str:

    weather_data = await WeatherService.get_weather(city, country_code)

    return f"""
Weather in {weather_data['city']}, {weather_data['country']}

Temperature: {weather_data['temperature']}°C
Condition: {weather_data['weather']} ({weather_data['description']})
Updated: {weather_data['timestamp']}
"""


@mcp.tool()
async def compare_weather(city1: str, city2: str) -> str:

    w1 = await WeatherService.get_weather(city1)
    w2 = await WeatherService.get_weather(city2)

    warmer = city1 if w1["temperature"] > w2["temperature"] else city2

    return f"{warmer} is warmer."

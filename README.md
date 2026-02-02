# 🌤️ Weather MCP Server

MCP server with weather tools for AWS QuickSight integration.

## Quick Start
1. Get OpenWeatherMap API key from https://openweathermap.org/api
2. Deploy to Railway: Connect this GitHub repository
3. Add environment variables in Railway dashboard

## Environment Variables
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key
- `JWT_SECRET`: Random string for token signing

## AWS QuickSight Setup
Use these URLs:
- MCP Endpoint: `https://[your-app].up.railway.app/sse`
- Token URL: `https://[your-app].up.railway.app/oauth/token`
- Auth URL: `https://[your-app].up.railway.app/oauth/authorize`

## Available Tools
1. `get_weather(city)` - Get current weather
2. `compare_weather(city1, city2)` - Compare two cities
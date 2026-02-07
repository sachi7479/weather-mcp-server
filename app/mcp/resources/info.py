import json
from app.mcp.server import mcp

@mcp.resource("info://server/weather")
def server_info() -> str:
    info = {
        "name": "Weather MCP Server",
        "description": "A server that provides weather information and forecasts.",
        "tools": ["get_weather", "get_forecast"],
        "version": "1.0.0"
    }
    return json.dumps(info, indent=2)
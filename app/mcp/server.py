import os
from dotenv import load_dotenv
load_dotenv()

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier


class SimpleAuthVerifier(JWTVerifier):
    def __init__(self):
        super().__init__(
            public_key=os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY"),
            issuer=os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER"),
            audience=os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE"),
            algorithm=os.getenv("FASTMCP_SERVER_AUTH_JWT_ALGORITHM"),
        )


# ✅ Detect Horizon environment automatically
if os.getenv("FASTMCP_CLOUD_URL"):
    # Running on Horizon → DO NOT use custom JWT
    mcp = FastMCP(name="Weather MCP Server")
else:
    # Running locally → use your JWT auth
    mcp = FastMCP(
        name="Weather MCP Server",
        auth=SimpleAuthVerifier()
    )

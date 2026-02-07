import os
from dotenv import load_dotenv
load_dotenv()

from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp import FastMCP


class SimpleAuthVerifier(JWTVerifier):

    def __init__(self):
        super().__init__(
            public_key=os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY"),
            issuer=os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER"),
            audience=os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE"),
            algorithm=os.getenv("FASTMCP_SERVER_AUTH_JWT_ALGORITHM"),
        )


mcp = FastMCP(
    name="Weather MCP Server",
    auth=SimpleAuthVerifier()
)

import os
import jwt
import sys
import time
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.mcp.server import mcp

# register tools/resources
import app.mcp.tools.weather
import app.mcp.resources.info

if __name__ == "__main__":
    # IMPORTANT: Use the SAME secret key as in server.py
    # Either use the environment variable or the hardcoded value
    secret_key = os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY", "uv-inspector-test-key-1234567890")
    
    token = jwt.encode(
        {
            "iss": os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER"),
            "aud": os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE"),
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        },
        secret_key,
        algorithm=os.getenv("FASTMCP_SERVER_AUTH_JWT_ALGORITHM")
    )
    
    print(f"\nToken for UV Inspector: {token}\n")

    mcp.run(
        transport="http",
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
    )
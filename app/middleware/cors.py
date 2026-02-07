from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

cors_middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

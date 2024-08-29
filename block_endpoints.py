# Em um arquivo separado, por exemplo, middlewares/block_endpoints.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from state import is_updating_database

class BlockEndpointsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_updating_database:
            raise HTTPException(status_code=503, detail="Service Unavailable: Database update in progress")
        response = await call_next(request)
        return response
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class BlockEndpointsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.app.state.is_updating_database:
            raise HTTPException(status_code=503, detail="Service Unavailable: Database update in progress")
        response = await call_next(request)
        return response

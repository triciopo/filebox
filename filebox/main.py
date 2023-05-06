from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from filebox.core.config import settings
from filebox.routers.api import router


class LimitUploadSize(BaseHTTPMiddleware):
    """https://github.com/tiangolo/fastapi/discussions/8167"""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.max_size: int = settings.SIZE_LIMIT

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method == "POST":
            if "content-length" not in request.headers:
                return Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
            content_length = int(request.headers["content-length"])
            if content_length > self.max_size:
                return Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        return await call_next(request)


app = FastAPI(
    title="filebox",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LimitUploadSize)

app.include_router(router, prefix=settings.API_PREFIX, tags=["files"])

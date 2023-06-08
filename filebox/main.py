from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from filebox.core.config import settings
from filebox.core.database import Base, engine
from filebox.rate_limiter import limiter
from filebox.routers.auth import auth_router
from filebox.routers.files import file_router
from filebox.routers.folders import folder_router
from filebox.routers.users import user_router


class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.max_size: int = settings.SIZE_LIMIT

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_size:
                return Response(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content="File too large",
                )
        return await call_next(request)


app = FastAPI(title="filebox", docs_url=settings.DOCS_URL, redoc_url=settings.REDOC_URL)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LimitUploadSize)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(file_router, prefix=settings.API_PREFIX, tags=["files"])
app.include_router(folder_router, prefix=settings.API_PREFIX, tags=["folders"])
app.include_router(user_router, prefix=settings.API_PREFIX, tags=["users"])
app.include_router(auth_router, prefix=settings.API_PREFIX, tags=["auth"])


@app.on_event("startup")
async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

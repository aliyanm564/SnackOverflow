import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.application.exceptions import (
    AppError, AuthenticationError, AuthorizationError,
    BusinessRuleError, ConflictError, NotFoundError, PaymentError,
)
from backend.app.infrastructure.database import init_db, seed_from_csv
from backend.app.presentation.routers.auth_router import router as auth_router
from backend.app.presentation.routers.order_router import router as order_router
from backend.app.presentation.routers.notification_router import router as notification_router
from backend.app.presentation.routers.user_router import router as user_router
from backend.app.presentation.routers.restaurant_router import router as restaurant_router

from backend.app.presentation.routers.delivery_router import router as delivery_router
from backend.app.presentation.routers.payment_router import router as payment_router

_CSV_PATH = os.getenv("CSV_PATH", "backend/data/food_delivery.csv")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if os.path.exists(_CSV_PATH):
        seed_from_csv(_CSV_PATH)
    yield

app = FastAPI(
    title="SnackOverflow",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATUS_MAP = {
    NotFoundError:       404,
    ConflictError:       409,
    AuthenticationError: 401,
    AuthorizationError:  403,
    BusinessRuleError:   422,
    PaymentError:        402,
}

@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    status_code = _STATUS_MAP.get(type(exc), 400)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})

API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(order_router, prefix=API_PREFIX)
app.include_router(notification_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(restaurant_router, prefix=API_PREFIX)

app.include_router(delivery_router, prefix=API_PREFIX)
app.include_router(payment_router, prefix=API_PREFIX)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

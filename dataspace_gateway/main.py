from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dataspace_gateway.config import settings
from dataspace_gateway.routers import auth, data, offerings, subscriptions

app = FastAPI(
    title="EnergyGuard Data Space Gateway",
    description=(
        "FastAPI gateway over the EnPower / True Connector Data Space APIs, covering "
        "the full Data Provide and Data Consume workflows: authentication, Data Offering "
        "management, subscriptions, and data provide/consume."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(offerings.router)
app.include_router(subscriptions.router)
app.include_router(data.router)


@app.get("/health", tags=["Health"], summary="Liveness check")
def health() -> dict:
    return {"status": "ok"}

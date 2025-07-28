from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import portfolio, health

app = FastAPI(
    title="Quantum Portfolio Optimizer",
    description="API for your unmodified VQE implementation",
    version="1.0.0"
)

# CORS Setup (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(health.router)
app.include_router(portfolio.router, prefix="/api/v1")
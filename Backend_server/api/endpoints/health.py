from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "active",
        "cache_ready": True  # Add actual cache verification if needed
    }
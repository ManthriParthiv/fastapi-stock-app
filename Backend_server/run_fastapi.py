import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.fastapi_adapter:app",  
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
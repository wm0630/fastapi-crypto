from fastapi import FastAPI
from app.api.endpoints import items

app = FastAPI()

# Include routers
app.include_router(items.router, prefix="/api/endpoints/items", tags=["items"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

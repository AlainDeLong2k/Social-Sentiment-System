from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import analysis

app = FastAPI(
    title="Sentiment Analysis API",
    description="API for analyzing sentiment of trending topics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(analysis.router, prefix=f"{settings.API_PREFIX}{settings.API_VERSION}", tags=["Analysis"])


@app.get("/", tags=["Root"])
def read_root() -> dict:
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Sentiment Analysis API"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)

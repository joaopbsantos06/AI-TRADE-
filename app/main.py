from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI Trade Research",
    description="Experimental paper-trading-only research API.",
)
app.include_router(router)

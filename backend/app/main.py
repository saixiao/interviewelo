from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.approach.router import router as approach_router
from app.auth.router import router as auth_router
from app.config import get_settings
from app.quiz.router import router as quiz_router
from app.stats.router import router as stats_router
from app.typing.router import router as typing_router

settings = get_settings()

app = FastAPI(title="InterviewElo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(typing_router)
app.include_router(approach_router)
app.include_router(quiz_router)
app.include_router(stats_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

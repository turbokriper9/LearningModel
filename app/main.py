from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 Импортируй CORS

from app.api.v1.endpoints import detect, health
from app.core.database import init_db

app = FastAPI()

# 👇 Добавь CORS middleware сразу после app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 👈 Разрешаем запросы с фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(health.router, prefix="/api/v1")
app.include_router(detect.router, prefix="/api/v1")
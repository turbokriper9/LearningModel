from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import detect, health
from app.api.v1.endpoints import attendance_routes      # <-- добавь это!
from app.core.database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(health.router, prefix="/api/v1")
app.include_router(detect.router, prefix="/api/v1")
app.include_router(attendance_routes.router, prefix="/api/v1")  # <-- добавь это!
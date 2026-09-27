import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(backend_dir)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from fastapi import FastAPI
try:
    from routes.migration import router
except ModuleNotFoundError:
    from backend.routes.migration import router
from fastapi.middleware.cors import CORSMiddleware

try:
    import scheduler
except ModuleNotFoundError:
    from backend import scheduler

app = FastAPI(
    title="DB Migration Tool",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router,
    prefix="/migration",
    tags=["Migration"]
)

@app.get("/")
def home():

    return {
        "message": "DB Migration Tool API Running"
    }
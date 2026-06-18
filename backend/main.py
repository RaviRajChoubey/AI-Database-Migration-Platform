import sys
import os

sys.path.append(
    os.path.abspath("..")
)

from fastapi import FastAPI
from routes.migration import router
from fastapi.middleware.cors import CORSMiddleware

import scheduler

app = FastAPI(
    title="DB Migration Tool",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
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
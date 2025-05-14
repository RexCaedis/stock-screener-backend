from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import get_filtered_stocks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stocks")
def read_stocks():
    return get_filtered_stocks()

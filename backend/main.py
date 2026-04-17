from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import router
from database.db import init_db

load_dotenv()

app = FastAPI(title="ATM Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def home():
    return {"message": "ATM Fraud Detection System Running"}
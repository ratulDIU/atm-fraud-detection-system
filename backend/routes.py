from fastapi import APIRouter
from fraud_service import analyze_transaction

router = APIRouter()

@router.post("/analyze")
def analyze(data: dict):
    result = analyze_transaction(data)
    return result
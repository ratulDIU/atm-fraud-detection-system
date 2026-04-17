from fastapi import APIRouter
from fraud_service import analyze_transaction
from database.db import (
    create_user, verify_email_code, resend_verification_code, set_password, authenticate_user,
    get_user_by_email
)

router = APIRouter()

@router.post("/analyze")
def analyze(data: dict):
    result = analyze_transaction(data)
    return result

# Authentication Routes
@router.post("/register")
def register(data: dict):
    account_number = data.get("account_number")
    card_holder_name = data.get("card_holder_name")
    email = data.get("email")

    if not all([account_number, card_holder_name, email]):
        return {"success": False, "message": "All fields are required"}

    try:
        account_number = int(account_number)
    except:
        return {"success": False, "message": "Invalid account number"}

    result = create_user(account_number, card_holder_name.strip(), email.strip())
    return result

@router.post("/verify-email")
def verify_email_endpoint(data: dict):
    user_id = data.get("user_id")
    verification_code = data.get("verification_code")

    if not all([user_id, verification_code]):
        return {"success": False, "message": "User ID and verification code are required"}

    try:
        user_id = int(user_id)
    except:
        return {"success": False, "message": "Invalid user ID"}

    result = verify_email_code(user_id, verification_code.strip())
    return result

@router.post("/resend-verification")
def resend_verification_endpoint(data: dict):
    user_id = data.get("user_id")

    if not user_id:
        return {"success": False, "message": "User ID is required"}

    try:
        user_id = int(user_id)
    except:
        return {"success": False, "message": "Invalid user ID"}

    result = resend_verification_code(user_id)
    return result

@router.post("/set-password")
def set_password_endpoint(data: dict):
    user_id = data.get("user_id")
    password = data.get("password")

    if not all([user_id, password]):
        return {"success": False, "message": "User ID and password are required"}

    try:
        user_id = int(user_id)
    except:
        return {"success": False, "message": "Invalid user ID"}

    result = set_password(user_id, password.strip())
    return result

@router.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return {"success": False, "message": "Email and password are required"}

    result = authenticate_user(email.strip().lower(), password.strip())
    return result

@router.post("/check-email")
def check_email(data: dict):
    email = data.get("email")

    if not email:
        return {"success": False, "message": "Email is required"}

    user = get_user_by_email(email.strip().lower())
    if user:
        return {"success": True, "exists": True}
    else:
        return {"success": True, "exists": False}
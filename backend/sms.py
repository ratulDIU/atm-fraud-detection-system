import os

SMS_PROVIDER = os.getenv("SMS_PROVIDER", "").strip().lower()
DEBUG_OTP = os.getenv("DEBUG_OTP", "0").strip() == "1"


def send_sms_via_twilio(to_number: str, message: str) -> dict:
    try:
        from twilio.rest import Client
    except ImportError:
        return {"success": False, "message": "Twilio package is not installed."}

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        return {"success": False, "message": "Twilio credentials are not configured."}

    try:
        client = Client(account_sid, auth_token)
        message_obj = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number,
        )
        return {"success": True, "message": "SMS sent successfully.", "sid": message_obj.sid}
    except Exception as exc:
        return {"success": False, "message": f"SMS send failed: {str(exc)}"}


def send_sms(to_number: str, message: str) -> dict:
    if SMS_PROVIDER == "twilio":
        return send_sms_via_twilio(to_number, message)

    return {"success": False, "message": "No SMS provider configured. Set SMS_PROVIDER=twilio."}

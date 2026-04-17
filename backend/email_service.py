import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_verification_email(to_email: str, verification_code: str) -> dict:
    """Send verification code via email."""
    
    email_provider = os.getenv("EMAIL_PROVIDER", "gmail").strip().lower()
    
    if email_provider == "gmail":
        return send_via_gmail(to_email, verification_code)
    elif email_provider == "debug":
        print(f"DEBUG EMAIL to {to_email}: Verification Code = {verification_code}")
        return {"success": True, "message": "Email sent (debug mode)"}
    else:
        return {"success": False, "message": f"Unsupported email provider: {email_provider}"}


def send_via_gmail(to_email: str, verification_code: str) -> dict:
    """Send email using Gmail SMTP."""
    
    sender_email = os.getenv("GMAIL_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not sender_email or not sender_password:
        return {"success": False, "message": "Gmail credentials not configured"}
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "ATM Fraud Detection - Email Verification"
        message["From"] = sender_email
        message["To"] = to_email
        
        # HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; border-radius: 10px;">
                    <h2 style="color: #4f46e5; text-align: center;">ATM Fraud Detection System</h2>
                    <p style="font-size: 16px; color: #333;">Hi there,</p>
                    <p style="font-size: 16px; color: #333;">Your email verification code is:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <h1 style="font-size: 48px; color: #4f46e5; letter-spacing: 10px; margin: 0;">{verification_code}</h1>
                    </div>
                    <p style="font-size: 14px; color: #666;">This code will expire in 10 minutes.</p>
                    <p style="font-size: 14px; color: #666;">If you did not request this code, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center;">© 2026 ATM Fraud Detection System. All rights reserved.</p>
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html_body, "html")
        message.attach(part)
        
        # Connect to Gmail and send
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        
        return {"success": True, "message": "Verification email sent successfully"}
    
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time
import hashlib
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from typing import Optional
from email.header import Header
from email.utils import formataddr

load_dotenv()

app = FastAPI(title="ESG Report Authentication API", version="1.0.0")
security = HTTPBearer()

# Allow frontend to call - updated for better compatibility
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:3001",  # Alternative React port
    "http://127.0.0.1:3000", # Alternative localhost
    "http://127.0.0.1:3001", # Alternative localhost
    "https://esgreport-alpha.vercel.app",  # Production domain
    "https://esg.parksonspackaging.com"  # ESG domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Storage (in production, use Redis or database)
otp_store = {}  # {email: {"code": "123456", "expires": 1234567890, "attempts": 0}}
rate_limit_store = {}  # {email: {"last_request": 1234567890, "count": 0}}
user_sessions = {}  # {email: {"token": "jwt_token", "expires": 1234567890}}

class EmailRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class RefreshTokenRequest(BaseModel):
    email: EmailStr

# SMTP config
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.PyJWTError:
        return None

def check_rate_limit(email: str):
    """Rate limiting: max 3 OTP requests per 15 minutes"""
    current_time = time.time()
    if email in rate_limit_store:
        last_request = rate_limit_store[email]["last_request"]
        count = rate_limit_store[email]["count"]
        
        # Reset counter if 15 minutes have passed
        if current_time - last_request > 900:  # 15 minutes
            rate_limit_store[email] = {"last_request": current_time, "count": 1}
            return True
        
        # Check if limit exceeded
        if count >= 3:
            return False
        
        # Increment counter
        rate_limit_store[email]["count"] += 1
        rate_limit_store[email]["last_request"] = current_time
    else:
        rate_limit_store[email] = {"last_request": current_time, "count": 1}
    
    return True

def create_email_template(otp: str, user_name: str = None):
    """Create a professional email template"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESG Report Access - OTP Verification</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #01507d, #14577d); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .otp-box {{ background: #01507d; color: white; padding: 20px; text-align: center; border-radius: 6px; margin: 20px 0; font-size: 24px; font-weight: bold; letter-spacing: 3px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Parksons Packaging</h1>
                <p>ESG Report Access Verification</p>
            </div>
            <div class="content">
                <p>Hello{f" {user_name}" if user_name else ""},</p>
                
                <p>Thank you for requesting access to our ESG Report. To complete your verification, please use the following One-Time Password (OTP):</p>
                
                <div class="otp-box">
                    {otp}
                </div>
                
                <p><strong>Important Notes:</strong></p>
                <ul>
                    <li>This OTP is valid for 5 minutes only</li>
                    <li>Do not share this OTP with anyone</li>
                    <li>If you didn't request this access, please ignore this email</li>
                </ul>
                
                <div class="warning">
                    <strong>Security Notice:</strong> Parksons Packaging will never ask for your password or personal information via email.
                </div>
                
                <p>Best regards,<br>
                <strong>Parksons Packaging Team</strong></p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>&copy; 2024 Parksons Packaging. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(to_email: str, otp: str, user_name: str = None):
    """Send OTP email with professional template"""
    html_content = create_email_template(otp, user_name)
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "ESG Report Access - OTP Verification"
    msg['From'] = formataddr((str(Header("Parksons Packaging", 'utf-8')), SMTP_USER))
    msg['To'] = to_email
    
    # Add HTML content
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # Add plain text fallback
    text_content = f"""
    ESG Report Access - OTP Verification
    
    Your OTP is: {otp}
    
    This OTP is valid for 5 minutes only.
    Do not share this OTP with anyone.
    
    Best regards,
    Parksons Packaging Team
    """
    text_part = MIMEText(text_content, 'plain', 'utf-8')
    msg.attach(text_part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def generate_otp():
    """Generate a secure 6-digit OTP"""
    return str(random.randint(100000, 999999))

# Send OTP endpoint
@app.post("/send-otp")
def send_otp(request: EmailRequest):
    """Send OTP to user's email"""
    
    # Check rate limiting
    if not check_rate_limit(request.email):
        raise HTTPException(
            status_code=429, 
            detail="Too many OTP requests. Please wait 15 minutes before trying again."
        )
    
    # Generate OTP
    otp = generate_otp()
    otp_store[request.email] = {
        "code": otp, 
        "expires": time.time() + 300,  # 5 minutes
        "attempts": 0,
        "user_name": request.name,
        "company": request.company
    }
    
    # Send email
    if send_email(request.email, otp, request.name):
        return {
            "success": True, 
            "message": "OTP sent successfully",
            "expires_in": 300
        }
    else:
        # Remove OTP if email fails
        if request.email in otp_store:
            del otp_store[request.email]
        raise HTTPException(status_code=500, detail="Failed to send email")

# Verify OTP endpoint
@app.post("/verify-otp")
def verify_otp(request: VerifyRequest):
    """Verify OTP and return access token"""
    
    record = otp_store.get(request.email)
    if not record:
        raise HTTPException(status_code=400, detail="No OTP sent for this email")
    
    # Check expiration
    if time.time() > record["expires"]:
        del otp_store[request.email]
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # Check attempts (max 3 attempts)
    if record["attempts"] >= 3:
        del otp_store[request.email]
        raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new OTP.")
    
    # Increment attempts
    record["attempts"] += 1
    
    # Verify OTP
    if request.otp != record["code"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": request.email, "name": record.get("user_name"), "company": record.get("company")}
    )
    
    # Store user session
    user_sessions[request.email] = {
        "token": access_token,
        "expires": time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    }
    
    # Clean up OTP
    del otp_store[request.email]
    
    return {
        "success": True,
        "message": "OTP verified successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_data": {
            "email": request.email,
            "name": record.get("user_name"),
            "company": record.get("company")
        }
    }

# Verify token endpoint
@app.post("/verify-token")
def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if the access token is valid"""
    email = verify_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check if session exists
    if email not in user_sessions:
        raise HTTPException(status_code=401, detail="Session not found")
    
    session = user_sessions[email]
    if time.time() > session["expires"]:
        del user_sessions[email]
        raise HTTPException(status_code=401, detail="Session expired")
    
    return {
        "success": True,
        "message": "Token is valid",
        "user_data": {
            "email": email
        }
    }

# Refresh token endpoint
@app.post("/refresh-token")
def refresh_token(request: RefreshTokenRequest):
    """Refresh the access token"""
    if request.email not in user_sessions:
        raise HTTPException(status_code=401, detail="No active session found")
    
    session = user_sessions[request.email]
    if time.time() > session["expires"]:
        del user_sessions[request.email]
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Generate new token
    access_token = create_access_token(
        data={"sub": request.email}
    )
    
    # Update session
    user_sessions[request.email] = {
        "token": access_token,
        "expires": time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    }
    
    return {
        "success": True,
        "message": "Token refreshed successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# Logout endpoint
@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout and invalidate session"""
    email = verify_token(credentials.credentials)
    if email and email in user_sessions:
        del user_sessions[email]
    
    return {"success": True, "message": "Logged out successfully"}

# Health check endpoint
@app.get("/")
def health_check():
    return {
        "status": "healthy", 
        "message": "ESG Report Authentication API is running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# API info endpoint
@app.get("/api-info")
def api_info():
    return {
        "name": "ESG Report Authentication API",
        "version": "1.0.0",
        "description": "Email-based OTP authentication system for ESG Report access",
        "endpoints": {
            "send_otp": "POST /send-otp",
            "verify_otp": "POST /verify-otp",
            "verify_token": "POST /verify-token",
            "refresh_token": "POST /refresh-token",
            "logout": "POST /logout"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

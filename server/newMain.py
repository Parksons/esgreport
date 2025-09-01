from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import random
import time
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json
import base64
from typing import Optional

# Google API
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

app = FastAPI(title="ESG Report Authentication API", version="2.0.0")
security = HTTPBearer()

# Allow frontend to call
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://esgreport-alpha.vercel.app",
    "https://esg.parksonspackaging.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Config
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Storage
otp_store = {}
rate_limit_store = {}
user_sessions = {}

# Gmail API Setup
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
SENDER_EMAIL = os.getenv("SMTP_USER")  # your Gmail ID

def get_gmail_service():
    creds_data = os.getenv("GMAIL_TOKEN")
    if not creds_data:
        raise RuntimeError("❌ GMAIL_TOKEN env variable not set")

    creds = Credentials.from_authorized_user_info(json.loads(creds_data), SCOPES)
    return build("gmail", "v1", credentials=creds)


# Models
class EmailRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class RefreshTokenRequest(BaseModel):
    email: EmailStr


# Helpers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None

def check_rate_limit(email: str):
    current_time = time.time()
    if email in rate_limit_store:
        last_request = rate_limit_store[email]["last_request"]
        count = rate_limit_store[email]["count"]
        if current_time - last_request > 900:
            rate_limit_store[email] = {"last_request": current_time, "count": 1}
            return True
        if count >= 3:
            return False
        rate_limit_store[email]["count"] += 1
        rate_limit_store[email]["last_request"] = current_time
    else:
        rate_limit_store[email] = {"last_request": current_time, "count": 1}
    return True


# Email template
def create_email_template(otp: str, user_name: str = None):
    return f"""
    <html>
    <body>
        <h2>ESG Report Access Verification</h2>
        <p>Hello{f" {user_name}" if user_name else ""},</p>
        <p>Your OTP is:</p>
        <h1>{otp}</h1>
        <p>This OTP is valid for 5 minutes.</p>
    </body>
    </html>
    """

def send_email(to_email: str, otp: str, user_name: str = None):
    service = get_gmail_service()
    html_content = create_email_template(otp, user_name)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "ESG Report Access - OTP Verification"
    msg["From"] = formataddr((str(Header("Parksons Packaging", "utf-8")), SENDER_EMAIL))
    msg["To"] = to_email

    # Attach text + html
    text_content = f"Your OTP is {otp}. Valid for 5 minutes."
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    try:
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


# OTP
def generate_otp():
    return str(random.randint(100000, 999999))


# Endpoints
@app.post("/send-otp")
def send_otp(request: EmailRequest):
    if not check_rate_limit(request.email):
        raise HTTPException(status_code=429, detail="Too many OTP requests. Try again later.")

    otp = generate_otp()
    otp_store[request.email] = {
        "code": otp,
        "expires": time.time() + 300,
        "attempts": 0,
        "user_name": request.name,
        "company": request.company
    }

    if send_email(request.email, otp, request.name):
        return {"success": True, "message": "OTP sent", "expires_in": 300}
    else:
        otp_store.pop(request.email, None)
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.post("/verify-otp")
def verify_otp(request: VerifyRequest):
    record = otp_store.get(request.email)
    if not record:
        raise HTTPException(status_code=400, detail="No OTP sent")

    if time.time() > record["expires"]:
        otp_store.pop(request.email, None)
        raise HTTPException(status_code=400, detail="OTP expired")

    if record["attempts"] >= 3:
        otp_store.pop(request.email, None)
        raise HTTPException(status_code=400, detail="Too many failed attempts")

    record["attempts"] += 1
    if request.otp != record["code"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    token = create_access_token(
        {"sub": request.email, "name": record.get("user_name"), "company": record.get("company")}
    )
    user_sessions[request.email] = {"token": token, "expires": time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)}
    otp_store.pop(request.email, None)

    return {
        "success": True,
        "message": "OTP verified",
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/verify-token")
def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = verify_token(credentials.credentials)
    if not email or email not in user_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    session = user_sessions[email]
    if time.time() > session["expires"]:
        user_sessions.pop(email, None)
        raise HTTPException(status_code=401, detail="Session expired")

    return {"success": True, "message": "Token is valid", "user_data": {"email": email}}

@app.post("/refresh-token")
def refresh_token(request: RefreshTokenRequest):
    if request.email not in user_sessions:
        raise HTTPException(status_code=401, detail="No active session")

    session = user_sessions[request.email]
    if time.time() > session["expires"]:
        user_sessions.pop(request.email, None)
        raise HTTPException(status_code=401, detail="Session expired")

    token = create_access_token({"sub": request.email})
    user_sessions[request.email] = {"token": token, "expires": time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)}

    return {"success": True, "message": "Token refreshed", "access_token": token}

@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = verify_token(credentials.credentials)
    if email in user_sessions:
        user_sessions.pop(email, None)
    return {"success": True, "message": "Logged out"}

@app.get("/")
def health_check():
    return {"status": "healthy", "message": "API running", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat()}

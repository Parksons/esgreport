from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
import random
import time
from dotenv import load_dotenv
import os
app = FastAPI()

# Allow frontend to call - updated for better compatibility
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:3001",  # Alternative React port
    "http://127.0.0.1:3000", # Alternative localhost
    "http://127.0.0.1:3001", # Alternative localhost
    "https://yourfrontenddomain.com"  # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# OTP storage (for demo, in-memory)
otp_store = {}  # {email: {"code": "123456", "expires": 1234567890}}

class EmailRequest(BaseModel):
    email: str  # Changed from EmailStr to str for better compatibility

class VerifyRequest(BaseModel):
    email: str  # Changed from EmailStr to str for better compatibility
    otp: str

# SMTP config
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587  # or 465 for SSL
SMTP_USER = "b24350@students.iitmandi.ac.in"
SMTP_PASS = os.getenv("SMTP_PASS")

def send_email(to_email: str, otp: str):
    msg = MIMEText(f"Your OTP is {otp}. It expires in 5 minutes.", "html")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())

def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP
@app.post("/send-otp")
def send_otp(request: EmailRequest):
    # Basic email validation
    if '@' not in request.email or '.' not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    otp = generate_otp()
    otp_store[request.email] = {"code": otp, "expires": time.time() + 300}  # 5 min
    
    try:
        send_email(request.email, otp)
        return {"success": True, "message": "OTP sent successfully"}
    except Exception as e:
        # Remove the OTP if email fails
        if request.email in otp_store:
            del otp_store[request.email]
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Verify OTP
@app.post("/verify-otp")
def verify_otp(request: VerifyRequest):
    record = otp_store.get(request.email)
    if not record:
        raise HTTPException(status_code=400, detail="No OTP sent for this email")
    
    if time.time() > record["expires"]:
        del otp_store[request.email]
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    if request.otp != record["code"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Clean up after successful verification
    del otp_store[request.email]
    return {"success": True, "message": "OTP verified successfully"}

# Health check endpoint
@app.get("/")
def health_check():
    return {"status": "healthy", "message": "OTP Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



#!/usr/bin/env python3
"""
FastAPI OTP Server Startup Script
Run this to start the OTP verification server
"""

import uvicorn
import sys
import os

def main():
    try:
        print("🚀 Starting FastAPI OTP Server...")
        print("📍 Server will run on: http://localhost:8000")
        print("🔗 API Endpoints:")
        print("   - POST /send-otp - Send OTP to email")
        print("   - POST /verify-otp - Verify OTP")
        print("   - GET / - Health check")
        print("\n📧 Make sure your SMTP credentials are configured in main.py")
        print("🌐 Frontend should be running on: http://localhost:3000")
        print("\n" + "="*50)
        
        # Start the server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload on code changes
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Make sure you have all required packages installed:")
        print("   pip install fastapi uvicorn pydantic")
        sys.exit(1)

if __name__ == "__main__":
    main()

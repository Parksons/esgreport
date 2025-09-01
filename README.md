# ESG Report - OTP Verification System

A secure ESG (Environmental, Social & Governance) report viewer with email-based OTP verification system.

## Features

- **Secure Access Control**: Email-based OTP verification
- **Modern UI**: React-based frontend with responsive design
- **Backend API**: FastAPI server with JWT token authentication
- **Email Integration**: Gmail API for sending OTP emails
- **Session Management**: Automatic session timeout and token verification
- **Gallery View**: Image gallery with access control

## Project Structure

```
esgreport/
├── server/                 # Backend API
│   ├── newMain.py         # FastAPI server with OTP logic
│   ├── start_server.py    # Server startup script
│   └── requirements.txt   # Python dependencies
├── src/                   # React frontend
│   ├── components/        # React components
│   │   ├── AccessForm.js  # OTP verification form
│   │   ├── Header.js      # Navigation header
│   │   └── ImageGallery.js # Gallery with access control
│   ├── context/           # React context
│   │   └── SecurityContext.js # Authentication state management
│   └── pages/             # Page components
└── public/                # Static assets
```

## Setup Instructions

### Backend Setup

1. **Navigate to server directory:**
   ```bash
   cd server
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the server directory with:
   ```env
   JWT_SECRET=your-secret-key-change-in-production
   SMTP_USER=your-gmail@gmail.com
   GMAIL_TOKEN={"your":"gmail-api-token-json"}
   ```

4. **Start the backend server:**
   ```bash
   python start_server.py
   ```
   The server will run on `http://localhost:8000`

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

## API Endpoints

### Authentication Endpoints

- `POST /send-otp` - Send OTP to email
  - Body: `{"email": "user@example.com", "name": "User Name", "company": "Company Name"}`
  - Response: `{"success": true, "message": "OTP sent", "expires_in": 300}`

- `POST /verify-otp` - Verify OTP and get access token
  - Body: `{"email": "user@example.com", "otp": "123456"}`
  - Response: `{"success": true, "message": "OTP verified", "access_token": "jwt_token", "token_type": "bearer", "expires_in": 1800}`

- `POST /verify-token` - Verify JWT token
  - Headers: `Authorization: Bearer <token>`
  - Response: `{"success": true, "message": "Token is valid", "user_data": {"email": "user@example.com"}}`

- `POST /logout` - Logout and invalidate session
  - Headers: `Authorization: Bearer <token>`
  - Response: `{"success": true, "message": "Logged out"}`

- `GET /` - Health check
  - Response: `{"status": "healthy", "message": "API running", "version": "2.0.0"}`

## How It Works

### OTP Verification Flow

1. **User Access Request**: User fills out the access form with name, company, email, and contact number
2. **OTP Generation**: Backend generates a 6-digit OTP and sends it via email
3. **OTP Verification**: User enters the OTP received in email
4. **Token Generation**: Upon successful verification, backend generates a JWT token
5. **Access Granted**: Frontend stores the token and grants access to the full gallery

### Security Features

- **Rate Limiting**: Maximum 3 OTP requests per email per 15 minutes
- **OTP Expiration**: OTPs expire after 5 minutes
- **Attempt Limiting**: Maximum 3 failed OTP attempts
- **Session Timeout**: JWT tokens expire after 30 minutes
- **Token Verification**: Frontend verifies tokens with backend on app startup

### Email Configuration

The system uses Gmail API for sending OTP emails. You need to:

1. Set up a Google Cloud Project
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Generate a Gmail token and store it in the `GMAIL_TOKEN` environment variable

## Development

### Backend Development

- **Auto-reload**: The server automatically reloads on code changes
- **CORS**: Configured to allow frontend requests from localhost and production domains
- **Error Handling**: Comprehensive error handling with proper HTTP status codes

### Frontend Development

- **React Context**: Uses SecurityContext for global authentication state
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: User-friendly error messages for failed requests

## Production Deployment

### Backend Deployment

The backend is configured for deployment on Railway with:
- Environment variables for production settings
- CORS configuration for production domains
- Health check endpoint for monitoring

### Frontend Deployment

The frontend can be deployed to Vercel, Netlify, or any static hosting service.

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the frontend URL is in the `origins` list in `newMain.py`
2. **Email Not Sending**: Check Gmail API credentials and token
3. **OTP Not Received**: Check spam folder and email configuration
4. **Token Expired**: User needs to re-authenticate after 30 minutes

### Debug Mode

Enable debug logging by setting the log level in `start_server.py`:
```python
log_level="debug"
```

## License

This project is proprietary software for Parksons Packaging.

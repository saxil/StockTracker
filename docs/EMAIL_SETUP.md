# Email Setup Instructions for Stock Analysis Tool

## Step 1: Enable 2-Factor Authentication on Gmail
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", enable "2-Step Verification"

## Step 2: Generate an App Password
1. Still in Security settings, find "App passwords" 
2. Click "App passwords" (you may need to sign in again)
3. Select "Mail" as the app
4. Select "Windows Computer" as the device
5. Click "Generate"
6. Copy the 16-character password (something like: abcd efgh ijkl mnop)

## Step 3: Set Environment Variables in Windows
Open PowerShell as Administrator and run:

```powershell
# Set your Gmail email
[Environment]::SetEnvironmentVariable("GMAIL_EMAIL", "your-email@gmail.com", "User")

# Set your Gmail app password (remove spaces)
[Environment]::SetEnvironmentVariable("GMAIL_APP_PASSWORD", "abcdefghijklmnop", "User")
```

Replace:
- "your-email@gmail.com" with your actual Gmail address
- "abcdefghijklmnop" with your actual 16-character app password (no spaces)

## Step 4: Restart your application
Close the terminal and restart Streamlit for the environment variables to take effect.

## Alternative: Use .env file (for development)
Create a .env file in your project directory:
```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

Then install python-dotenv and modify email_service.py to load from .env file.

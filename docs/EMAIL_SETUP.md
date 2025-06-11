# Email Setup Instructions (Optional)

The Stock Tracker application can send email notifications for price alerts. **Email setup is completely optional** - the app works perfectly without it.

## Quick Setup for Gmail

If you want to receive email alerts, follow these steps:

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to [Google Account settings](https://myaccount.google.com/)
2. Click "Security" → Enable "2-Step Verification"

### Step 2: Generate an App Password
1. In Security settings, find "App passwords"
2. Select "Mail" and "Windows Computer"
3. Copy the 16-character password (e.g., `abcdefghijklmnop`)

### Step 3: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:EMAIL_ADDRESS="your-email@gmail.com"
$env:EMAIL_PASSWORD="your-16-char-app-password"
```

**Alternative: Create `.env` file**
```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop
```

### Step 4: Restart the Application
Close and restart Streamlit for changes to take effect.

## Important Notes

- **Email is optional** - all core features work without email setup
- Only needed for price alert notifications
- Uses secure Gmail SMTP (no API keys required)
- App will show "Email not configured" if not set up

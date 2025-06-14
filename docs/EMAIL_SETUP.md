# Email Service Configuration

The application can send email notifications for alerts and other events. To enable this, you need to configure an SMTP server.

## Required Environment Variables

The Email Service uses the following environment variables for its configuration:

*   `SMTP_HOST`: The hostname or IP address of your SMTP server (e.g., `smtp.gmail.com`).
*   `SMTP_PORT`: The port number for the SMTP server (e.g., `587` for TLS, `465` for SSL). The service currently defaults to 587 and attempts STARTTLS.
*   `SMTP_USER`: The username for authenticating with the SMTP server (usually your full email address).
*   `SMTP_PASSWORD`: The password for authenticating with the SMTP server. For services like Gmail, this will likely be an "App Password".
*   `SENDER_EMAIL`: The email address that will appear as the sender (e.g., `your-email@example.com`). This should typically match the `SMTP_USER` or be an authorized sender for that account.

## Configuration Methods

You can set these environment variables in several ways depending on your deployment:

*   **Local Development (using `.env` file with a loader like `python-dotenv` - not built-in yet, so manual export is an option):**
    You can create a `.env` file in the project root (ensure it's in `.gitignore`!) and load it, or set them directly in your shell.
    Example `.env` content:
    ```
    SMTP_HOST=smtp.example.com
    SMTP_PORT=587
    SMTP_USER=user@example.com
    SMTP_PASSWORD=your_secret_password
    SENDER_EMAIL=user@example.com
    ```
    Then run `export $(cat .env | xargs)` in your terminal before starting the app, or use a Python library to load it if you modify the app's entry point.

*   **Streamlit Cloud / Sharing**:
    You can set these as secrets directly in your Streamlit Cloud app settings. Refer to Streamlit's documentation on "Secrets management".

*   **Docker / Server Deployment**:
    Provide these environment variables when running the Docker container or configuring the application on your server.

## Example: Using Gmail SMTP

Gmail is a common choice for sending emails. Here's how to configure it:

1.  **Enable 2-Step Verification**: You must have 2-Step Verification enabled on your Google Account.
2.  **Create an App Password**:
    *   Go to your Google Account settings: [https://myaccount.google.com/](https://myaccount.google.com/)
    *   Navigate to "Security".
    *   Under "Signing in to Google," click on "App passwords" (you might need to sign in again). If you don't see this option, 2-Step Verification might not be set up correctly, or App Passwords might not be available for your account type.
    *   Select "Mail" for the app and "Other (Custom name)" for the device. Give it a name (e.g., "StockTrackerApp").
    *   Google will generate a 16-character App Password. **Copy this password immediately.** It will not be shown again.
3.  **Set Environment Variables**:
    *   `SMTP_HOST`: `smtp.gmail.com`
    *   `SMTP_PORT`: `587` (for TLS)
    *   `SMTP_USER`: Your full Gmail address (e.g., `your.email@gmail.com`)
    *   `SMTP_PASSWORD`: The 16-character App Password you generated (e.g., `abcd efgh ijkl mnop`).
    *   `SENDER_EMAIL`: Your full Gmail address (e.g., `your.email@gmail.com`).

**Important Notes for Gmail:**
*   Google may block sign-in attempts from apps it considers less secure. Using 2-Step Verification and an App Password is the recommended and more secure method.
*   There are sending limits for Gmail accounts (e.g., 500 emails per day for a standard account). For high-volume applications, consider a dedicated email sending service (e.g., SendGrid, Mailgun, AWS SES).

## Example: Generic SMTP Server

If you are using another email provider or your own SMTP server:

*   `SMTP_HOST`: Your provider's SMTP server address.
*   `SMTP_PORT`: Typically `587` (for STARTTLS) or `465` (for SSL). Check your provider's documentation. The current `EmailService` implementation uses STARTTLS.
*   `SMTP_USER`: Your email username.
*   `SMTP_PASSWORD`: Your email password.
*   `SENDER_EMAIL`: The email address you are sending from.

Consult your email provider's documentation for the correct SMTP settings.

## Testing Email Configuration

After setting up the environment variables, you can test the email service by triggering an event in the application that sends an email (e.g., a price alert). Check the application logs for any error messages from the `EmailService`.
```

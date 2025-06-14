import os
import smtplib
import logging
from email.mime.text import MIMEText

# Required Environment Variables for EmailService:
# SMTP_HOST: Hostname of the SMTP server (e.g., "smtp.gmail.com")
# SMTP_PORT: Port of the SMTP server (e.g., 587 for TLS, 465 for SSL)
# SMTP_USER: Username for SMTP authentication
# SMTP_PASSWORD: Password for SMTP authentication
# SENDER_EMAIL: The email address from which emails will be sent

class EmailService:
    """
    A service class for sending emails using SMTP.
    Configuration is loaded from environment variables.
    """

    def __init__(self):
        """
        Initializes the EmailService by loading SMTP configuration
        from environment variables.
        """
        self.logger = logging.getLogger(__name__)

        self.smtp_host = os.getenv("SMTP_HOST")
        smtp_port_str = os.getenv("SMTP_PORT")
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")

        self.smtp_port = 587  # Default to 587 for STARTTLS
        if smtp_port_str:
            try:
                self.smtp_port = int(smtp_port_str)
            except ValueError:
                self.logger.warning(
                    f"Invalid SMTP_PORT value '{smtp_port_str}'. Defaulting to {self.smtp_port}."
                )

        self.is_configured = all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_user,
            self.smtp_password,
            self.sender_email
        ])

        if not self.is_configured:
            self.logger.warning(
                "Email service is not fully configured. Environment variables "
                "(SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL) "
                "are required. Emails will not be sent."
            )

    def send_email(self, recipient_email: str, subject: str, body: str, body_type: str = 'html') -> bool:
        """
        Sends an email to the specified recipient.

        Args:
            recipient_email: The email address of the recipient.
            subject: The subject of the email.
            body: The content of the email (can be HTML or plain text).
            body_type: Type of the body content, 'html' or 'plain'. Default is 'html'.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        if not self.is_configured:
            self.logger.info(
                f"Email sending skipped to {recipient_email} (subject: '{subject}') "
                "due to lack of configuration."
            )
            return False

        if not recipient_email:
            self.logger.warning("No recipient email provided. Cannot send email.")
            return False

        msg = MIMEText(body, body_type)
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = recipient_email

        server = None  # Initialize server to None for finally block
        try:
            # If using SSL on a different port (e.g., 465), smtplib.SMTP_SSL would be used.
            # This implementation assumes STARTTLS on the specified port (default 587).
            self.logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) # Added timeout
            server.ehlo()  # Extended Hello to server

            # Attempt STARTTLS regardless of port, unless it's 465 (where SMTP_SSL is typical)
            if self.smtp_port != 465: # Common SSL port where STARTTLS is not used
                self.logger.info("Attempting STARTTLS...")
                server.starttls()
                server.ehlo()  # Re-send ehlo after STARTTLS

            self.logger.info(f"Logging in as {self.smtp_user}...")
            server.login(self.smtp_user, self.smtp_password)

            self.logger.info(f"Sending email to {recipient_email} with subject: {subject}...")
            server.sendmail(self.sender_email, recipient_email, msg.as_string())

            self.logger.info(f"Email sent successfully to {recipient_email} with subject: {subject}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP Authentication Error for user {self.smtp_user}: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            self.logger.error(f"SMTP Connection Error to {self.smtp_host}:{self.smtp_port}: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            self.logger.error(f"SMTP Server Disconnected unexpectedly: {e}")
            return False
        except smtplib.SMTPException as e: # Catch other SMTP related exceptions
            self.logger.error(f"SMTP Error when sending email to {recipient_email}: {e}")
            return False
        except OSError as e: # Catch socket errors, like "nodename nor servname provided, or not known"
            self.logger.error(f"Network or OS Error when sending email (check SMTP_HOST): {e}")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while sending email to {recipient_email}: {e}", exc_info=True)
            return False
        finally:
            if server:
                try:
                    self.logger.info("Closing SMTP server connection.")
                    server.quit()
                except smtplib.SMTPServerDisconnected: # pragma: no cover
                    self.logger.info("SMTP server was already disconnected.")
                except Exception as e: # pragma: no cover
                    self.logger.error(f"Error while closing SMTP server connection: {e}")

if __name__ == '__main__': # pragma: no cover
    # Example Usage (requires environment variables to be set)
    # This block will only run if the script is executed directly.
    # For actual testing, use unittest or pytest with mocks or a test SMTP server.

    # Configure basic logging for this example run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    if not all(os.getenv(var) for var in ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SENDER_EMAIL"]):
        logger.warning("SMTP environment variables are not fully set for the __main__ example.")
        logger.warning("Please set: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL")
        logger.warning("Skipping EmailService example execution.")
    else:
        logger.info("Attempting to send a test email using EmailService...")
        email_service = EmailService()

        if email_service.is_configured:
            # Replace with a real recipient email for testing
            test_recipient = os.getenv("TEST_RECIPIENT_EMAIL", "test@example.com")
            if test_recipient == "test@example.com" and "TEST_RECIPIENT_EMAIL" not in os.environ:
                logger.warning("TEST_RECIPIENT_EMAIL environment variable not set. Using 'test@example.com'.")

            subject = "Test Email from Stock Tracker EmailService"
            body_html = """
            <html>
                <body>
                    <h1>Hello!</h1>
                    <p>This is a <b>test email</b> from the Stock Tracker application's EmailService.</p>
                    <p>If you received this, the service is working correctly (at least for this configuration).</p>
                </body>
            </html>
            """

            logger.info(f"Sending test email to: {test_recipient}")
            success = email_service.send_email(test_recipient, subject, body_html, body_type='html')

            if success:
                logger.info(f"Test email sent successfully to {test_recipient}.")
            else:
                logger.error(f"Failed to send test email to {test_recipient}.")
        else:
            logger.warning("EmailService is not configured. Cannot send test email.")

    logger.info("EmailService __main__ example finished.")
```

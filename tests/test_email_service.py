import unittest
from unittest.mock import patch, MagicMock
import os
import smtplib
import logging

# Ensure src is in path for tests
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stock_tracker.services.email_service import EmailService

# Suppress most logging output during tests unless specifically testing logging
# If you want to see logs from the service during tests, set this to logging.INFO or logging.DEBUG
# For CI/CD, CRITICAL or ERROR is usually better to keep logs clean.
logger = logging.getLogger('src.stock_tracker.services.email_service')
logger.setLevel(logging.CRITICAL) # Suppress logs from the service itself
# To capture specific logs in tests, you can use self.assertLogs context manager.

class TestEmailService(unittest.TestCase):

    def _get_valid_env_vars(self):
        return {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "password123",
            "SENDER_EMAIL": "sender@example.com"
        }

    @patch.dict(os.environ, _get_valid_env_vars(None))
    def test_initialization_configured(self):
        with patch.dict(os.environ, self._get_valid_env_vars()):
            service = EmailService()
            self.assertTrue(service.is_configured)
            self.assertEqual(service.smtp_host, "smtp.example.com")
            self.assertEqual(service.smtp_port, 587)
            self.assertEqual(service.smtp_user, "user@example.com")
            self.assertEqual(service.smtp_password, "password123")
            self.assertEqual(service.sender_email, "sender@example.com")

    def test_initialization_not_configured_missing_one(self):
        # Test by clearing one essential var and ensuring others are set (or not)
        # Store original environment
        original_environ = os.environ.copy()

        test_env = self._get_valid_env_vars()
        del test_env["SMTP_PASSWORD"] # Remove one variable

        os.environ.clear()
        os.environ.update(test_env)

        with self.assertLogs(logger='src.stock_tracker.services.email_service', level='WARNING') as log_capture:
            service = EmailService()
            self.assertFalse(service.is_configured)
        self.assertIn("Email service is not fully configured", log_capture.output[0])

        # Restore original environment
        os.environ.clear()
        os.environ.update(original_environ)


    def test_initialization_not_configured_all_missing(self):
        original_environ = os.environ.copy()
        os.environ.clear() # Clear all env vars that might affect the test

        with self.assertLogs(logger='src.stock_tracker.services.email_service', level='WARNING') as log_capture:
            service = EmailService()
            self.assertFalse(service.is_configured)
        self.assertIn("Email service is not fully configured", log_capture.output[0])

        os.environ.clear()
        os.environ.update(original_environ)


    def test_initialization_default_port_when_not_set(self):
        env_vars = self._get_valid_env_vars()
        del env_vars["SMTP_PORT"] # SMTP_PORT is removed
        with patch.dict(os.environ, env_vars, clear=True): # clear=True ensures only these are set
            service = EmailService()
            # is_configured should still be true as port defaults
            self.assertTrue(service.is_configured)
            self.assertEqual(service.smtp_port, 587)


    def test_initialization_default_port_when_invalid(self):
        env_vars = self._get_valid_env_vars()
        env_vars["SMTP_PORT"] = "invalid_port" # Invalid port
        with patch.dict(os.environ, env_vars, clear=True):
            with self.assertLogs(logger='src.stock_tracker.services.email_service', level='WARNING') as log_capture:
                service = EmailService()
                self.assertTrue(service.is_configured)
                self.assertEqual(service.smtp_port, 587)
            self.assertIn("Invalid SMTP_PORT value 'invalid_port'", log_capture.output[0])


    @patch('src.stock_tracker.services.email_service.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp_class):
        with patch.dict(os.environ, self._get_valid_env_vars()):
            email_service = EmailService()
            self.assertTrue(email_service.is_configured)

            mock_smtp_instance = MagicMock()
            mock_smtp_class.return_value = mock_smtp_instance

            result = email_service.send_email("test@example.com", "Test Subject", "Test Body")

            self.assertTrue(result)
            mock_smtp_class.assert_called_once_with("smtp.example.com", 587, timeout=10)
            mock_smtp_instance.ehlo.assert_any_call()
            mock_smtp_instance.starttls.assert_called_once()
            mock_smtp_instance.login.assert_called_once_with("user@example.com", "password123")
            mock_smtp_instance.sendmail.assert_called_once()
            mock_smtp_instance.quit.assert_called_once()


    @patch('src.stock_tracker.services.email_service.smtplib.SMTP')
    def test_send_email_success_ssl_port_465_no_starttls(self, mock_smtp_class):
        env_vars_ssl = self._get_valid_env_vars()
        env_vars_ssl["SMTP_PORT"] = "465" # Port where STARTTLS is typically not used
        with patch.dict(os.environ, env_vars_ssl, clear=True):
            email_service = EmailService()
            self.assertTrue(email_service.is_configured)
            self.assertEqual(email_service.smtp_port, 465)

            mock_smtp_instance = MagicMock()
            mock_smtp_class.return_value = mock_smtp_instance

            result = email_service.send_email("test@example.com", "Test Subject SSL", "Test Body SSL")
            self.assertTrue(result)
            mock_smtp_class.assert_called_once_with("smtp.example.com", 465, timeout=10)
            mock_smtp_instance.starttls.assert_not_called() # Key check: STARTTLS should not be called
            mock_smtp_instance.login.assert_called_once_with("user@example.com", "password123")
            mock_smtp_instance.sendmail.assert_called_once()
            mock_smtp_instance.quit.assert_called_once()


    def test_send_email_not_configured(self):
        original_environ = os.environ.copy()
        os.environ.clear() # Ensure no configuration

        email_service = EmailService() # This will log a warning during init
        self.assertFalse(email_service.is_configured)

        # We expect an INFO log when send_email is called and service is not configured
        with self.assertLogs(logger='src.stock_tracker.services.email_service', level='INFO') as log_capture:
            result = email_service.send_email("test@example.com", "Test Subject", "Test Body")
            self.assertFalse(result)

        self.assertTrue(any("Email sending skipped due to lack of configuration" in msg for msg in log_capture.output))

        os.environ.clear()
        os.environ.update(original_environ)


    def test_send_email_no_recipient(self):
        with patch.dict(os.environ, self._get_valid_env_vars()):
            email_service = EmailService()
            self.assertTrue(email_service.is_configured)
            # Expect a WARNING log when recipient is empty
            with self.assertLogs(logger='src.stock_tracker.services.email_service', level='WARNING') as log_capture:
                result = email_service.send_email("", "Test Subject", "Test Body") # Empty recipient
                self.assertFalse(result)
            self.assertIn("No recipient email provided", log_capture.output[0])


    @patch('src.stock_tracker.services.email_service.smtplib.SMTP')
    def test_send_email_smtp_authentication_error(self, mock_smtp_class):
        with patch.dict(os.environ, self._get_valid_env_vars()):
            email_service = EmailService()
            mock_smtp_instance = MagicMock()
            mock_smtp_class.return_value = mock_smtp_instance
            mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(
                535, b"Authentication credentials invalid"
            )

            with self.assertLogs(logger='src.stock_tracker.services.email_service', level='ERROR') as log_capture:
                result = email_service.send_email("test@example.com", "Auth Fail", "Body")
                self.assertFalse(result)
            self.assertIn("SMTP Authentication Error", log_capture.output[0])
            mock_smtp_instance.quit.assert_called_once()


    @patch('src.stock_tracker.services.email_service.smtplib.SMTP')
    def test_send_email_smtp_connect_error(self, mock_smtp_class):
        with patch.dict(os.environ, self._get_valid_env_vars()):
            email_service = EmailService()
            mock_smtp_class.side_effect = smtplib.SMTPConnectError(500, "Connection timed out")

            with self.assertLogs(logger='src.stock_tracker.services.email_service', level='ERROR') as log_capture:
                result = email_service.send_email("test@example.com", "Connect Fail", "Body")
                self.assertFalse(result)
            self.assertIn("SMTP Connection Error", log_capture.output[0])
            # quit should not be called on the instance if the constructor failed
            # mock_smtp_instance is not created here, so no mock_smtp_instance.quit() check


    @patch('src.stock_tracker.services.email_service.smtplib.SMTP')
    def test_send_email_generic_exception_on_sendmail(self, mock_smtp_class):
        with patch.dict(os.environ, self._get_valid_env_vars()):
            email_service = EmailService()
            mock_smtp_instance = MagicMock()
            mock_smtp_class.return_value = mock_smtp_instance
            mock_smtp_instance.sendmail.side_effect = Exception("Generic sending error")

            with self.assertLogs(logger='src.stock_tracker.services.email_service', level='ERROR') as log_capture:
                result = email_service.send_email("test@example.com", "Generic Fail", "Body")
                self.assertFalse(result)
            self.assertIn("An unexpected error occurred while sending email", log_capture.output[0])
            mock_smtp_instance.quit.assert_called_once()


    @patch('src.stock_tracker.services.email_service.smtplib.SMTP')
    def test_send_email_os_error_on_connect(self, mock_smtp_class):
        with patch.dict(os.environ, self._get_valid_env_vars()):
            email_service = EmailService()
            mock_smtp_class.side_effect = OSError("Network is unreachable")

            with self.assertLogs(logger='src.stock_tracker.services.email_service', level='ERROR') as log_capture:
                result = email_service.send_email("test@example.com", "OS Error", "Body")
                self.assertFalse(result)
            self.assertIn("Network or OS Error when sending email", log_capture.output[0])


if __name__ == '__main__': # pragma: no cover
    unittest.main()
```

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def send_email_alert(recipient: str, subject: str, body_html: str):
    """SMTP service implementation for dispatching HTML emails."""
    # In a real environment, you'd use SendGrid/AWS SES or configured SMTP
    # Here we mock it for development
    
    mock_smtp_host = "localhost" # Assuming highly local config or disabled
    mock_smtp_port = 1025 # Common mailhog testing port
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "alerts@wearable-ai.local"
    msg["To"] = recipient

    # Compile the HTML template
    html_part = MIMEText(body_html, "html")
    msg.attach(html_part)

    try:
        # Non-blocking async smtp should ideally be used (aiosmtplib), but synchronous serves the MVP
        with smtplib.SMTP(mock_smtp_host, mock_smtp_port) as server:
            # server.login() and TLS skipped for local test environment
            server.sendmail(msg["From"], [recipient], msg.as_string())
            logger.info(f"Dispatched email alert to {recipient}")
    except ConnectionRefusedError:
        logger.debug(f"Email skipped: No SMTP server listening on {mock_smtp_host}:{mock_smtp_port}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")

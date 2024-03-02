import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailSender:
    def __init__(self, smtp_server, port, username, password, use_tls=True):
        """
        Initialize the EmailSender with SMTP server details.

        :param smtp_server: Address of the SMTP server.
        :param port: Port number for the SMTP server.
        :param username: Username for SMTP authentication.
        :param password: Password for SMTP authentication.
        :param use_tls: Use TLS for secure connection (default: True).
        """
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send_email(self, sender, recipient, subject, body):
        """
        Send an email using the SMTP server.

        :param sender: Email address of the sender.
        :param recipient: Email address of the recipient.
        :param subject: Subject of the email.
        :param body: Body of the email.
        :return: None
        """
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                logging.info(f"Email sent successfully to {recipient}")
        except smtplib.SMTPException as e:
            logging.error(f"Failed to send email: {e}")
            raise

# Test Function
def test_email_sender():
    """
    Test function for EmailSender class.
    """
    logging.info("Starting test for EmailSender")
    try:
        sender = EmailSender('smtp.example.com', 587, 'your_username', 'your_password')
        sender.send_email('from@example.com', 'to@example.com', 'Test Subject', 'This is the body of the email.')
        logging.info("Test completed successfully")
    except Exception as e:
        logging.error(f"Test failed: {e}")

# Uncomment to run the test
test_email_sender()

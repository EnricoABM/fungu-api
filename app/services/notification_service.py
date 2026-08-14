import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.infra.config import Settings

class NotificationService:
    @staticmethod
    def send_telegram(chat_id: str, message: str):
        if not Settings.TELEGRAM_BOT_TOKEN or not chat_id:
            return
        url = f"https://api.telegram.org/bot{Settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Erro no envio do Telegram: {e}")

    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        if not Settings.SMTP_USER or not to_email:
            return
        msg = MIMEMultipart()
        msg['From'] = Settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(Settings.SMTP_SERVER, Settings.SMTP_PORT)
            server.starttls()
            server.login(Settings.SMTP_USER, Settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Erro no envio do E-mail: {e}")

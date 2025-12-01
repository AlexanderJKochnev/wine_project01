import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config.project_config import settings


class EmailSender:
    def __init__(self):
        self.smtp_host = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.use_tls = settings.EMAIL_USE_TLS
        self.use_ssl = settings.EMAIL_USE_SSL

    async def send_email(self, to_email: str, subject: str, body: str):
        """
        Отправляет электронное письмо
        
        :param to_email: Адрес получателя
        :param subject: Тема письма
        :param body: Текст письма
        """
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            if self.use_ssl:
                # For SSL connections (like Yandex on port 465)
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                # For TLS connections (like Gmail on port 587)
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
        except Exception as e:
            print(f"Ошибка при отправке электронного письма: {e}")
            raise
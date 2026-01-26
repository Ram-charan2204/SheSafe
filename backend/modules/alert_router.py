import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class AlertRouter:
    def __init__(self):
        self.sender_email = "shesafe05@gmail.com"
        self.sender_password = "hljuvhdqitlcuebv"
        self.receiver_email = "ramcharancherry338@gmail.com"

    def send_email(self, alert_type):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subject = f"SHE SAFE ALERT: {alert_type}"
        body = f"""
SHE SAFE SYSTEM ALERT

Alert Type : {alert_type}
Time       : {time_now}

Immediate attention required.
"""

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        server.send_message(msg)
        server.quit()

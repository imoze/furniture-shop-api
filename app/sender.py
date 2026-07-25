import smtplib
from email.mime.text import MIMEText

class Sender():
    def __init__(self):
        self.server_settings = ('mailhog', 1025)

    def send_email(self, order_str, email):
        message = MIMEText(order_str)
        message['From'] = 'furniture@shop.com'
        message['To'] = email
        message['Subject'] = 'Your order'

        with smtplib.SMTP(*self.server_settings) as server:
            server.send_message(message)

def get_sender():
    sender = Sender()
    yield sender
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os.path
import pickle

class GmailClient:
    def __init__(self, credentials_file, token_file='token.pickle'):
        self.token_file = token_file
        self.credentials_file = credentials_file
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        # Загружаем сохраненные токены, если они есть
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # Если нет действующих учетных данных, позволяем пользователю войти
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Сохраняем учетные данные для следующего запуска
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        return service

    def create_message(self, sender, to, subject, message_text):
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        msg = MIMEText(message_text)
        message.attach(msg)

        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        return {'raw': raw}

    def create_message_html(self, sender, to, subject, message_text_html):
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        # Ваше HTML-содержимое
        part2 = MIMEText(message_text_html, 'html')
        message.attach(part2)

        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        return {'raw': raw}

    def send_message(self, user_id, message):
        try:
            sent_message = (self.service.users().messages().send(userId=user_id, body=message).execute())
            print('Message Id: %s' % sent_message['id'])
            return sent_message
        except Exception as e:
            print('An error occurred: %s' % e)



# Пример использования класса
if __name__ == "__main__":
    gmail_client = GmailClient('client_secret_941562501395-mip2shfoedg2iso8jj74pb9ks2tuu3a0.apps.googleusercontent.com.json')
    sender = "admin@me-qr.me"
    to = "vdeathwalker@gmail.com"
    subject = "Тестовое письмо"
    message_text = "Текст письма"
    message = gmail_client.create_message(sender, to, subject, message_text)
    gmail_client.send_message("me", message)

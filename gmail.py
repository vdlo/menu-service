import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException



class Gmail:

    gmail_user = 'menu.service.me@gmail.com'
    gmail_password = 'RhceDL^7'

    def __init__(self, to, subject, body):
        self.msg = MIMEMultipart()
        self.msg['From'] = self.gmail_user
        self.msg['To'] = to
        self.msg['Subject'] = subject
        self.msg.attach(MIMEText(body, 'plain'))

    def send(self):
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.gmail_user, self.gmail_password)
            text = self.msg.as_string()
            server.sendmail(self.gmail_user, self.msg['To'], text)
            server.close()
            print('Email sent!')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


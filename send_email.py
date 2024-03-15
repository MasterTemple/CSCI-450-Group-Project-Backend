import smtplib
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
s=smtplib.SMTP("smtp.gmail.com", 587)
s.starttls()

load_dotenv()

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("APP_PASSWORD")

s.login(EMAIL, PASSWORD)

receiver="blake.scampone@biola.edu"
subject="Lyric of Lyrics - Verification Code"
body="Your verification code is <b>414514</b>"

msg = MIMEMultipart()
msg['From'] = EMAIL
msg['To'] = receiver
msg['Subject'] = subject
html_message = body
msg.attach(MIMEText(html_message, 'html'))
s.sendmail(EMAIL, [receiver], msg.as_string())

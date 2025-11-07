import math
from email.message import EmailMessage
import smtplib
from config import Config

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c  # km

def send_email(subject, to_email, body):
    if not (Config.GMAIL_USER and Config.GMAIL_PASS):
        return False, "Email not configured"
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = Config.GMAIL_USER
    msg["To"] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(Config.GMAIL_USER, Config.GMAIL_PASS)
            smtp.send_message(msg)
        return True, "sent"
    except Exception as e:
        return False, str(e)

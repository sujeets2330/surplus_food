from agents.utils import send_email

class MonitoringAgent:
    def __init__(self):
        pass

    def notify_match(self, donor_email, recipient_email, details):
        subject = "Donation Match Planned"
        body = f"A match has been created. Details: {details}"
        send_email(subject, donor_email, body)
        send_email(subject, recipient_email, body)

    def notify_status(self, to_email, status, details):
        subject = f"Delivery Status Update: {status}"
        body = f"Status changed to {status}. Details: {details}"
        send_email(subject, to_email, body)

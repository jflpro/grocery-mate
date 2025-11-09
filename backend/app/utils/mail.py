from email.message import EmailMessage
import smtplib

def send_newsletter(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'jeff@grooo-mate.work.gd'
    msg['To'] = to_email
    # --- Header List-Unsubscribe ---
    msg['List-Unsubscribe'] = '<mailto:unsubscribe@grooo-mate.work.gd>'
    msg.set_content(body)

    # --- Envoi SMTP ---
    with smtplib.SMTP('mail.grooo-mate.work.gd', 25) as smtp:
        smtp.login('jeff@grooo-mate.work.gd', 'TON_MDP_ICI')
        smtp.send_message(msg)

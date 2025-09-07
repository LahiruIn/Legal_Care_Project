from email.message import EmailMessage
import smtplib
from flask import current_app

def send_email(subject: str, to: str, html: str = None, text: str = None, from_name: str = None) -> bool:
    cfg = current_app.config
    host = cfg.get("MAIL_HOST")
    port = int(cfg.get("MAIL_PORT", 587))
    username = cfg.get("MAIL_USERNAME")
    password = cfg.get("MAIL_PASSWORD")
    use_tls = bool(cfg.get("MAIL_USE_TLS", True))
    from_addr = cfg.get("MAIL_FROM") or username
    sender_name = from_name or cfg.get("MAIL_SENDER_NAME", "Legal Care")

    # Guard: all required settings must exist
    if not (host and port and username and password and from_addr):
        current_app.logger.warning("Email not sent – mail config incomplete.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{from_addr}>"
    msg["To"] = to

    if html:
        msg.set_content(text or "You have a new message.")
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(text or "")

    with smtplib.SMTP(host, port) as s:
        if use_tls:
            s.starttls()
        s.login(username, password)
        s.send_message(msg)
    return True

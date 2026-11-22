import logging
from email.message import EmailMessage
from email.utils import formataddr

import aiosmtplib

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Отправляет email через SMTP.
    Возвращает True при успехе, False при ошибке.
    Не бросает исключения — только логирует.
    """
    if not to_email:
        logger.warning("Empty email, skip sending")
        return False

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = formataddr(("", to_email))
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls,
            timeout=15,
        )
        logger.info("Email sent to %s (subject: %s)", to_email, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False
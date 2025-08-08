from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(email_to: str, subject: str, html_content: str):
    """
    Sends an email using fastapi-mail.
    """
    message = MessageSchema(
        subject=subject, recipients=[email_to], body=html_content, subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_password_reset_email(email_to: str, callback_url: str, token: str):
    """
    Constructs and sends the password reset email.
    """
    reset_url = f"{callback_url}?token={token}"
    subject = "Reset Your Password"

    html_content = f"""
    <html>
    <body>
        <p>Hello,</p>
        <p>You requested to reset your password. Please click the link below to proceed:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>Thanks,</p>
        <p>Your Application Team</p>
    </body>
    </html>
    """

    await send_email(email_to, subject, html_content)

import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings

logger = logging.getLogger(__name__)

_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
    VALIDATE_CERTS=True,
)


def _build_invite_html(invited_by_name: str, role: str, validation_code: str, accept_url: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>TeamFlow Invite</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 40px 20px;">
  <div style="max-width: 480px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px; border: 1px solid #334155;">
    <div style="margin-bottom: 24px;">
      <div style="width: 40px; height: 40px; background: #6366f1; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px;">T</div>
      <span style="font-size: 20px; font-weight: 600; color: white; margin-left: 10px; vertical-align: middle;">TeamFlow</span>
    </div>
    <h1 style="font-size: 22px; font-weight: 600; color: white; margin: 0 0 8px;">You've been invited</h1>
    <p style="color: #94a3b8; margin: 0 0 24px;">{invited_by_name} has invited you to join TeamFlow as a <strong style="color: #a5b4fc;">{role}</strong>.</p>
    <div style="background: #0f172a; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 24px; border: 1px solid #334155;">
      <p style="color: #94a3b8; font-size: 13px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.05em;">Your Validation Code</p>
      <p style="color: white; font-size: 36px; font-weight: 700; letter-spacing: 0.15em; margin: 0; font-family: monospace;">{validation_code}</p>
    </div>
    <a href="{accept_url}" style="display: block; background: #6366f1; color: white; text-decoration: none; text-align: center; padding: 14px 24px; border-radius: 8px; font-weight: 600; font-size: 15px; margin-bottom: 20px;">Accept Invitation</a>
    <p style="color: #64748b; font-size: 12px; margin: 0;">This invitation expires in 72 hours. If you did not expect this email, you can safely ignore it.</p>
  </div>
</body>
</html>
"""


async def send_invite_email(
    to_email: str,
    invited_by_name: str,
    role: str,
    validation_code: str,
    token: str,
) -> None:
    if not settings.MAIL_USERNAME:
        logger.warning("MAIL_USERNAME not configured — skipping invite email to %s (code: %s)", to_email, validation_code)
        return

    accept_url = f"{settings.FRONTEND_URL}/invite/accept?token={token}"
    html_body = _build_invite_html(invited_by_name, role, validation_code, accept_url)

    message = MessageSchema(
        subject="You've been invited to join TeamFlow",
        recipients=[to_email],
        body=html_body,
        subtype=MessageType.html,
    )
    fm = FastMail(_conf)
    await fm.send_message(message)
    logger.info("Invite email sent to %s", to_email)

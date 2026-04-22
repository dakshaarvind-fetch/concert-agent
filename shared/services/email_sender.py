"""Email sender — step 12. Uses Resend API (preferred for Agentverse Hosted)."""


async def send_email(to: str, subject: str, html: str) -> None:
    """
    Send an HTML email.

    Prefers RESEND_API_KEY when set; falls back to Gmail SMTP via
    GMAIL_SMTP_USER + GMAIL_SMTP_APP_PASSWORD.
    """
    raise NotImplementedError(
        "email_sender.send_email — implement in step 12. "
        "Wire either resend SDK or smtplib here."
    )

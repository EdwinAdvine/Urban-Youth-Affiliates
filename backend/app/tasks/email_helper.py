"""SMTP email helper used by Celery tasks.

All email sending is synchronous (called from worker, not from async FastAPI).
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(*, to: str, subject: str, html_body: str, text_body: str = "") -> bool:
    """Send an email via SMTP. Returns True on success, False on error."""
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not configured — email skipped: %s", subject)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, [to], msg.as_string())
        logger.info("Email sent to %s — %s", to, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        return False


# ─── Email templates ──────────────────────────────────────────────────────────

def _base_html(title: str, body: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{title}</title></head>
<body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden">
    <div style="background:#0A0A0A;padding:24px;text-align:center">
      <h1 style="color:#F59E0B;margin:0;font-size:22px">Y&amp;U Affiliates</h1>
    </div>
    <div style="padding:32px">
      {body}
    </div>
    <div style="background:#f5f5f5;padding:16px;text-align:center;font-size:12px;color:#666">
      &copy; 2026 Y&amp;U Affiliates. All rights reserved.
    </div>
  </div>
</body>
</html>
"""


def affiliate_approved_email(to: str, full_name: str) -> None:
    body = f"""
<h2 style="color:#0A0A0A">Welcome aboard, {full_name}!</h2>
<p>Your affiliate application has been <strong style="color:#10B981">approved</strong>.</p>
<p>You can now log in, browse the product marketplace, and start generating referral links.</p>
<a href="https://affiliates.yuaffiliates.co.ke/affiliate/marketplace"
   style="display:inline-block;background:#F59E0B;color:#0A0A0A;padding:12px 24px;
          border-radius:6px;text-decoration:none;font-weight:bold;margin-top:16px">
  Browse Products
</a>
"""
    send_email(
        to=to,
        subject="Your Y&U Affiliates application has been approved!",
        html_body=_base_html("Application Approved", body),
        text_body=f"Hi {full_name}, your affiliate application has been approved. Log in to start earning.",
    )


def affiliate_rejected_email(to: str, full_name: str, reason: str = "") -> None:
    reason_block = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
    body = f"""
<h2 style="color:#0A0A0A">Application Update</h2>
<p>Hi {full_name}, unfortunately your affiliate application was not approved at this time.</p>
{reason_block}
<p>If you believe this is an error, please contact <a href="mailto:support@yuaffiliates.co.ke">support@yuaffiliates.co.ke</a>.</p>
"""
    send_email(
        to=to,
        subject="Y&U Affiliates — Application Status Update",
        html_body=_base_html("Application Update", body),
        text_body=f"Hi {full_name}, your affiliate application was not approved. Contact support for details.",
    )


def new_sale_email(
    to: str,
    full_name: str,
    order_id: str,
    sale_amount: float,
    commission: float,
) -> None:
    body = f"""
<h2 style="color:#0A0A0A">You made a sale!</h2>
<p>Hi {full_name}, great news — a conversion was recorded for your referral link.</p>
<table style="width:100%;border-collapse:collapse;margin-top:16px">
  <tr><td style="padding:8px;border-bottom:1px solid #eee;color:#666">Order ID</td>
      <td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold">{order_id}</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #eee;color:#666">Sale Amount</td>
      <td style="padding:8px;border-bottom:1px solid #eee">KES {sale_amount:,.2f}</td></tr>
  <tr><td style="padding:8px;color:#666">Commission Earned</td>
      <td style="padding:8px;font-weight:bold;color:#10B981">KES {commission:,.2f}</td></tr>
</table>
<p style="margin-top:16px;font-size:13px;color:#666">Commission is pending admin approval before it's added to your withdrawable balance.</p>
"""
    send_email(
        to=to,
        subject=f"New sale! You earned KES {commission:,.2f}",
        html_body=_base_html("New Sale", body),
        text_body=f"Hi {full_name}, you earned KES {commission:,.2f} commission on order {order_id}.",
    )


def payout_approved_email(to: str, full_name: str, amount: float) -> None:
    body = f"""
<h2 style="color:#0A0A0A">Payout Processed</h2>
<p>Hi {full_name}, your payout of <strong style="color:#10B981">KES {amount:,.2f}</strong> has been approved and a bank transfer has been initiated.</p>
<p>Transfers typically arrive within 1–2 business days depending on your bank.</p>
"""
    send_email(
        to=to,
        subject=f"Y&U Affiliates — Payout of KES {amount:,.2f} sent",
        html_body=_base_html("Payout Processed", body),
        text_body=f"Hi {full_name}, your payout of KES {amount:,.2f} has been initiated.",
    )


def payout_failed_email(to: str, full_name: str, amount: float, reason: str = "") -> None:
    reason_block = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
    body = f"""
<h2 style="color:#0A0A0A">Payout Failed</h2>
<p>Hi {full_name}, unfortunately your payout of <strong>KES {amount:,.2f}</strong> could not be processed.</p>
{reason_block}
<p>The amount has been returned to your approved balance. Please update your bank details and try again, or contact support.</p>
"""
    send_email(
        to=to,
        subject="Y&U Affiliates — Payout could not be processed",
        html_body=_base_html("Payout Failed", body),
        text_body=f"Hi {full_name}, your payout of KES {amount:,.2f} failed. The amount has been returned to your balance.",
    )

import requests
from flask import current_app


class WhatsAppService:
    """
    Sends WhatsApp messages via the Meta Cloud API.
    Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
    """

    BASE_URL = "https://graph.facebook.com/v19.0"

    @classmethod
    def _headers(cls) -> dict:
        token = current_app.config["WHATSAPP_API_TOKEN"]
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def _phone_id(cls) -> str:
        return current_app.config["WHATSAPP_PHONE_NUMBER"]

    # ── Send text message ─────────────────────────────────────────────────────

    @classmethod
    def send_text(cls, to: str, message: str) -> dict:
        """Send a plain text message to a WhatsApp number."""
        url = f"{cls.BASE_URL}/{cls._phone_id()}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        try:
            resp = requests.post(url, json=payload, headers=cls._headers(), timeout=10)
            resp.raise_for_status()
            return {"success": True, "message_id": resp.json().get("messages", [{}])[0].get("id")}
        except requests.RequestException as e:
            current_app.logger.error(f"[WhatsApp] send_text failed: {e}")
            return {"success": False, "error": str(e)}

    # ── Order notification to admin ───────────────────────────────────────────

    @classmethod
    def notify_admin_new_order(cls, order) -> dict:
        """
        Notify the shop owner on WhatsApp when a new order is placed.
        `order` is an Order model instance.
        """
        admin_phone = current_app.config["WHATSAPP_PHONE_NUMBER"]

        items_text = "\n".join(
            f"  • {item.product_name} x{item.quantity} — ₹{item.subtotal:,.0f}"
            for item in order.items
        )

        message = (
            f"🛍️ *New Order Received!*\n\n"
            f"📋 Order: *{order.order_number}*\n"
            f"👤 Customer: {order.customer_name}\n"
            f"📞 Phone: {order.customer_phone}\n"
            f"📍 Address: {order.customer_address or 'Not provided'}\n\n"
            f"*Items:*\n{items_text}\n\n"
            f"💰 *Total: ₹{float(order.total_amount):,.0f}*\n"
            f"📦 Source: {order.source.upper()}\n\n"
            f"Reply to confirm this order."
        )
        return cls.send_text(admin_phone, message)

    # ── Order confirmation to customer ────────────────────────────────────────

    @classmethod
    def notify_customer_order_confirmed(cls, order) -> dict:
        """Send an order confirmation message to the customer."""
        message = (
            f"✅ *Order Confirmed — SANA Sarees*\n\n"
            f"Hi {order.customer_name}! 🙏\n\n"
            f"Your order *{order.order_number}* has been confirmed.\n"
            f"Total: ₹{float(order.total_amount):,.0f}\n\n"
            f"We'll get in touch for delivery details.\n"
            f"Thank you for shopping with SANA! 🌸"
        )
        return cls.send_text(order.customer_phone, message)

    # ── Status update to customer ─────────────────────────────────────────────

    @classmethod
    def notify_status_update(cls, order) -> dict:
        status_emoji = {
            "confirmed":  "✅",
            "processing": "🔨",
            "shipped":    "🚚",
            "delivered":  "🎉",
            "cancelled":  "❌",
        }
        emoji = status_emoji.get(order.status, "📦")

        message = (
            f"{emoji} *Order Update — SANA Sarees*\n\n"
            f"Hi {order.customer_name}!\n\n"
            f"Your order *{order.order_number}* status:\n"
            f"*{order.status.upper()}*\n\n"
            f"For queries, reply to this message."
        )
        return cls.send_text(order.customer_phone, message)

    # ── Webhook verification ──────────────────────────────────────────────────

    @staticmethod
    def verify_webhook(mode: str, token: str, challenge: str) -> str | None:
        """
        Verify a Meta webhook subscription request.
        Returns the challenge string if valid, else None.
        """
        expected = current_app.config["WHATSAPP_VERIFY_TOKEN"]
        if mode == "subscribe" and token == expected:
            return challenge
        return None

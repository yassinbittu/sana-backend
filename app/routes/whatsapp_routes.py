from flask import Blueprint, request, jsonify
from app.utils.whatsapp import WhatsAppService
from app.utils.helpers import success_response, error_response
from app.middleware.auth_middleware import admin_required

whatsapp_bp = Blueprint("whatsapp", __name__)


@whatsapp_bp.get("/webhook")
def verify_webhook():
    """
    GET /api/whatsapp/webhook
    Meta platform calls this to verify the webhook endpoint.
    Params: hub.mode, hub.verify_token, hub.challenge
    """
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    result = WhatsAppService.verify_webhook(mode, token, challenge)
    if result:
        # Return challenge as plain text (Meta requirement)
        return result, 200, {"Content-Type": "text/plain"}

    return error_response("Webhook verification failed. Check your WHATSAPP_VERIFY_TOKEN.", 403)


@whatsapp_bp.post("/webhook")
def receive_webhook():
    """
    POST /api/whatsapp/webhook
    Meta sends incoming messages / status updates here.
    Parses the payload and logs it; extend this to auto-create orders etc.
    """
    payload = request.get_json(silent=True) or {}

    # ── Safety check ──────────────────────────────────────
    if payload.get("object") != "whatsapp_business_account":
        return jsonify({"success": False}), 400

    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # ── Incoming message ──────────────────────
                for msg in value.get("messages", []):
                    from_number = msg.get("from")
                    msg_type    = msg.get("type")
                    body        = msg.get("text", {}).get("body", "")

                    # TODO: hook into your business logic here
                    # e.g. parse "ORDER SANA-20240115-X7K2" to confirm orders
                    print(f"[WhatsApp] Message from {from_number} [{msg_type}]: {body}")

                # ── Status update ─────────────────────────
                for status in value.get("statuses", []):
                    print(f"[WhatsApp] Status update: {status.get('id')} → {status.get('status')}")

    except Exception as e:
        print(f"[WhatsApp] Webhook parse error: {e}")

    # Meta requires a 200 response, always
    return jsonify({"success": True}), 200


@whatsapp_bp.post("/send")
@admin_required
def send_message():
    """
    POST /api/whatsapp/send
    Manually send a WhatsApp message (admin only).
    Body: { "to": "919876543210", "message": "Hello!" }
    """
    data = request.get_json(silent=True) or {}
    to   = data.get("to")
    msg  = data.get("message")

    if not to or not msg:
        return error_response("'to' and 'message' are required")

    result = WhatsAppService.send_text(to, msg)
    if result.get("success"):
        return success_response(
            data={"message_id": result.get("message_id")},
            message="Message sent successfully",
        )
    return error_response(f"Failed to send message: {result.get('error')}", 502)

from flask import Blueprint, request, jsonify
from app.utils.whatsapp import WhatsAppService
from app.utils.helpers import success_response, error_response
from app.middleware.auth_middleware import admin_required

whatsapp_bp = Blueprint("whatsapp", __name__)


@whatsapp_bp.get("/webhook")
def verify_webhook():
    """
    Verify WhatsApp webhook
    ---
    tags:
      - WhatsApp
    parameters:
      - in: query
        name: hub.mode
        type: string
        required: true
        example: "subscribe"
      - in: query
        name: hub.verify_token
        type: string
        required: true
        example: "your_verify_token"
      - in: query
        name: hub.challenge
        type: string
        required: true
        example: "challenge_string"
    responses:
      200:
        description: Webhook verified
        schema:
          type: string
          example: "challenge_string"
      403:
        description: Verification failed
    """
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    result = WhatsAppService.verify_webhook(mode, token, challenge)
    if result:
        # Return challenge as plain text (Meta requirement)
        return result, 200, {"Content-Type": "text/plain"}

    return error_response("Webhook verification failed. Check your WHATSAPP_VERIFY_TOKEN.", 403)
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
    Receive WhatsApp webhook
    ---
    tags:
      - WhatsApp
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: WhatsApp webhook payload
    responses:
      200:
        description: Webhook processed
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
      400:
        description: Invalid payload
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
    Send WhatsApp message
    ---
    tags:
      - WhatsApp
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            to:
              type: string
              example: "919876543210"
            message:
              type: string
              example: "Hello from SANA!"
    responses:
      200:
        description: Message sent
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Message sent successfully"
            data:
              type: object
              properties:
                message_id:
                  type: string
                  example: "wamid.HBgLMTY0NjcwNDI1MDIVAgASGBQzA3NDA0Q0FGMzYxQzYxMzAA="
      400:
        description: Bad request
      401:
        description: Unauthorized
      502:
        description: WhatsApp API error
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

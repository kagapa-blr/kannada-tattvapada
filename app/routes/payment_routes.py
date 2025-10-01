from flask import Blueprint, render_template, request, jsonify
from app.services.payment_service import CashfreePaymentService
from app.services.shopping_user_service import MessageTemplate
from app.utils.logger import setup_logger

payment_bp = Blueprint("payment", __name__,template_folder="templates/payment",url_prefix="/payment")

API_PREFIX = "/api/v1"
logger = setup_logger("payment_route")
payment_service = CashfreePaymentService()

# -----------------------------
# Create Order
# -----------------------------
@payment_bp.route(f"{API_PREFIX}/create-order", methods=["POST"])
def create_order():
    try:
        data = request.json or {}
        email = data.get("email")
        phone = data.get("phone")
        amount = data.get("amount")
        name = data.get("name")
        shipping_address = data.get("address")
        cart_items = data.get("items")

        if not email or not phone or not amount:
            return jsonify(MessageTemplate.invalid_request("Email, phone, and amount are required")), 400

        amount = float(amount)
        if amount <= 0:
            return jsonify(MessageTemplate.invalid_request("Amount must be positive")), 400

        user_info = {"email": email, "phone": phone, "name": name}

        order_id, payment_session_id = payment_service.create_order(
            email=email,
            phone=phone,
            amount=amount,
            name=name,
            host_url=request.host_url,
            user_info=user_info,
            address_info=shipping_address,
            items=cart_items
        )

        return jsonify(MessageTemplate.success("Order created", {
            "order_id": order_id,
            "payment_session_id": payment_session_id
        })), 200

    except Exception as e:
        logger.exception("Error creating order")
        return jsonify(MessageTemplate.database_error(str(e))), 500

# -----------------------------
# Payment Status
# -----------------------------
@payment_bp.route(f"{API_PREFIX}/payment-status")
def payment_status():
    order_id = request.args.get("order_id")
    if not order_id:
        return jsonify(MessageTemplate.invalid_request("Missing order_id")), 400

    try:
        order, payment = payment_service.fetch_order_with_payments(order_id)
        status = payment.get("payment_status", getattr(order, "status", "PENDING"))

        receipt_data = {
            "Order ID": getattr(order, "order_number", order_id),
            "Status": status,
            "Amount": payment.get("payment_amount") or getattr(order, "total_amount", 0),
            "Transaction No": payment.get("cf_payment_id") or "N/A",
            "Transaction Date": payment.get("payment_time") or getattr(order, "created_at"),
            "Bank Ref No": payment.get("bank_reference") or "N/A",
            "Payment Method": payment.get("payment_method") or getattr(order, "payment_method"),
            "Customer Info": getattr(order, "user_info", {}),
            "Shipping Address": getattr(order, "address_info", {}),
            "Items": getattr(order, "items", [])
        }

        return jsonify(MessageTemplate.success("Payment status retrieved", {
            "order_id": order_id,
            "receipt_data": receipt_data
        })), 200

    except Exception as e:
        logger.exception(f"Error fetching payment status for order_id={order_id}")
        return jsonify(MessageTemplate.database_error(str(e))), 500

# -----------------------------
# Webhook
# -----------------------------
@payment_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        signature = request.headers.get("x-webhook-signature")
        timestamp = request.headers.get("x-webhook-timestamp")
        raw_body = request.data.decode("utf-8")

        event_type, event_data = payment_service.verify_webhook(signature, raw_body, timestamp)
        logger.info(f"[Webhook] Received {event_type} for order {event_data.get('order_id')}")
        return jsonify(MessageTemplate.success("Webhook processed")), 200

    except Exception as e:
        logger.exception("Error in webhook handler")
        return jsonify(MessageTemplate.database_error(str(e))), 500


# -----------------------------
# Success Page
# -----------------------------
@payment_bp.route("/success")
def success_page():
    order_id = request.args.get("order_id")
    if not order_id:
        return "Missing order_id", 400

    try:
        # Fetch order and payment info from Cashfree
        order, payment = payment_service.fetch_order_with_payments(order_id)

        # Render success template only if payment succeeded
        status = payment.get("payment_status", getattr(order, "status", "PENDING"))
        if status.upper() in ["SUCCESS", "PAID"]:
            return render_template("payment/success.html", order=order, payment=payment)
        else:
            return render_template("payment/failure.html", order=order, payment=payment)

    except Exception as e:
        logger.exception(f"Error in success page for order_id={order_id}")
        return render_template("payment/failure.html", order_id=order_id, error=str(e)), 500


# -----------------------------
# Failure Page
# -----------------------------
@payment_bp.route("/failure")
def failure_page():
    order_id = request.args.get("order_id")
    if not order_id:
        return "Missing order_id", 400

    try:
        # Optionally fetch order/payment info if available
        order, payment = payment_service.fetch_order_with_payments(order_id)
    except Exception:
        order, payment = {}, {}

    return render_template("payment/failure.html", order=order, payment=payment)

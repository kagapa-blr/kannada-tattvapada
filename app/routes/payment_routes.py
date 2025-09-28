from flask import Blueprint, render_template, request, jsonify

from app.routes.payment_service import CashfreePaymentService
from app.utils.logger import setup_logger

payment_bp = Blueprint("payment",__name__,template_folder="templates/payment",url_prefix="/payment")

API_PREFIX = "/api/v1"
logger = setup_logger("payment_route")

payment_service = CashfreePaymentService()

# ---------------------------------
# Create Order
# ---------------------------------
@payment_bp.route(f"{API_PREFIX}/create-order", methods=["POST"])
def create_order():
    try:
        data = request.json or {}
        email = data.get("email")
        phone = data.get("phone")
        amount = data.get("amount")
        name = data.get("name")

        if not email or not phone or not amount:
            return jsonify({"error": "Email, phone, and amount are required"}), 400

        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400

        order_id, payment_session_id = payment_service.create_order(
            email=email,
            phone=phone,
            amount=amount,
            name=name,
            host_url=request.host_url
        )

        return jsonify({"order_id": order_id, "payment_session_id": payment_session_id}), 200

    except Exception as e:
        logger.exception("Error creating order")
        return jsonify({"error": str(e)}), 500

# ---------------------------------
# Payment Status (with transaction info)
# ---------------------------------
@payment_bp.route(f"{API_PREFIX}/payment-status")
def payment_status():
    order_id = request.args.get("order_id")
    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400

    try:
        order, payment = payment_service.fetch_order_with_payments(order_id)
        status = payment.get("payment_status", order.order_status)

        receipt_data = {
            "Email Address": order.customer_details.customer_email,
            "Mobile No": order.customer_details.customer_phone,
            "Transaction No": payment.get("cf_payment_id") or "N/A",
            "Transaction Date": payment.get("payment_time") or order.created_at,
            "Bank Ref No": payment.get("bank_reference") or "N/A",
            "Amount": f"₹{order.order_amount}",
            "Status": status,
            "Name": order.customer_details.customer_name
        }

        return jsonify({"order_id": order_id, "receipt_data": receipt_data}), 200

    except Exception as e:
        logger.exception(f"Error fetching payment status for order_id={order_id}")
        return jsonify({"error": str(e)}), 500


# ---------------------------------
# Webhook Handler
# ---------------------------------
@payment_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        signature = request.headers.get("x-webhook-signature")
        timestamp = request.headers.get("x-webhook-timestamp")
        raw_body = request.data.decode("utf-8")

        event_type, event_data = payment_service.verify_webhook(signature, raw_body, timestamp)
        logger.info(f"[Webhook] Received {event_type} for order {event_data.get('order_id')}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("Error in webhook handler")
        return jsonify({"error": str(e)}), 500

# ---------------------------------
# Success / Failure Pages
# ---------------------------------
@payment_bp.route("/success")
def success_page():
    order_id = request.args.get("order_id")
    if not order_id:
        return "Missing order_id", 400

    try:
        order, payment = payment_service.fetch_order_with_payments(order_id)
        status = payment.get("payment_status", order.order_status)

        if status == "SUCCESS" or status == "PAID":
            return render_template("payment/success.html", order=order, payment=payment)
        else:
            return render_template("payment/failure.html", order=order, payment=payment)

    except Exception as e:
        logger.exception(f"Error in success page for order_id={order_id}")
        return render_template("payment/failure.html", order_id=order_id, error=str(e)), 500

@payment_bp.route("/failure")
def failure_page():
    order_id = request.args.get("order_id")
    if not order_id:
        return "Missing order_id", 400
    return render_template("payment/failure.html", order_id=order_id)

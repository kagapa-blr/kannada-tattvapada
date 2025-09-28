import os
import uuid
import io
import warnings
from flask import Blueprint, render_template, request, jsonify, send_file
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
from weasyprint import HTML
from app.utils.logger import setup_logger

# ---------------------------------------------------
# Ignore Warnings
# ---------------------------------------------------
warnings.filterwarnings("ignore")

# ---------------------------------------------------
# Blueprint Setup
# ---------------------------------------------------
payment_bp = Blueprint(
    "payment",
    __name__,
    template_folder="templates/payment",
    url_prefix="/payment"
)

API_PREFIX = "/api/v1"
logger = setup_logger(name="payment_route")

# ---------------------------------------------------
# Cashfree Configuration
# ---------------------------------------------------
Cashfree.XClientId = os.getenv("CASHFREE_CLIENT_ID")
Cashfree.XClientSecret = os.getenv("CASHFREE_CLIENT_SECRET")
Cashfree.XEnvironment = Cashfree.SANDBOX if os.getenv("CASHFREE_ENV", "sandbox").lower() == "sandbox" else Cashfree.PRODUCTION
X_API_VERSION = "2023-08-01"

# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------
def generate_order_id():
    return f"order_{uuid.uuid4().hex[:12]}"

def generate_customer_id():
    return f"cust_{uuid.uuid4().hex[:6]}"

# ---------------------------------------------------
# Routes
# ---------------------------------------------------
# ----------------------------------------
# Updated Cashfree Routes with Failure
# ----------------------------------------

@payment_bp.route(f"{API_PREFIX}/create-order", methods=["POST"])
def create_order():
    try:
        data = request.json or {}
        email = data.get("email")
        phone = data.get("phone")

        if not email or not phone or not data.get("amount"):
            return jsonify({"error": "Email, phone, and amount are required"}), 400

        try:
            amount = float(data.get("amount"))
            if amount <= 0:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Amount must be a positive number"}), 400

        order_id = generate_order_id()
        customer = CustomerDetails(
            customer_id=generate_customer_id(),
            customer_name=data.get("name", "Guest User"),
            customer_email=email,
            customer_phone=phone
        )

        order_meta = OrderMeta(
            return_url=f"{request.host_url}payment/success?order_id={order_id}",
            failure_url=f"{request.host_url}payment/failure?order_id={order_id}",
            notify_url=f"{request.host_url}payment/webhook"
        )

        create_order_request = CreateOrderRequest(
            order_id=order_id,
            order_amount=amount,
            order_currency="INR",
            customer_details=customer,
            order_meta=order_meta,
            order_note="Flask Cashfree Hosted Checkout"
        )

        api_response = Cashfree().PGCreateOrder(X_API_VERSION, create_order_request)
        order_data = getattr(api_response, "data", None)
        payment_session_id = getattr(order_data, "payment_session_id", None)
        if not payment_session_id:
            payment_session_id = getattr(api_response, "response", {}).get("payment_session_id")

        if not payment_session_id:
            logger.error("Payment Session ID not found in Cashfree response")
            return jsonify({"error": "Payment Session ID not found"}), 500

        return jsonify({"payment_session_id": payment_session_id, "order_id": order_id}), 200

    except Exception as e:
        logger.exception("Error in create_order")
        return jsonify({"error": str(e)}), 500


@payment_bp.route("/success")
def success_page():
    order_id = request.args.get("order_id")
    if not order_id:
        return "Missing order_id", 400
    return render_template("payment/success.html", order_id=order_id)


@payment_bp.route("/failure")
def failure_page():
    """
    Render payment failure page.
    """
    order_id = request.args.get("order_id")
    if not order_id:
        return "Missing order_id", 400
    return render_template("payment/failure.html", order_id=order_id)


@payment_bp.route(f"{API_PREFIX}/payment-status")
def payment_status():
    order_id = request.args.get("order_id")
    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400

    try:
        api_response = Cashfree().PGFetchOrder(
            x_api_version=X_API_VERSION,
            order_id=order_id
        )
        order = getattr(api_response, "data", None)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        receipt_data = {
            "Email Address": order.customer_details.customer_email,
            "Mobile No": order.customer_details.customer_phone,
            "Transaction No": getattr(order, "cf_payment_id", "N/A"),
            "Transaction Date": getattr(order, "order_created_time", "N/A"),
            "Bank Ref No": getattr(order, "bank_reference", "N/A"),
            "Amount": f"₹{order.order_amount}",
            "Status": getattr(order, "order_status", "N/A"),
            "Name": order.customer_details.customer_name
        }

        return jsonify({"order_id": order_id, "receipt_data": receipt_data}), 200

    except Exception as e:
        logger.exception(f"Error fetching payment status for order_id={order_id}")
        return jsonify({"error": str(e)}), 500



@payment_bp.route("/receipt/<order_id>")
def generate_receipt(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return "Order not found", 404

    html_content = render_template("payment/receipt_template.html", order=order)

    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)

    return send_file(
        pdf_file,
        as_attachment=True,
        download_name=f"receipt_{order_id}.pdf",
        mimetype="application/pdf"
    )
@payment_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.json
        logger.info(f"[Webhook] Received: {payload}")
        # Optional: handle failed payments
        if payload.get("order_status") == "FAILED":
            logger.warning(f"Payment failed for order {payload.get('order_id')}")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("Error in webhook handler")
        return jsonify({"error": str(e)}), 500

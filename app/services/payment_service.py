import os
import uuid

import requests
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta

from app.services.shopping_user_service import ShoppingOrderService
from app.utils.logger import setup_logger


class CashfreePaymentService:
    def __init__(self, environment: str = None, api_version: str = "2023-08-01"):
        self.logger = setup_logger("CashfreePaymentService")

        Cashfree.XClientId = os.getenv("CASHFREE_CLIENT_ID")
        Cashfree.XClientSecret = os.getenv("CASHFREE_CLIENT_SECRET")
        env = environment or os.getenv("CASHFREE_ENV", "sandbox")
        Cashfree.XEnvironment = Cashfree.SANDBOX if env.lower() == "sandbox" else Cashfree.PRODUCTION

        self.api_version = api_version
        self.client = Cashfree()

    @staticmethod
    def generate_order_id() -> str:
        return f"order_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_customer_id() -> str:
        return f"cust_{uuid.uuid4().hex[:6]}"

    def create_order(self, email: str, phone: str, amount: float, name: str = None,
                     host_url: str = None, **kwargs):
        """Create a Cashfree order and save full details locally."""
        order_id = self.generate_order_id()

        # Customer info
        customer = CustomerDetails(
            customer_id=self.generate_customer_id(),
            customer_name=name or "Guest User",
            customer_email=email,
            customer_phone=phone
        )

        # Order meta
        order_meta = OrderMeta(
            return_url=f"{host_url}payment/success?order_id={order_id}" if host_url else None,
            notify_url=f"{host_url}payment/webhook" if host_url else None
        )

        create_order_request = CreateOrderRequest(
            order_id=order_id,
            order_amount=amount,
            order_currency="INR",
            customer_details=customer,
            order_meta=order_meta,
            order_note=kwargs.get("order_note", "Cashfree Hosted Checkout")
        )

        # Call Cashfree API
        api_response = self.client.PGCreateOrder(self.api_version, create_order_request)
        order_data = getattr(api_response, "data", None)
        payment_session_id = getattr(order_data, "payment_session_id", None)

        if not payment_session_id:
            self.logger.error(f"Cashfree response missing payment_session_id: {api_response}")
            raise Exception("Payment Session ID not found")

        # Save order in DB
        ShoppingOrderService.create_order(
            email=email,
            order_number=order_id,
            total_amount=amount,
            status="CREATED",
            payment_method=kwargs.get("payment_method"),
            shipping_address_id=kwargs.get("shipping_address_id"),
            notes=kwargs.get("notes"),
            user_info=kwargs.get("user_info"),
            address_info=kwargs.get("address_info"),
            items=kwargs.get("items")
        )

        return order_id, payment_session_id

    def fetch_order_with_payments(self, order_id: str):
        """Fetch Cashfree order + payment details."""
        order_response = self.client.PGFetchOrder(self.api_version, order_id=order_id)
        order = getattr(order_response, "data", None)
        if not order:
            raise Exception("Order not found in Cashfree")

        # Fetch payments
        env = os.getenv("CASHFREE_ENV", "sandbox").lower()
        base_url = "https://sandbox.cashfree.com" if env == "sandbox" else "https://api.cashfree.com"
        payments_url = f"{base_url}/pg/orders/{order_id}/payments"

        headers = {
            "x-client-id": os.getenv("CASHFREE_CLIENT_ID"),
            "x-client-secret": os.getenv("CASHFREE_CLIENT_SECRET"),
            "x-api-version": self.api_version
        }

        verify_ssl = False if env == "sandbox" else True
        payments_response = requests.get(payments_url, headers=headers, verify=verify_ssl)

        payment = {}
        if payments_response.status_code == 200:
            payments = payments_response.json()
            payment = payments[0] if isinstance(payments, list) and payments else {}

        payment_info = {
            "cf_payment_id": payment.get("cf_payment_id"),
            "payment_status": payment.get("payment_status"),
            "bank_reference": payment.get("bank_reference"),
            "payment_amount": payment.get("payment_amount"),
            "payment_currency": payment.get("payment_currency"),
            "payment_time": payment.get("payment_time"),
            "payment_method": payment.get("payment_method"),
        }

        return order, payment_info

    def verify_webhook(self, signature: str, raw_body: str, timestamp: str):
        """Verify Cashfree webhook and update local order."""
        webhook_event, err = self.client.PGVerifyWebhookSignature(signature, raw_body, timestamp)
        if err:
            raise Exception(f"Invalid webhook signature: {err}")

        event_obj = webhook_event.get("object", {})
        event_data = event_obj.get("data", {})
        cf_order_id = event_data.get("order_id")
        payment_status = event_data.get("payment_status")

        if cf_order_id:
            ShoppingOrderService.update_order(
                order_id=cf_order_id,
                status=payment_status or "UNKNOWN",
                payment_method=event_data.get("payment_method"),
                notes=event_data.get("notes")
            )

        return event_obj.get("type"), event_data

from flask import Blueprint, request, jsonify, render_template
from app.services.shopping_user_service import ShoppingUserService, ShoppingUserAddressService, ShoppingOrderService
from app.utils.logger_config import get_logger

shopping_user_bp = Blueprint(
    "shopping_user",
    __name__,
    template_folder="templates/shopping",
    url_prefix="/shopping"
)
API_PREFIX = "/api/v1"
WEB_UI_PREFIX = "/"
logger = get_logger(name="shopping_route")

# User Profile Page
@shopping_user_bp.route(WEB_UI_PREFIX, methods=["GET"])
def shopping_page():
    return render_template("shopping/user-profile.html")

# --- ShoppingUser REST API ---
@shopping_user_bp.route(f"{API_PREFIX}/users/<string:email>", methods=["GET"])
def get_user(email):
    result = ShoppingUserService.get_user_by_email(email=email)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/users/", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email is required.", "data": None}), 400
    result = ShoppingUserService.create_user(
        email=email,
        name=data.get("name"),
        phone=data.get("phone"),
        gender=data.get("gender"),
        date_of_birth=data.get("date_of_birth"),
        preferred_language=data.get("preferred_language")
    )
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/users/<email>", methods=["PUT"])
def update_user(email):
    data = request.get_json() or {}
    print('user data', data)
    result = ShoppingUserService.update_user(email=email, **data)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/users/<string:email>", methods=["DELETE"])
def delete_user(email):
    result = ShoppingUserService.delete_user(email=email)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/users/", methods=["GET"])
def list_users():
    limit = request.args.get("limit", default=100, type=int)
    offset = request.args.get("offset", default=0, type=int)
    result = ShoppingUserService.list_users(limit=limit, offset=offset)
    return jsonify(result)

# --- Address REST API ---
@shopping_user_bp.route(f"{API_PREFIX}/users/<string:email>/addresses", methods=["GET"])
def list_addresses(email):
    result = ShoppingUserAddressService.list_addresses(email=email)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/users/<string:email>/addresses", methods=["POST"])
def add_address(email):
    data = request.get_json() or {}
    result = ShoppingUserAddressService.create_address(email=email, **data)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/addresses/<int:address_id>", methods=["PUT"])
def update_address(address_id):
    data = request.get_json() or {}
    result = ShoppingUserAddressService.update_address(address_id=address_id, **data)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/addresses/<int:address_id>", methods=["DELETE"])
def delete_address(address_id):
    result = ShoppingUserAddressService.delete_address(address_id=address_id)
    return jsonify(result)

# --- Orders REST API ---
@shopping_user_bp.route(f"{API_PREFIX}/users/<string:email>/orders", methods=["GET"])
def list_orders(email):
    result = ShoppingOrderService.list_orders(email=email)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/users/<string:email>/orders", methods=["POST"])
def create_order(email):
    data = request.get_json() or {}
    # order_number/total_amount are required
    if "order_number" not in data or "total_amount" not in data:
        return jsonify({"success": False, "message": "order_number and total_amount are required.", "data": None}), 400
    result = ShoppingOrderService.create_order(
        email=email,
        order_number=data["order_number"],
        total_amount=data["total_amount"],
        status=data.get("status"),
        payment_method=data.get("payment_method"),
        shipping_address_id=data.get("shipping_address_id"),
        notes=data.get("notes")
    )
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.get_json() or {}
    result = ShoppingOrderService.update_order(order_id=order_id, **data)
    return jsonify(result)

@shopping_user_bp.route(f"{API_PREFIX}/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    result = ShoppingOrderService.delete_order(order_id=order_id)
    return jsonify(result)

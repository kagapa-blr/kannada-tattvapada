import os
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
from app.services.shopping_books_service import ShoppingBooksService, allowed_file

UPLOAD_FOLDER = "uploads/covers"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DEFAULT_COVER_URL = "/uploads/covers/default.jpg"

service = ShoppingBooksService()

WEB_PREFIX = "/books"
API_PREFIX = "/api"

shopping_books_bp = Blueprint(
    "shopping_books",
    __name__,
    template_folder="templates/shoppingbooks",
    url_prefix=WEB_PREFIX
)


@shopping_books_bp.route(f"{API_PREFIX}/", methods=["GET"])
def api_list_books():
    try:
        draw = int(request.args.get("draw", 1))
        start = int(request.args.get("start", 0))
        length = int(request.args.get("length", 10))
        search_value = request.args.get("search_word", "").strip()

        total_count, filtered_count, books = service.list_books(
            search_word=search_value,
            limit=length,
            offset=start
        )

        data = [{
            "id": b.id,
            "title": b.title,
            "subtitle": b.subtitle,
            "author_name": b.author_name,
            "description": b.description,
            "book_code": b.book_code,
            "catalog_number": b.catalog_number,
            "publisher_name": b.publisher_name,
            "publication_date": b.publication_date.isoformat() if b.publication_date else None,
            "number_of_pages": b.number_of_pages,
            "price": float(b.price),
            "discount_price": float(b.discount_price) if b.discount_price else None,
            "stock_quantity": b.stock_quantity,
            "cover_image_url": b.cover_image_url if b.cover_image_url else DEFAULT_COVER_URL,
            "rating": b.rating,
            "language": b.language,
            "created_at": b.created_at.isoformat(),
            "updated_at": b.updated_at.isoformat()
        } for b in books]

        return jsonify({
            "draw": draw,
            "recordsTotal": total_count,
            "recordsFiltered": filtered_count,
            "data": data
        })
    except Exception as e:
        current_app.logger.error(f"[Books] List failed: {str(e)}")
        return jsonify({"error": "Failed to list books", "details": str(e)}), 500


@shopping_books_bp.route(f"{API_PREFIX}/<int:book_id>", methods=["GET"])
def api_get_book(book_id):
    book = service.get_book_by_id(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({
        "id": book.id,
        "title": book.title,
        "subtitle": book.subtitle,
        "author_name": book.author_name,
        "description": book.description,
        "book_code": book.book_code,
        "catalog_number": book.catalog_number,
        "publisher_name": book.publisher_name,
        "publication_date": book.publication_date.isoformat() if book.publication_date else None,
        "number_of_pages": book.number_of_pages,
        "price": float(book.price),
        "discount_price": float(book.discount_price) if book.discount_price else None,
        "stock_quantity": book.stock_quantity,
        "cover_image_url": book.cover_image_url,
        "rating": book.rating,
        "language": book.language
    })


@shopping_books_bp.route(f"{API_PREFIX}/", methods=["POST"])
def api_create_book():
    data = request.form.to_dict() or request.json or {}
    cover_file = request.files.get("cover_file")

    if cover_file and not allowed_file(cover_file.filename):
        return jsonify({"error": "Invalid cover file type"}), 400

    book, error = service.create_book(cover_file=cover_file, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Book created", "id": book.id, "title": book.title})


@shopping_books_bp.route(f"{API_PREFIX}/<int:book_id>", methods=["PUT"])
def api_update_book(book_id):
    data = request.form.to_dict() or request.json or {}
    cover_file = request.files.get("cover_file")

    if cover_file and not allowed_file(cover_file.filename):
        return jsonify({"error": "Invalid cover file type"}), 400

    book, error = service.update_book(book_id, cover_file=cover_file, **data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Book updated", "id": book.id, "title": book.title})


@shopping_books_bp.route(f"{API_PREFIX}/<int:book_id>", methods=["DELETE"])
def api_delete_book(book_id):
    success, error = service.delete_book(book_id)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Book deleted"})


@shopping_books_bp.route(f"{API_PREFIX}/bulk-upload", methods=["POST"])
def api_bulk_upload():
    csv_file = request.files.get("file")
    if not csv_file:
        return jsonify({"error": "CSV file is required"}), 400
    if not csv_file.filename.endswith(".csv"):
        return jsonify({"error": "Only CSV files allowed"}), 400

    temp_path = os.path.join(UPLOAD_FOLDER, secure_filename(csv_file.filename))
    csv_file.save(temp_path)

    uploaded_books, errors = service.bulk_upload_from_csv(temp_path)
    os.remove(temp_path)

    return jsonify({
        "uploaded_count": len(uploaded_books),
        "books": [{"id": b.id, "title": b.title} for b in uploaded_books],
        "errors": errors
    })


@shopping_books_bp.route(f"{API_PREFIX}/autofill", methods=["POST"])
def api_auto_create_from_tatvapada():
    payload = request.form or request.json or {}
    default_price_str = str(payload.get("default_price", "0")).strip()

    try:
        default_price = float(default_price_str)
    except ValueError:
        return jsonify({"error": "Invalid default price"}), 400

    created, skipped = service.auto_create_from_tatvapada(default_price)

    return jsonify({
        "message": "Auto-create from Tatvapada completed",
        "created": created,
        "skipped": skipped
    })


@shopping_books_bp.route("/admin", methods=["GET"])
def web_list_books_admin():
    return render_template("shopping/shoppingbooks-admin.html")

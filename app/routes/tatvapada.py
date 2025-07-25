"""
Tatvapada routes: expose endpoints for CRUD operations (API + Web Form).
"""

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template
)

from app.services.tatvapada_service import TatvapadaService
from app.utils.logger import setup_logger

tatvapada_bp = Blueprint("tatvapada", __name__)
logger = setup_logger("tatvapada_routes", "tatvapada_routes.log")
tatvapada_service = TatvapadaService()  # hardcoded service instance

# =======================
# API JSON ROUTES
# =======================

@tatvapada_bp.route("/api/tatvapada/add", methods=["POST"])
def add_tatvapada_api():
    data = request.get_json()
    logger.info(f"Received JSON request: {data}")

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    if tatvapada_service.exists_by_tatvapadakosha(data.get("tatvapadakosha")):
        return jsonify({"error": "Duplicate tatvapadakosha not allowed"}), 409

    result = tatvapada_service.insert_tatvapada(data)
    if result:
        return jsonify({"message": "Tatvapada inserted", "id": result.id}), 201
    return jsonify({"error": "Insert failed"}), 500


@tatvapada_bp.route("/api/tatvapada/all", methods=["GET"])
def list_all_tatvapadas_api():
    records = tatvapada_service.get_all_tatvapada()
    return jsonify([
        {k: v for k, v in r.__dict__.items() if not k.startswith("_")}
        for r in records
    ])


@tatvapada_bp.route("/api/tatvapada/sankya/<string:sankya>", methods=["GET"])
def get_tatvapada_by_sankya_api(sankya):
    results = tatvapada_service.get_by_sankya(sankya)
    return jsonify([
        {k: v for k, v in r.__dict__.items() if not k.startswith("_")}
        for r in results
    ])


@tatvapada_bp.route("/api/tatvapada/search", methods=["GET"])
def search_tatvapada_by_keyword_api():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    results = tatvapada_service.search_by_keyword(keyword)
    return jsonify([
        {k: v for k, v in r.__dict__.items() if not k.startswith("_")}
        for r in results
    ])

# ===========================
# New API Endpoints (Lookups)
# ===========================

@tatvapada_bp.route("/api/tatvapada/kosha-mapping", methods=["GET"])
def get_kosha_mapping_api():
    mapping = tatvapada_service.get_all_tatvapadakosha_mapping()
    return jsonify(mapping)


@tatvapada_bp.route("/api/tatvapada/samputa-by-kosha", methods=["GET"])
def get_samputa_by_kosha_api():
    tatvapadakosha = request.args.get("tatvapadakosha")
    if not tatvapadakosha:
        return jsonify({"error": "tatvapadakosha is required"}), 400

    samputas = tatvapada_service.get_samputa_by_tatvapadakosha(tatvapadakosha)
    return jsonify(samputas)


@tatvapada_bp.route("/api/tatvapada/sankhye-by-samputa", methods=["GET"])
def get_sankhye_by_samputa_api():
    try:
        samputa_sankhye = int(request.args.get("samputa_sankhye", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Valid samputa_sankhye is required"}), 400

    sankhyes = tatvapada_service.get_tatvapada_sankhye_by_samputa(samputa_sankhye)
    return jsonify(sankhyes)


@tatvapada_bp.route("/api/tatvapada/by-sankhye", methods=["GET"])
def get_tatvapada_by_sankhye_api():
    sankhye = request.args.get("tatvapada_sankhye")
    if not sankhye:
        return jsonify({"error": "tatvapada_sankhye is required"}), 400

    entry = tatvapada_service.get_tatvapada_by_sankhye(sankhye)
    if not entry:
        return jsonify({"error": "Not found"}), 404

    return jsonify({k: v for k, v in entry.__dict__.items() if not k.startswith("_")})


# =======================
# WEB FORM ROUTES (HTML)
# =======================

@tatvapada_bp.route("/tatvapada", methods=["GET"])
def tatvapada_list_page():
    data = tatvapada_service.get_all_tatvapada()
    return render_template("index.html", data=data)


@tatvapada_bp.route("/tatvapada/add", methods=["GET", "POST"])
def add_tatvapada_form():
    if request.method == "POST":
        form_data = request.get_json() if request.is_json else request.form.to_dict()

        if not form_data.get("tatvapadakosha"):
            return jsonify({"error": "ತತ್ತ್ವಪದಕೋಶ ಅಗತ್ಯವಿದೆ."}), 400

        # Safe casting
        form_data["tatvapadakosha_sankhye"] = int(form_data.get("tatvapadakosha_sankhye", 1) or 1)
        form_data["samputa_sankhye"] = int(form_data.get("samputa_sankhye", 0) or 0)

        if tatvapada_service.exists_by_tatvapadakosha(form_data.get("tatvapadakosha")):
            return jsonify({"error": "ಈ ತತ್ತ್ವಪದಕೋಶ ಈಗಾಗಲೇ ಅಸ್ತಿತ್ವದಲ್ಲಿದೆ."}), 409

        success = tatvapada_service.insert_tatvapada(form_data)
        if success:
            return jsonify({"message": "ತತ್ತ್ವಪದ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ."})
        else:
            return jsonify({"error": "ದಾಖಲಾತಿ ವಿಫಲವಾಗಿದೆ."}), 500

    return render_template("insert.html")

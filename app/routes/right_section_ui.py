from flask import Blueprint, render_template
from flask import Blueprint, request, jsonify
right_section_bp = Blueprint(
    'right_section', __name__,
    template_folder='templates/right_section',
    url_prefix='/right-section'  # ✅ Add prefix here
)

# ===== Routes with specific methods =====

@right_section_bp.route('/tatvapada_suchi', methods=['GET'])
def tatvapada_suchi():
    return render_template('right_section/tatvapada_suchi.html')

@right_section_bp.route('/arthakosha', methods=['GET'])
def arthakosha():
    return render_template('right_section/arthakosha.html')

@right_section_bp.route('/tippani', methods=['GET'])
def tippani():
    return render_template('right_section/tippani.html')


@right_section_bp.route('/tatvapadakara_vivarane', methods=['GET'])
def tatvapadakara_vivarane():
    return render_template('right_section/tatvapadakara_vivarane.html')

@right_section_bp.route('/pradhana_sampadakaru_nudi', methods=['GET'])
def pradhana_sampadakaru_nudi():
    return render_template('right_section/pradhana_sampadakaru_nudi.html')

@right_section_bp.route('/user_document', methods=['GET'])
def samputa_sampadakaru_nudi():
    return render_template('right_section/user_document.html')

@right_section_bp.route('/paramarshana_sahitya', methods=['GET'])
def paramarshana_sahitya():
    return render_template('right_section/paramarshana_sahitya.html')



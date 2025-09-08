from flask import Blueprint
from flask import render_template

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
    return render_template('right_section/paribhashika_padavivarana.html')


@right_section_bp.route('/tatvapadakara_vivarane', methods=['GET'])
def tatvapadakara_vivarane():
    return render_template('right_section/tatvapadakara_vivarane.html')


@right_section_bp.route('/sampadakaru_nudi', methods=['GET'])
def samputa_sampadakaru_nudi():
    return render_template('right_section/sampadakara_nudi.html')


@right_section_bp.route('/shodhane', methods=['GET'])
def shodhane():
    return render_template('right_section/shodhane.html')


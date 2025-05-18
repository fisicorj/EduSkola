from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Instituicao

painel_bp = Blueprint('painel', __name__, url_prefix='/painel')

@painel_bp.route('/')
@login_required
def painel():
    total = Instituicao.query.count()
    return render_template('painel/painel.html', total=total)
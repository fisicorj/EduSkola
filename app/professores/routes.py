from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.auth.decorators import role_required
from app import db
from app.models import Professor, Disciplina

professores_bp = Blueprint('professores', __name__, url_prefix='/professores')

@professores_bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # quantidade de professores por página
    pagination = Professor.query.paginate(page=page, per_page=per_page)
    
    return render_template(
        'professores/listar.html',
        professores=pagination.items,
        pagination=pagination
    )

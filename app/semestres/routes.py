from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_required
from app import db
from app.models import SemestreLetivo

semestres_bp = Blueprint('semestres', __name__, url_prefix='/semestres')

@semestres_bp.route('/')
@login_required
def listar():
    semestres = SemestreLetivo.query.all()
    return render_template('semestres/listar.html', semestres=semestres)

from datetime import datetime

@semestres_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        ano = int(request.form['ano'])
        semestre = int(request.form['semestre'])
        
        # ✅ Conversão das datas
        data_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date()
        data_fim = datetime.strptime(request.form['data_fim'], '%Y-%m-%d').date()

        semestre_letivo = SemestreLetivo(
            ano=ano,
            semestre=semestre,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        db.session.add(semestre_letivo)
        db.session.commit()
        flash('Semestre cadastrado com sucesso.', 'success')
        return redirect(url_for('semestres.listar'))
        
    return render_template('semestres/form.html')

@semestres_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    semestre = SemestreLetivo.query.get_or_404(id)

    if request.method == 'POST':
        semestre.ano = int(request.form['ano'])
        semestre.semestre = int(request.form['semestre'])

        # ✅ Conversão das datas
        semestre.data_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date()
        semestre.data_fim = datetime.strptime(request.form['data_fim'], '%Y-%m-%d').date()

        db.session.commit()
        flash('Semestre atualizado com sucesso.', 'success')
        return redirect(url_for('semestres.listar'))

    return render_template('semestres/form.html', titulo='Editar Semestre', semestre=semestre)


@semestres_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    semestre = SemestreLetivo.query.get_or_404(id)
    db.session.delete(semestre)
    db.session.commit()
    flash('Semestre excluído com sucesso!', 'success')
    return redirect(url_for('semestres.listar'))

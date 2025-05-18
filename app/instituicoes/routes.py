from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Instituicao

inst_bp = Blueprint('instituicoes', __name__, url_prefix='/instituicoes')

@inst_bp.route('/')
@login_required
def listar():
    instituicoes = Instituicao.query.all()
    return render_template('instituicoes/listar.html', instituicoes=instituicoes)

@inst_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if request.method == 'POST':
        i = Instituicao(
            nome=request.form['nome'],
            sigla=request.form['sigla'],
            cidade=request.form['cidade'],
            tipo=request.form['tipo']
        )
        db.session.add(i)
        db.session.commit()
        flash('Instituição cadastrada com sucesso.', 'success')
        return redirect(url_for('instituicoes.listar'))
    return render_template('instituicoes/form.html', titulo='Nova Instituição')

@inst_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    i = Instituicao.query.get_or_404(id)
    if request.method == 'POST':
        i.nome = request.form['nome']
        i.sigla = request.form['sigla']
        i.cidade = request.form['cidade']
        i.tipo = request.form['tipo']
        db.session.commit()
        flash('Instituição atualizada.', 'info')
        return redirect(url_for('instituicoes.listar'))
    return render_template('instituicoes/form.html', instituicao=i, titulo='Editar Instituição')

@inst_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    i = Instituicao.query.get_or_404(id)
    db.session.delete(i)
    db.session.commit()
    flash('Instituição excluída.', 'danger')
    return redirect(url_for('instituicoes.listar'))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Avaliacao, Turma, Disciplina

avaliacoes_bp = Blueprint('avaliacoes', __name__, url_prefix='/avaliacoes')

@avaliacoes_bp.route('/')
@login_required
def listar():
    avaliacoes = Avaliacao.query.all()
    return render_template('avaliacoes/listar.html', avaliacoes=avaliacoes)

@avaliacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    if request.method == 'POST':
        nome = request.form['nome']
        peso = float(request.form['peso'])
        turma_id = request.form['turma_id']
        disciplina_id = request.form['disciplina_id']

        avaliacao = Avaliacao(
            nome=nome,
            peso=peso,
            turma_id=turma_id,
            disciplina_id=disciplina_id
        )
        db.session.add(avaliacao)
        db.session.commit()
        flash('Avaliação cadastrada com sucesso.', 'success')
        return redirect(url_for('avaliacoes.listar'))

    return render_template('avaliacoes/form.html', titulo='Nova Avaliação', turmas=turmas, disciplinas=disciplinas)

@avaliacoes_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    avaliacao = Avaliacao.query.get_or_404(id)
    db.session.delete(avaliacao)
    db.session.commit()
    flash('Avaliação excluída.', 'danger')
    return redirect(url_for('avaliacoes.listar'))

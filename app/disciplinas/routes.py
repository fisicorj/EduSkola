from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Disciplina, Turma, Professor

disciplinas_bp = Blueprint('disciplinas', __name__, url_prefix='/disciplinas')

@disciplinas_bp.route('/')
@login_required
def listar():
    disciplinas = Disciplina.query.all()
    return render_template('disciplinas/listar.html', disciplinas=disciplinas)

@disciplinas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if request.method == 'POST':
        d = Disciplina(
            nome=request.form['nome'],
            sigla=request.form['sigla'],
            turma_id=request.form['turma_id'],
            professor_id=request.form['professor_id']
        )
        db.session.add(d)
        db.session.commit()
        flash('Disciplina cadastrada com sucesso.', 'success')
        return redirect(url_for('disciplinas.listar'))
    turmas = Turma.query.all()
    professores = Professor.query.all()
    return render_template('disciplinas/form.html', titulo='Nova Disciplina', turmas=turmas, professores=professores)

@disciplinas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    d = Disciplina.query.get_or_404(id)
    if request.method == 'POST':
        d.nome = request.form['nome']
        d.sigla = request.form['sigla']
        d.turma_id = request.form['turma_id']
        d.professor_id = request.form['professor_id']
        db.session.commit()
        flash('Disciplina atualizada.', 'info')
        return redirect(url_for('disciplinas.listar'))
    turmas = Turma.query.all()
    professores = Professor.query.all()
    return render_template('disciplinas/form.html', disciplina=d, titulo='Editar Disciplina', turmas=turmas, professores=professores)

@disciplinas_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    d = Disciplina.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash('Disciplina excluída.', 'danger')
    return redirect(url_for('disciplinas.listar'))
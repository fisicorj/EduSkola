from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Aluno, Turma

alunos_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

@alunos_bp.route('/')
@login_required
def listar():
    alunos = Aluno.query.all()
    return render_template('alunos/listar.html', alunos=alunos)

@alunos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    turmas = Turma.query.all()
    if request.method == 'POST':
        nome      = request.form['nome']
        email     = request.form['email']
        matricula = request.form['matricula']
        turma_id  = request.form['turma_id']
        # Validação simples: matrícula única
        if Aluno.query.filter_by(matricula=matricula).first():
            flash('Matrícula já cadastrada.', 'danger')
            return redirect(url_for('alunos.novo'))
        aluno = Aluno(
            nome=nome,
            email=email,
            matricula=matricula,
            turma_id=turma_id
        )
        db.session.add(aluno)
        db.session.commit()
        flash('Aluno cadastrado com sucesso.', 'success')
        return redirect(url_for('alunos.listar'))
    return render_template('alunos/form.html', titulo='Novo Aluno', turmas=turmas)

@alunos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    aluno = Aluno.query.get_or_404(id)
    turmas = Turma.query.all()
    if request.method == 'POST':
        aluno.nome      = request.form['nome']
        aluno.email     = request.form['email']
        aluno.matricula = request.form['matricula']
        aluno.turma_id  = request.form['turma_id']
        db.session.commit()
        flash('Aluno atualizado com sucesso.', 'info')
        return redirect(url_for('alunos.listar'))
    return render_template('alunos/form.html', titulo='Editar Aluno', aluno=aluno, turmas=turmas)

@alunos_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    aluno = Aluno.query.get_or_404(id)
    db.session.delete(aluno)
    db.session.commit()
    flash('Aluno excluído com sucesso.', 'danger')
    return redirect(url_for('alunos.listar'))

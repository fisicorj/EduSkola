from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Aluno, Turma, SemestreLetivo

alunos_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

from app.models import Aluno, Turma, Instituicao, SemestreLetivo

@alunos_bp.route('/')
@login_required
def listar():
    turma_id = request.args.get('turma_id', type=int)
    instituicao_id = request.args.get('instituicao_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)

    turmas = Turma.query.all()
    instituicoes = Instituicao.query.all()
    semestres = SemestreLetivo.query.all()

    alunos_query = Aluno.query

    if turma_id:
        alunos_query = alunos_query.filter_by(turma_id=turma_id)
    elif semestre_id:
        alunos_query = alunos_query.join(Turma).filter(Turma.semestre_letivo_id == semestre_id)

    if instituicao_id:
        alunos_query = alunos_query.join(Turma).filter(Turma.instituicao_id == instituicao_id)

    alunos = alunos_query.all()

    return render_template('alunos/listar.html', alunos=alunos, turmas=turmas,
                           instituicoes=instituicoes, semestres=semestres,
                           turma_id=turma_id, instituicao_id=instituicao_id, semestre_id=semestre_id)


@alunos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    turmas = Turma.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        matricula = request.form['matricula']
        turma_id = request.form['turma_id']
        semestre_letivo_id = request.form['semestre_letivo_id']

        if Aluno.query.filter_by(matricula=matricula).first():
            flash('Matrícula já cadastrada.', 'danger')
            return redirect(url_for('alunos.novo'))

        aluno = Aluno(
            nome=nome,
            email=email,
            matricula=matricula,
            turma_id=turma_id,
            semestre_letivo_id=semestre_letivo_id
        )
        db.session.add(aluno)
        db.session.commit()
        flash('Aluno cadastrado com sucesso.', 'success')
        return redirect(url_for('alunos.listar'))

    return render_template('alunos/form.html', titulo='Novo Aluno', turmas=turmas, semestres=semestres)


@alunos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    aluno = Aluno.query.get_or_404(id)
    turmas = Turma.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        aluno.nome = request.form['nome']
        aluno.email = request.form['email']
        aluno.matricula = request.form['matricula']
        aluno.turma_id = request.form['turma_id']
        aluno.semestre_letivo_id = request.form['semestre_letivo_id']
        db.session.commit()
        flash('Aluno atualizado com sucesso.', 'info')
        return redirect(url_for('alunos.listar'))

    return render_template('alunos/form.html', titulo='Editar Aluno', aluno=aluno, turmas=turmas, semestres=semestres)


@alunos_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    aluno = Aluno.query.get_or_404(id)
    db.session.delete(aluno)
    db.session.commit()
    flash('Aluno excluído com sucesso!', 'success')
    return redirect(url_for('alunos.listar'))

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auth.decorators import role_required
from app import db
from app.models import Turma, Instituicao, Curso, SemestreLetivo

turmas_bp = Blueprint('turmas', __name__, url_prefix='/turmas')

from app.models import Turma, Instituicao, SemestreLetivo, Curso

@turmas_bp.route('/')
@login_required
def listar():
    semestre_id = request.args.get('semestre_id', type=int)
    instituicao_id = request.args.get('instituicao_id', type=int)
    turno = request.args.get('turno')

    semestres = SemestreLetivo.query.all()
    instituicoes = Instituicao.query.all()
    turnos = ["Manhã", "Tarde", "Noite"]

    turmas_query = Turma.query

    if semestre_id:
        turmas_query = turmas_query.filter_by(semestre_letivo_id=semestre_id)

    if instituicao_id:
        turmas_query = turmas_query.filter_by(instituicao_id=instituicao_id)

    if turno:
        turmas_query = turmas_query.filter_by(turno=turno)

    turmas = turmas_query.all()

    return render_template('turmas/listar.html', turmas=turmas, semestres=semestres, 
                           instituicoes=instituicoes, turnos=turnos,
                           semestre_id=semestre_id, instituicao_id=instituicao_id, turno_sel=turno)



@turmas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    cursos = Curso.query.all()
    instituicoes = Instituicao.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        t = Turma(
            nome=request.form['nome'],
            codigo=request.form['codigo'],
            turno=request.form['turno'],
            curso_id=request.form['curso_id'],
            instituicao_id=request.form['instituicao_id'],
            semestre_letivo_id=request.form['semestre_letivo_id']  
        )
        db.session.add(t)
        db.session.commit()
        flash('Turma cadastrada com sucesso.', 'success')
        return redirect(url_for('turmas.listar'))

    return render_template('turmas/form.html', titulo='Nova Turma', cursos=cursos, instituicoes=instituicoes, semestres=semestres)

from app.models import SemestreLetivo

@turmas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    turma = Turma.query.get_or_404(id)
    cursos = Curso.query.all()
    instituicoes = Instituicao.query.all()
    semestres = SemestreLetivo.query.all()  # ✅ Aqui!

    if request.method == 'POST':
        turma.nome = request.form['nome']
        turma.codigo = request.form['codigo']
        turma.turno = request.form['turno']
        turma.curso_id = request.form['curso_id']
        turma.instituicao_id = request.form['instituicao_id']
        turma.semestre_letivo_id = request.form['semestre_letivo_id']
        db.session.commit()
        flash('Turma atualizada com sucesso.', 'success')
        return redirect(url_for('turmas.listar'))

    return render_template('turmas/form.html', turma=turma, cursos=cursos, instituicoes=instituicoes, semestres=semestres)

@turmas_bp.route('/minhas')
@login_required
@role_required('professor')
def minhas_turmas():
    disciplinas = Disciplina.query.filter_by(professor_id=current_user.id).all()
    turmas = list({disciplina.turma for disciplina in disciplinas})  # Set para evitar repetição
    return render_template('turmas/minhas.html', turmas=turmas)


@turmas_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    t = Turma.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Turma excluída.', 'danger')
    return redirect(url_for('turmas.listar'))
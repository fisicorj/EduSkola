from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Disciplina, Turma, Professor, SemestreLetivo

disciplinas_bp = Blueprint('disciplinas', __name__, url_prefix='/disciplinas')

@disciplinas_bp.route('/')
@login_required
def listar():
    from app.models import Instituicao

    turma_id = request.args.get('turma_id', type=int)
    instituicao_id = request.args.get('instituicao_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)

    turmas = Turma.query.all()
    professores = Professor.query.all()
    semestres = SemestreLetivo.query.all()
    instituicoes = Instituicao.query.all()

    disciplinas_query = Disciplina.query

    if turma_id:
        disciplinas_query = disciplinas_query.filter_by(turma_id=turma_id)

    if semestre_id:
        disciplinas_query = disciplinas_query.filter_by(semestre_letivo_id=semestre_id)

    if instituicao_id:
        disciplinas_query = disciplinas_query.join(Turma).filter(Turma.instituicao_id == instituicao_id)

    disciplinas = disciplinas_query.all()

    return render_template('disciplinas/listar.html',
                           disciplinas=disciplinas,
                           turmas=turmas,
                           professores=professores,
                           semestres=semestres,
                           instituicoes=instituicoes,
                           turma_id=turma_id,
                           semestre_id=semestre_id,
                           instituicao_id=instituicao_id)


@disciplinas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    turmas = Turma.query.all()
    professores = Professor.query.all()
    semestres = SemestreLetivo.query.all()
    
    if request.method == 'POST':
        d = Disciplina(
            nome=request.form['nome'],
            sigla=request.form['sigla'],
            turma_id=request.form['turma_id'],
            professor_id=request.form['professor_id'],
            semestre_letivo_id=request.form['semestre_letivo_id']  # ✅ agora envia o semestre
        )
        db.session.add(d)
        db.session.commit()
        flash('Disciplina cadastrada com sucesso.', 'success')
        return redirect(url_for('disciplinas.listar'))

    return render_template('disciplinas/form.html', titulo='Nova Disciplina', turmas=turmas, professores=professores, semestres=semestres)


@disciplinas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    d = Disciplina.query.get_or_404(id)
    turmas = Turma.query.all()
    professores = Professor.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        d.nome = request.form['nome']
        d.sigla = request.form['sigla']
        d.turma_id = request.form['turma_id']
        d.professor_id = request.form['professor_id']
        d.semestre_letivo_id = request.form['semestre_letivo_id']
        db.session.commit()
        flash('Disciplina atualizada.', 'info')
        return redirect(url_for('disciplinas.listar'))

    return render_template('disciplinas/form.html', disciplina=d, titulo='Editar Disciplina', turmas=turmas, professores=professores, semestres=semestres)

@disciplinas_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    d = Disciplina.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash('Disciplina excluída.', 'danger')
    return redirect(url_for('disciplinas.listar'))
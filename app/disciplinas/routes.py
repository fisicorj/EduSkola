from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Disciplina, Turma, Professor, SemestreLetivo, DisciplinaTurmaProfessor, Curso, CursoDisciplina
from app.auth.decorators import role_required
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload

disciplinas_bp = Blueprint('disciplinas', __name__, url_prefix='/disciplinas')

@disciplinas_bp.route('/')
@login_required
def listar():
    curso_id = request.args.get('curso_id', type=int)
    turma_id = request.args.get('turma_id', type=int)
    professor_id = request.args.get('professor_id', type=int)

    query = Disciplina.query

    # Fazer join com a tabela associativa apenas uma vez
    join_associacao = db.session.query(Disciplina).join(DisciplinaTurmaProfessor)

    if turma_id:
        join_associacao = join_associacao.filter(DisciplinaTurmaProfessor.turma_id == turma_id)

    if professor_id:
        join_associacao = join_associacao.filter(DisciplinaTurmaProfessor.professor_id == professor_id)

    if turma_id or professor_id:
        disciplinas = join_associacao.distinct().all()
    else:
        disciplinas = query.all()

    cursos = Curso.query.all()
    turmas = Turma.query.all()
    professores = Professor.query.all()

    return render_template('disciplinas/listar.html',
                       disciplinas=disciplinas,
                       cursos=cursos,
                       turmas=turmas,
                       professores=professores,
                       curso_id=curso_id,
                       turma_id=turma_id,
                       professor_id=professor_id)


@disciplinas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    turmas = Turma.query.all()
    professores = Professor.query.all()
    cursos = Curso.query.all()

    if request.method == 'POST':
        nome = request.form.get('nome')
        sigla = request.form.get('sigla')

        if not nome or not sigla:
            flash('Nome e sigla são obrigatórios.', 'danger')
            return redirect(url_for('disciplinas.nova'))

        disciplina = Disciplina(nome=nome, sigla=sigla)
        db.session.add(disciplina)
        db.session.commit()

        # Cursos
        curso_ids = request.form.getlist('cursos[]')
        for curso_id in curso_ids:
            assoc = CursoDisciplina(
                curso_id=int(curso_id),
                disciplina_id=disciplina.id
            )
            db.session.add(assoc)

        # Turmas e Professores
        turma_ids = request.form.getlist('turma_ids[]')
        for turma_id in turma_ids:
            turma = Turma.query.get(int(turma_id))
            semestre_id = turma.semestre_letivo_id
            professor_ids = request.form.getlist(f'professores_{turma_id}[]')
            for professor_id in professor_ids:
                assoc = DisciplinaTurmaProfessor(
                    disciplina_id=disciplina.id,
                    turma_id=int(turma_id),
                    professor_id=int(professor_id),
                    semestre_letivo_id=semestre_id
                )
                db.session.add(assoc)

        db.session.commit()
        flash('Disciplina criada com sucesso.', 'success')
        return redirect(url_for('disciplinas.listar'))

    return render_template('disciplinas/form.html',
                           titulo='Nova Disciplina',
                           turmas=turmas,
                           professores=professores,
                           cursos=cursos)



@disciplinas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    disciplina = Disciplina.query.get_or_404(id)
    turmas = Turma.query.all()
    professores = Professor.query.all()
    cursos = Curso.query.all()

    if request.method == 'POST':
        disciplina.nome = request.form.get('nome')
        disciplina.sigla = request.form.get('sigla')

        if not disciplina.nome or not disciplina.sigla:
            flash('Nome e sigla são obrigatórios.', 'danger')
            return redirect(url_for('disciplinas.editar', id=id))

        # Limpar antigos
        CursoDisciplina.query.filter_by(disciplina_id=disciplina.id).delete()
        DisciplinaTurmaProfessor.query.filter_by(disciplina_id=disciplina.id).delete()

        # Novos cursos
        curso_ids = request.form.getlist('cursos[]')
        for curso_id in curso_ids:
            assoc = CursoDisciplina(
                curso_id=int(curso_id),
                disciplina_id=disciplina.id
            )
            db.session.add(assoc)

        # Novas turmas e professores
        turma_ids = request.form.getlist('turma_ids[]')
        for turma_id in turma_ids:
            turma = Turma.query.get(int(turma_id))
            semestre_id = turma.semestre_letivo_id
            professor_ids = request.form.getlist(f'professores_{turma_id}[]')
            for professor_id in professor_ids:
                assoc = DisciplinaTurmaProfessor(
                    disciplina_id=disciplina.id,
                    turma_id=int(turma_id),
                    professor_id=int(professor_id),
                    semestre_letivo_id=semestre_id
                )
                db.session.add(assoc)

        db.session.commit()
        flash('Disciplina atualizada com sucesso.', 'info')
        return redirect(url_for('disciplinas.listar'))

    # Bloco necessário para preencher os checkboxes corretamente
    professores_ids_por_turma = {}
    associacoes = DisciplinaTurmaProfessor.query.filter_by(disciplina_id=disciplina.id).all()
    for assoc in associacoes:
        professores_ids_por_turma.setdefault(assoc.turma_id, []).append(assoc.professor_id)

    return render_template('disciplinas/form.html',
                           titulo='Editar Disciplina',
                           disciplina=disciplina,
                           turmas=turmas,
                           professores=professores,
                           cursos=cursos,
                           professores_ids_por_turma=professores_ids_por_turma)


@disciplinas_bp.route('/excluir/<int:id>', methods=['GET', 'POST'])
@login_required
def excluir(id):
    disciplina = Disciplina.query.get_or_404(id)
    CursoDisciplina.query.filter_by(disciplina_id=disciplina.id).delete()
    db.session.delete(disciplina)
    db.session.commit()
    flash('Disciplina excluída.', 'danger')
    return redirect(url_for('disciplinas.listar'))


@disciplinas_bp.route('/minhas_disciplinas')
@login_required
@role_required('professor')
def minhas_disciplinas():
    professor = Professor.query.filter_by(user_id=current_user.id).first()
    if not professor:
        flash('Professor não encontrado.', 'danger')
        return redirect(url_for('painel.painel'))

    disciplinas_ids = db.session.query(DisciplinaTurmaProfessor.disciplina_id).filter_by(professor_id=professor.id).distinct()

    disciplinas = Disciplina.query \
        .filter(Disciplina.id.in_(disciplinas_ids)) \
        .options(
            joinedload(Disciplina.associacoes).joinedload(DisciplinaTurmaProfessor.turma),
            joinedload(Disciplina.associacoes).joinedload(DisciplinaTurmaProfessor.professor)
        ) \
        .all()

    return render_template('disciplinas/minhas.html', disciplinas=disciplinas)


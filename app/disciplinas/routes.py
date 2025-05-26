from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Disciplina, Turma, Professor, SemestreLetivo, DisciplinaTurmaProfessor
from app.auth.decorators import role_required

disciplinas_bp = Blueprint('disciplinas', __name__, url_prefix='/disciplinas')

@disciplinas_bp.route('/')
@login_required
def listar():
    disciplinas = Disciplina.query.all()
    turmas = Turma.query.all()
    professores = Professor.query.all()
    semestres = SemestreLetivo.query.all()
    return render_template('disciplinas/listar.html',
                           disciplinas=disciplinas,
                           turmas=turmas,
                           professores=professores,
                           semestres=semestres)

@disciplinas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    turmas = Turma.query.all()
    professores = Professor.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        nome = request.form['nome']
        sigla = request.form['sigla']
        semestre_letivo_id = request.form['semestre_letivo_id']

        disciplina = Disciplina(
            nome=nome,
            sigla=sigla,
            semestre_letivo_id=semestre_letivo_id
        )

        db.session.add(disciplina)
        db.session.commit()

        # Associações
        turma_ids = request.form.getlist('turma_ids')
        for turma_id in turma_ids:
            professores_ids = request.form.getlist(f'professores_{turma_id}[]')
            for professor_id in professores_ids:
                assoc = DisciplinaTurmaProfessor(
                    disciplina_id=disciplina.id,
                    turma_id=int(turma_id),
                    professor_id=int(professor_id)
                )
                db.session.add(assoc)

        db.session.commit()
        flash('Disciplina criada com sucesso.', 'success')
        return redirect(url_for('disciplinas.listar'))

    return render_template('disciplinas/form.html',
                           titulo='Nova Disciplina',
                           turmas=turmas,
                           professores=professores,
                           semestres=semestres)

@disciplinas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    disciplina = Disciplina.query.get_or_404(id)
    turmas = Turma.query.all()
    professores = Professor.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        disciplina.nome = request.form['nome']
        disciplina.sigla = request.form['sigla']
        disciplina.semestre_letivo_id = request.form['semestre_letivo_id']

        # Limpa associações antigas
        DisciplinaTurmaProfessor.query.filter_by(disciplina_id=disciplina.id).delete()

        # Recria associações
        turma_ids = request.form.getlist('turma_ids')
        for turma_id in turma_ids:
            professores_ids = request.form.getlist(f'professores_{turma_id}[]')
            for professor_id in professores_ids:
                assoc = DisciplinaTurmaProfessor(
                    disciplina_id=disciplina.id,
                    turma_id=int(turma_id),
                    professor_id=int(professor_id)
                )
                db.session.add(assoc)

        db.session.commit()
        flash('Disciplina atualizada com sucesso.', 'info')
        return redirect(url_for('disciplinas.listar'))

    return render_template('disciplinas/form.html',
                           titulo='Editar Disciplina',
                           disciplina=disciplina,
                           turmas=turmas,
                           professores=professores,
                           semestres=semestres)

@disciplinas_bp.route('/excluir/<int:id>', methods=['GET', 'POST'])
@login_required
def excluir(id):
    disciplina = Disciplina.query.get_or_404(id)
    DisciplinaTurmaProfessor.query.filter_by(disciplina_id=disciplina.id).delete()
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

    disciplinas = professor.disciplinas  # via propriedade
    return render_template('disciplinas/minhas.html', disciplinas=disciplinas)

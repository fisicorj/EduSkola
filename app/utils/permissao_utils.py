from app.models import Disciplina, Avaliacao, Turma, DisciplinaTurmaProfessor, Professor
from flask_login import current_user
from flask import abort

def pode_acessar_disciplina(disciplina_id, turma_id=None):
    if current_user.role != 'professor':
        return True  # outros perfis podem acessar

    professor = current_user.professor
    if not professor:
        abort(403)

    query = DisciplinaTurmaProfessor.query.filter_by(
        professor_id=professor.id,
        disciplina_id=disciplina_id
    )

    if turma_id:
        query = query.filter_by(turma_id=turma_id)

    if not query.first():
        abort(403)

    return True


def pode_acessar_avaliacao(avaliacao_id):
    from app.utils.permissao_utils import pode_acessar_disciplina
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
    return pode_acessar_disciplina(avaliacao.disciplina_id)


def pode_acessar_turma(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    if current_user.role == 'professor':
        if not current_user.professor:
            abort(403)
        
        disciplinas_prof = Disciplina.query.filter_by(professor_id=current_user.professor.id, turma_id=turma.id).all()
        if not disciplinas_prof:
            abort(403)
    return True

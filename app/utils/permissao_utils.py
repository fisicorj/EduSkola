from app.models import Disciplina, Avaliacao, Turma
from flask_login import current_user
#from flask import flash, redirect, url_for
from flask import abort

def pode_acessar_disciplina(disciplina_id):
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    
    if current_user.role == 'professor':
        if not current_user.professor or disciplina.professor_id != current_user.professor.id:
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

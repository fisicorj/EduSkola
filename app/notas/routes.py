from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Aluno, Turma, Disciplina, Avaliacao, Nota
from app.utils.avaliacao_utils import calcular_media

notas_bp = Blueprint('notas', __name__, url_prefix='/notas')

@notas_bp.route('/lancar', methods=['GET', 'POST'])
@login_required
def lancar():
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()

    if request.method == 'POST':
        turma_id = request.form['turma_id']
        disciplina_id = request.form['disciplina_id']
        alunos = Aluno.query.filter_by(turma_id=turma_id).all()
        avaliacoes = Avaliacao.query.filter_by(turma_id=turma_id, disciplina_id=disciplina_id).all()

        for aluno in alunos:
            for avaliacao in avaliacoes:
                campo = f'nota_{aluno.id}_{avaliacao.id}'
                if campo in request.form:
                    valor = request.form[campo]
                    nota = Nota.query.filter_by(aluno_id=aluno.id, avaliacao_id=avaliacao.id).first()
                    if nota:
                        nota.valor = valor
                    else:
                        nova = Nota(aluno_id=aluno.id, avaliacao_id=avaliacao.id, valor=valor)
                        db.session.add(nova)
        db.session.commit()
        flash('Notas salvas com sucesso.', 'success')
        return redirect(url_for('notas.lancar'))

    return render_template('notas/selecionar.html', turmas=turmas, disciplinas=disciplinas)

@notas_bp.route('/lancar/<int:turma_id>/<int:disciplina_id>', methods=['GET'])
@login_required
def formulario_lancamento(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()

    # Carregar notas existentes
    notas = {(n.aluno_id, n.avaliacao_id): n.valor for n in Nota.query.all()}

    return render_template('notas/lancar.html', turma=turma, disciplina=disciplina, alunos=alunos, avaliacoes=avaliacoes, notas=notas)

@notas_bp.route('/resultado/<int:turma_id>/<int:disciplina_id>')
@login_required
def resultado(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    alunos = Aluno.query.filter_by(turma_id=turma.id).all()

    resultados = []

    for aluno in alunos:
        media = calcular_media(aluno, disciplina, turma)
        if media is None:
            situacao = "Sem nota"
        elif media >= turma.instituicao.media_aprovacao:
            situacao = "Aprovado"
        else:
            situacao = "Reprovado"
        resultados.append({
            'aluno': aluno,
            'media': media,
            'situacao': situacao
        })

    return render_template('notas/resultado.html', resultados=resultados, turma=turma, disciplina=disciplina)

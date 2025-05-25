from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Aluno, Turma, Disciplina, Avaliacao, Nota, SemestreLetivo
from app.utils.avaliacao_utils import calcular_media
from collections import defaultdict

notas_bp = Blueprint('notas', __name__, url_prefix='/notas')

# ✅ Seleção de turma/disciplina por semestre para lançamento
@notas_bp.route('/selecionar', methods=['GET'])
@login_required
def selecionar_lancamento():
    semestres = SemestreLetivo.query.all()
    semestre_id = request.args.get('semestre_id', type=int)

    turmas = Turma.query.filter_by(semestre_letivo_id=semestre_id).all() if semestre_id else Turma.query.all()
    disciplinas = Disciplina.query.all()

    return render_template('notas/selecionar.html', 
                           turmas=turmas, 
                           disciplinas=disciplinas, 
                           semestres=semestres, 
                           semestre_id=semestre_id)

# ✅ Redirecionamento após seleção para lançamento
@notas_bp.route('/lancar/selecionar', methods=['POST'])
@login_required
def formulario_lancamento():
    turma_id = request.form['turma_id']
    disciplina_id = request.form['disciplina_id']
    return redirect(url_for('notas.lancar', turma_id=turma_id, disciplina_id=disciplina_id))

# ✅ Lançamento de notas
@notas_bp.route('/lancar/<int:turma_id>/<int:disciplina_id>', methods=['GET', 'POST'])
@login_required
def lancar(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()

    if request.method == 'POST':
        for aluno in alunos:
            for avaliacao in avaliacoes:
                campo = f'nota_{aluno.id}_{avaliacao.id}'
                if campo in request.form:
                    valor = request.form[campo]
                    valor = float(valor) if valor else None

                    nota = Nota.query.filter_by(aluno_id=aluno.id, avaliacao_id=avaliacao.id).first()
                    if nota:
                        nota.valor = valor
                    else:
                        nova = Nota(aluno_id=aluno.id, avaliacao_id=avaliacao.id, valor=valor)
                        db.session.add(nova)
        db.session.commit()
        flash('Notas salvas com sucesso.', 'success')
        return redirect(url_for('notas.lancar', turma_id=turma_id, disciplina_id=disciplina_id))

    notas = {
        (n.aluno_id, n.avaliacao_id): n.valor
        for n in Nota.query.filter(Nota.avaliacao_id.in_([av.id for av in avaliacoes])).all()
    }

    return render_template('notas/lancar.html', 
                           turma=turma, 
                           disciplina=disciplina, 
                           alunos=alunos, 
                           avaliacoes=avaliacoes, 
                           notas=notas)

# ✅ Seleção de resultado: turma e/ou disciplina
@notas_bp.route('/resultado/selecionar', methods=['GET', 'POST'])
@login_required
def selecionar_resultado():
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    semestres = SemestreLetivo.query.all()

    semestre_id = request.args.get('semestre_id')

    if request.method == 'POST':
        turma_id = request.form['turma_id']
        disciplina_id = request.form.get('disciplina_id')

        if disciplina_id:
            return redirect(url_for('notas.resultado', turma_id=turma_id, disciplina_id=disciplina_id))
        else:
            return redirect(url_for('notas.resultado_turma', turma_id=turma_id))

    return render_template('notas/selecionar_resultado.html',
                           turmas=turmas,
                           disciplinas=disciplinas,
                           semestres=semestres,
                           semestre_id=semestre_id)

# ✅ Exibição de resultado por turma e disciplina
@notas_bp.route('/resultado/<int:turma_id>/<int:disciplina_id>')
@login_required
def resultado(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
    notas_todas = Nota.query.all()

    notas = {(n.aluno_id, n.avaliacao_id): n.valor for n in notas_todas}

    resultados = []

    for aluno in alunos:
        aluno_notas = [notas.get((aluno.id, av.id)) for av in avaliacoes]
        media = calcular_media(aluno, disciplina, turma)
        situacao = "Sem nota"
        if media is not None:
            situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"

        resultados.append({
            'aluno': aluno,
            'notas': aluno_notas,
            'media': media,
            'situacao': situacao
        })

    return render_template('notas/resultado.html',
                           turma=turma,
                           disciplina=disciplina,
                           avaliacoes=avaliacoes,
                           resultados=resultados)

# ✅ Resultado de todas as disciplinas da turma

@notas_bp.route('/resultado_turma/<int:turma_id>')
@login_required
def resultado_turma(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplinas = Disciplina.query.filter_by(turma_id=turma.id).all()
    alunos = Aluno.query.filter_by(turma_id=turma.id).all()

    agrupado = defaultdict(list)

    for disciplina in disciplinas:
        avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
        for aluno in alunos:
            notas = []
            for avaliacao in avaliacoes:
                nota = Nota.query.filter_by(aluno_id=aluno.id, avaliacao_id=avaliacao.id).first()
                notas.append(nota.valor if nota else None)

            media = calcular_media(aluno, disciplina, turma)
            situacao = "Sem nota"
            if media is not None:
                situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"

            agrupado[disciplina].append({
                'aluno': aluno,
                'notas': notas,
                'media': media,
                'situacao': situacao,
                'avaliacoes': avaliacoes
            })

    return render_template('notas/resultado_turma.html',
                           turma=turma,
                           agrupado=agrupado)



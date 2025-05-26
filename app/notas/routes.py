from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Aluno, Turma, Disciplina, Avaliacao, Nota, SemestreLetivo, Professor
from app.utils.avaliacao_utils import calcular_media
from app.utils.permissao_utils import pode_acessar_disciplina
from werkzeug.exceptions import abort

notas_bp = Blueprint('notas', __name__, url_prefix='/notas')

@notas_bp.route('/selecionar', methods=['GET'])
@login_required
def selecionar_lancamento():
    semestres = SemestreLetivo.query.all()
    semestre_id = request.args.get('semestre_id', type=int)

    turmas = Turma.query.filter_by(semestre_letivo_id=semestre_id).all() if semestre_id else Turma.query.all()

    if current_user.role == 'professor':
        professor = Professor.query.filter_by(user_id=current_user.id).first()
        if not professor:
            abort(403)
        disciplinas = professor.disciplinas
    else:
        disciplinas = Disciplina.query.all()

    return render_template('notas/selecionar.html',
                           turmas=turmas,
                           disciplinas=disciplinas,
                           semestres=semestres,
                           semestre_id=semestre_id)

@notas_bp.route('/lancar/selecionar', methods=['POST'])
@login_required
def formulario_lancamento():
    turma_id = request.form['turma_id']
    disciplina_id = request.form['disciplina_id']
    return redirect(url_for('notas.lancar', turma_id=turma_id, disciplina_id=disciplina_id))

@notas_bp.route('/lancar/<int:turma_id>/<int:disciplina_id>', methods=['GET', 'POST'])
@login_required
def lancar(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)

    if not pode_acessar_disciplina(disciplina_id):
        abort(403)

    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()

    if not avaliacoes:
        flash('Não há avaliações cadastradas para esta turma e disciplina.', 'warning')
        return redirect(url_for('notas.selecionar_lancamento'))

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
        flash('Notas lançadas com sucesso.', 'success')
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

@notas_bp.route('/resultado/selecionar', methods=['GET', 'POST'])
@login_required
def selecionar_resultado():
    turmas = Turma.query.all()

    if current_user.role == 'professor':
        professor = Professor.query.filter_by(user_id=current_user.id).first()
        if not professor:
            abort(403)
        disciplinas = professor.disciplinas
    else:
        disciplinas = Disciplina.query.all()

    semestres = SemestreLetivo.query.all()
    semestre_id = request.args.get('semestre_id', type=int)

    if request.method == 'POST':
        turma_id = request.form['turma_id']
        disciplina_id = request.form.get('disciplina_id')

        return redirect(url_for('notas.resultado', turma_id=turma_id, disciplina_id=disciplina_id))

    return render_template('notas/selecionar_resultado.html',
                           turmas=turmas,
                           disciplinas=disciplinas,
                           semestres=semestres,
                           semestre_id=semestre_id)

@notas_bp.route('/resultado/<int:turma_id>/<int:disciplina_id>')
@login_required
def resultado(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)

    if not pode_acessar_disciplina(disciplina_id):
        abort(403)

    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()

    notas_todas = Nota.query.filter(Nota.avaliacao_id.in_([a.id for a in avaliacoes])).all()
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

@notas_bp.route('/resultado_turma/<int:turma_id>')
@login_required
def resultado_turma(turma_id):
    turma = Turma.query.get_or_404(turma_id)

    from app.models import DisciplinaTurmaProfessor

    # Buscar as disciplinas associadas a essa turma via a tabela associativa
    disciplina_ids = db.session.query(DisciplinaTurmaProfessor.disciplina_id).filter_by(turma_id=turma.id).distinct()
    disciplinas = Disciplina.query.filter(Disciplina.id.in_(disciplina_ids)).all()

    alunos = Aluno.query.filter_by(turma_id=turma.id).all()

    agrupado = {}

    for disciplina in disciplinas:
        avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
        dados = []

        for aluno in alunos:
            notas = []
            for avaliacao in avaliacoes:
                nota = Nota.query.filter_by(aluno_id=aluno.id, avaliacao_id=avaliacao.id).first()
                notas.append(nota.valor if nota else None)

            media = calcular_media(aluno, disciplina, turma)
            situacao = "Sem nota"
            if media is not None:
                situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"

            dados.append({
                'aluno': aluno,
                'notas': notas,
                'media': media,
                'situacao': situacao,
                'avaliacoes': avaliacoes
            })

        agrupado[disciplina] = dados

    return render_template('notas/resultado_turma.html',
                           turma=turma,
                           agrupado=agrupado)

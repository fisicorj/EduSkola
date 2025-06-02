from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, Response
from flask_login import login_required, current_user
from app import db
from app.models import Aluno, Turma, Disciplina, Avaliacao, Nota, SemestreLetivo, Professor, DisciplinaTurmaProfessor
from app.utils.avaliacao_utils import calcular_media
from app.utils.permissao_utils import pode_acessar_disciplina
from app.services.email_service import enviar_email
from werkzeug.exceptions import abort
from weasyprint import HTML
from io import BytesIO
from datetime import datetime
import csv
from io import StringIO


notas_bp = Blueprint('notas', __name__, url_prefix='/notas')
data_hora_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")

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
        disciplinas_ids = db.session.query(Disciplina.id).join(Disciplina.associacoes)\
            .filter(DisciplinaTurmaProfessor.professor_id == professor.id).distinct()
        disciplinas = Disciplina.query.filter(Disciplina.id.in_(disciplinas_ids)).all()

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
                    valor_str = request.form[campo]

                    if not valor_str:
                        #Se não foi preenchido, não cria nem atualiza
                        continue

                    try:
                        valor = float(valor_str)
                    except ValueError:
                        flash(f"Nota inválida para {aluno.nome} na avaliação {avaliacao.nome}.", 'danger')
                        continue

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
        disciplinas_ids = db.session.query(Disciplina.id).join(Disciplina.associacoes)\
            .filter(DisciplinaTurmaProfessor.professor_id == professor.id).distinct()
        disciplinas = Disciplina.query.filter(Disciplina.id.in_(disciplinas_ids)).all()

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

    disciplina_ids = db.session.query(DisciplinaTurmaProfessor.disciplina_id).filter_by(turma_id=turma.id).distinct()
    disciplinas = Disciplina.query.filter(Disciplina.id.in_(disciplina_ids)).all()

    alunos = Aluno.query.filter_by(turma_id=turma.id).all()

    agrupado = {}
    estatisticas = {}

    for disciplina in disciplinas:
        avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
        dados = []
        qtd_aprovados = 0

        for aluno in alunos:
            notas = []
            for avaliacao in avaliacoes:
                nota = Nota.query.filter_by(aluno_id=aluno.id, avaliacao_id=avaliacao.id).first()
                notas.append(nota.valor if nota else None)

            media = calcular_media(aluno, disciplina, turma)
            situacao = "Sem nota"
            if media is not None:
                situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"
                if situacao == "Aprovado":
                    qtd_aprovados += 1

            dados.append({
                'aluno': aluno,
                'notas': notas,
                'media': media,
                'situacao': situacao,
                'avaliacoes': avaliacoes
            })

        agrupado[disciplina] = dados

        # Cálculo das médias das avaliações (colunas)
        medias_avaliacoes = []
        for idx, avaliacao in enumerate(avaliacoes):
            notas_av = [
                dado['notas'][idx] for dado in dados
                if dado['notas'][idx] is not None
            ]
            if notas_av:
                media_coluna = sum(notas_av) / len(notas_av)
            else:
                media_coluna = 0.0
            medias_avaliacoes.append(media_coluna)

        # Cálculo da média das médias
        medias_individuais = [dado['media'] for dado in dados if dado['media'] is not None]
        if medias_individuais:
            media_das_medias = sum(medias_individuais) / len(medias_individuais)
        else:
            media_das_medias = 0.0

        # Cálculo do percentual de aprovados
        total_alunos = len(dados)
        percentual_aprovados = (qtd_aprovados / total_alunos * 100) if total_alunos else 0.0

        estatisticas[disciplina.id] = {
            'medias_avaliacoes': medias_avaliacoes,
            'media_das_medias': media_das_medias,
            'percentual_aprovados': percentual_aprovados
        }

    return render_template('notas/resultado_turma.html',
                           turma=turma,
                           agrupado=agrupado,
                           estatisticas=estatisticas)


@notas_bp.route('/resultado_individual/<int:turma_id>/<int:disciplina_id>/<int:aluno_id>')
@login_required
def resultado_individual(turma_id, disciplina_id, aluno_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    aluno = Aluno.query.get_or_404(aluno_id)

    if not pode_acessar_disciplina(disciplina_id):
        abort(403)

    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
    notas = []
    
    for av in avaliacoes:
        nota = Nota.query.filter_by(aluno_id=aluno.id, avaliacao_id=av.id).first()
        notas.append(nota.valor if nota else None)

    media = calcular_media(aluno, disciplina, turma)
    situacao = "Sem nota"
    if media is not None:
        situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"

    return render_template('notas/resultado_individual.html',
                           turma=turma,
                           disciplina=disciplina,
                           aluno=aluno,
                           avaliacoes=avaliacoes,
                           notas=notas,
                           media=media,
                           situacao=situacao)

@notas_bp.route('/resultado_aluno', methods=['GET', 'POST'])
@login_required
def resultado_aluno():
    aluno = None
    resultados = []

    if request.method == 'POST':
        nome_aluno = request.form.get('nome_aluno')

        aluno = Aluno.query.filter(Aluno.nome.ilike(f"%{nome_aluno}%")).first()

        if aluno:
            turmas = Turma.query.filter_by(id=aluno.turma_id).all()

            for turma in turmas:
                disciplinas = Disciplina.query.join(Avaliacao).filter(Avaliacao.turma_id == turma.id).distinct().all()

                for disciplina in disciplinas:
                    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()

                    aluno_notas = []
                    for av in avaliacoes:
                        nota = Nota.query.filter_by(aluno_id=aluno.id, avaliacao_id=av.id).first()
                        aluno_notas.append((av.nome, nota.valor if nota else None))

                    media = calcular_media(aluno, disciplina, turma)
                    situacao = "Sem nota"
                    if media is not None:
                        situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"

                    resultados.append({
                        'turma': turma,
                        'disciplina': disciplina,
                        'avaliacoes': aluno_notas,
                        'media': media,
                        'situacao': situacao
                    })

    return render_template('notas/resultado_aluno.html', aluno=aluno, resultados=resultados)

@notas_bp.route('/export/pdf/<int:turma_id>/<int:disciplina_id>')
@login_required
def export_pdf(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)

    if not pode_acessar_disciplina(disciplina_id):
        abort(403)

    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
    
    notas_todas = Nota.query.filter(Nota.avaliacao_id.in_([a.id for a in avaliacoes])).all()
    notas = {(n.aluno_id, n.avaliacao_id): n.valor for n in notas_todas}

    resultados = []
    qtd_aprovados = 0

    for aluno in alunos:
        aluno_notas = [notas.get((aluno.id, av.id)) for av in avaliacoes]
        media = calcular_media(aluno, disciplina, turma)
        situacao = "Sem nota"
        if media is not None:
            situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"
            if situacao == "Aprovado":
                qtd_aprovados += 1
        resultados.append({
            'aluno': aluno,
            'notas': aluno_notas,
            'media': media,
            'situacao': situacao
        })

    # Cálculo das médias das avaliações (colunas)
    medias_avaliacoes = []
    for idx, avaliacao in enumerate(avaliacoes):
        notas_av = [
            resultado['notas'][idx] for resultado in resultados
            if resultado['notas'][idx] is not None
        ]
        if notas_av:
            media_coluna = sum(notas_av) / len(notas_av)
        else:
            media_coluna = 0.0
        medias_avaliacoes.append(media_coluna)

    # Cálculo da média das médias
    medias_individuais = [resultado['media'] for resultado in resultados if resultado['media'] is not None]
    if medias_individuais:
        media_das_medias = sum(medias_individuais) / len(medias_individuais)
    else:
        media_das_medias = 0.0

    # Cálculo do percentual de aprovados
    total_alunos = len(resultados)
    percentual_aprovados = (qtd_aprovados / total_alunos * 100) if total_alunos else 0.0

    # Renderiza template HTML
    html = render_template('notas/relatorio_pdf.html',
                           turma=turma,
                           disciplina=disciplina,
                           avaliacoes=avaliacoes,
                           resultados=resultados,
                           medias_avaliacoes=medias_avaliacoes,
                           media_das_medias=media_das_medias,
                           percentual_aprovados=percentual_aprovados,
                           data_hora_emissao=data_hora_emissao)

    # Gera o PDF
    pdf_file = BytesIO()
    HTML(string=html).write_pdf(pdf_file)
    pdf_file.seek(0)

    response = make_response(pdf_file.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{turma.codigo}_{disciplina.sigla}.pdf'

    return response


@notas_bp.route('/export/csv/<int:turma_id>/<int:disciplina_id>')
@login_required
def export_csv(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)

    if not pode_acessar_disciplina(disciplina_id):
        abort(403)

    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
    
    notas_todas = Nota.query.filter(Nota.avaliacao_id.in_([a.id for a in avaliacoes])).all()
    notas = {(n.aluno_id, n.avaliacao_id): n.valor for n in notas_todas}

    output = StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)

    # Cabeçalho
    header = ['Aluno']
    header += [av.nome for av in avaliacoes]
    header += ['Média', 'Situação']
    writer.writerow(header)

    for aluno in alunos:
        aluno_notas = [notas.get((aluno.id, av.id)) for av in avaliacoes]
        media = calcular_media(aluno, disciplina, turma)
        situacao = "Sem nota"
        if media is not None:
            situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"
        
        row = [aluno.nome]
        row += [f"{n:.2f}" if n is not None else '-' for n in aluno_notas]
        row.append(f"{media:.2f}" if media is not None else '-')
        row.append(situacao)
        writer.writerow(row)

    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=notas_{turma.codigo}_{disciplina.sigla}.csv"}
    )


@notas_bp.route('/enviar_email_coletivo/<int:turma_id>/<int:disciplina_id>')
@login_required
def enviar_email_coletivo(turma_id, disciplina_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)

    if not pode_acessar_disciplina(disciplina_id):
        abort(403)

    alunos = Aluno.query.filter_by(turma_id=turma.id).all()
    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
    
    notas_todas = Nota.query.filter(Nota.avaliacao_id.in_([a.id for a in avaliacoes])).all()
    notas = {(n.aluno_id, n.avaliacao_id): n.valor for n in notas_todas}

    enviados = 0

    for aluno in alunos:
        aluno_notas = []
        for av in avaliacoes:
            nota = notas.get((aluno.id, av.id))
            nota_txt = f"{nota:.2f}" if nota is not None else '-'
            aluno_notas.append((av.nome, nota_txt))

        media = calcular_media(aluno, disciplina, turma)
        situacao = "Sem nota"
        if media is not None:
            situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"

        # Template HTML inline estilizado
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f4f4f4; }}
                .aprovado {{ color: green; font-weight: bold; }}
                .reprovado {{ color: red; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h2>Olá {aluno.nome},</h2>
            <p>Segue o relatório de suas notas na disciplina <strong>{disciplina.nome}</strong> - Turma <strong>{turma.nome}</strong>:</p>
            <table>
                <thead>
                    <tr>
                        <th>Avaliação</th>
                        <th>Nota</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{av}</td><td>{nota}</td></tr>' for av, nota in aluno_notas])}
                </tbody>
            </table>
            <p><strong>Média final:</strong> {f"{media:.2f}" if media is not None else '-'}</p>
            <p><strong>Situação:</strong> <span class="{ 'aprovado' if situacao == 'Aprovado' else 'reprovado' }">{situacao}</span></p>
            <p>Atenciosamente,<br>Coordenação</p>
        </body>
        </html>
        """

        try:
            enviar_email(aluno.email, f"Notas - {disciplina.nome}", corpo_html)
            enviados += 1
        except Exception as e:
            print(f"Erro ao enviar para {aluno.email}: {e}")

    flash(f'E-mails enviados com sucesso: {enviados} alunos.', 'success')
    return redirect(url_for('notas.resultado', turma_id=turma.id, disciplina_id=disciplina.id))

@notas_bp.route('/enviar_email_individual/<int:turma_id>/<int:disciplina_id>/<int:aluno_id>')
@login_required
def enviar_email_individual(turma_id, disciplina_id, aluno_id):
    turma = Turma.query.get_or_404(turma_id)
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    aluno = Aluno.query.get_or_404(aluno_id)

    if not pode_acessar_disciplina(disciplina_id):
        abort(403)

    avaliacoes = Avaliacao.query.filter_by(turma_id=turma.id, disciplina_id=disciplina.id).all()
    notas = Nota.query.filter(Nota.aluno_id == aluno.id, Nota.avaliacao_id.in_([a.id for a in avaliacoes])).all()

    aluno_notas = []
    for av in avaliacoes:
        nota = next((n.valor for n in notas if n.avaliacao_id == av.id), None)
        nota_txt = f"{nota:.2f}" if nota is not None else '-'
        aluno_notas.append(f"{av.nome}: {nota_txt}")

    media = calcular_media(aluno, disciplina, turma)
    situacao = "Sem nota"
    if media is not None:
        situacao = "Aprovado" if media >= turma.instituicao.media_aprovacao else "Reprovado"

    corpo = f"""
Olá {aluno.nome},

Segue o relatório de suas notas na disciplina {disciplina.nome} - Turma {turma.nome}:

{chr(10).join(aluno_notas)}

Média final: {f"{media:.2f}" if media is not None else '-'}  Situação: {situacao}

Atenciosamente,
Coordenação
"""
    try:
        enviar_email(aluno.email, f"Notas - {disciplina.nome}", corpo)
        flash(f'E-mail enviado com sucesso para {aluno.nome}', 'success')
    except Exception as e:
        flash(f'Erro ao enviar e-mail para {aluno.nome}: {e}', 'danger')

    return redirect(url_for('notas.resultado', turma_id=turma.id, disciplina_id=disciplina.id))

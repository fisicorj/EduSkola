import os
from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app, send_from_directory, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app import db
from app.models import Importacao, Instituicao, Curso, Turma, Aluno, Professor, Disciplina, Nota, Avaliacao
from app.services.importacao_service import ImportacaoService
from app.services.zip_service import criar_zip_modelos


painel_bp = Blueprint('painel', __name__, url_prefix='/painel')

TEMPLATES_FOLDER = os.path.join('static', 'templates_importacao')
ZIP_MODELOS_PATH = os.path.join('static', 'templates_importacao.zip')

@painel_bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    """Processa a importação e redireciona para o painel."""
    tipos = ImportacaoService.TIPOS_SUPORTADOS

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        arquivo = request.files.get('arquivo')

        if not tipo or not arquivo:
            flash('Selecione o tipo e envie um arquivo.', 'danger')
            return redirect(url_for('painel.painel'))

        try:
            ImportacaoService.processar_upload(tipo, arquivo, current_user)
            flash('Importação realizada com sucesso.', 'success')
        except Exception as e:
            flash(f'Erro: {str(e)}', 'danger')

    # ✅ Sempre redireciona para painel
    return redirect(url_for('painel.painel'))


@painel_bp.route('/template/<nome>')
@login_required
def baixar_template(nome):
    """Download individual de template"""
    try:
        caminho = os.path.join(current_app.root_path, TEMPLATES_FOLDER)
        return send_from_directory(caminho, nome, as_attachment=True)
    except Exception as e:
        flash(f"Erro ao baixar template: {str(e)}", 'danger')
        return redirect(url_for('painel.importar'))

@painel_bp.route('/template/all')
@login_required
def baixar_todos_templates():
    """Download de todos os templates como .zip"""
    try:
        zip_path = criar_zip_modelos(
            pasta_modelos=os.path.join(current_app.root_path, 'static', 'templates_importacao'),
            nome_zip='templates_importacao.zip'
        )
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        flash(f"Erro ao gerar ou baixar pacote: {str(e)}", 'danger')
        return redirect(url_for('painel.importar'))


@painel_bp.route('/')
@login_required
def painel():
    """Dashboard principal"""
    try:
        stats = {
            'instituicoes': Instituicao.query.count(),
            'turmas': Turma.query.count(),
            'alunos': Aluno.query.count(),
            'professores': Professor.query.count(),
            'disciplinas': Disciplina.query.count()
        }

        alunos_por_turma = db.session.query(
            Turma.nome.label('turma'),
            func.count(Aluno.id).label('quantidade')
        ).join(Aluno).group_by(Turma.id).order_by(desc('quantidade')).limit(10).all()

        disciplinas_por_professor = db.session.query(
            Professor.nome.label('professor'),
            func.count(Disciplina.id).label('quantidade')
        ).join(Disciplina).group_by(Professor.id).order_by(desc('quantidade')).limit(10).all()

        notas_por_aluno = db.session.query(
            Aluno.nome.label('aluno'),
            Disciplina.nome.label('disciplina'),
            Nota.valor.label('valor')
        ).join(Nota, Nota.aluno_id == Aluno.id)\
         .join(Avaliacao, Nota.avaliacao_id == Avaliacao.id)\
         .join(Disciplina, Avaliacao.disciplina_id == Disciplina.id)\
         .order_by(Aluno.nome).limit(20).all()

        media_por_disciplina = db.session.query(
            Disciplina.nome.label('disciplina'),
            func.avg(Nota.valor).label('media')
        ).join(Avaliacao, Avaliacao.disciplina_id == Disciplina.id)\
         .join(Nota, Nota.avaliacao_id == Avaliacao.id)\
         .group_by(Disciplina.id).all()

        labels_turma = [t.turma for t in alunos_por_turma]
        valores_turma = [t.quantidade for t in alunos_por_turma]

        labels_prof = [p.professor for p in disciplinas_por_professor]
        valores_prof = [p.quantidade for p in disciplinas_por_professor]

        historico_importacoes = Importacao.query.order_by(desc(Importacao.data)).limit(5).all()
        ultima_importacao = Importacao.query.order_by(desc(Importacao.data)).first()
        tipos = ImportacaoService.TIPOS_SUPORTADOS

        return render_template(
            'painel/painel.html',
            stats=stats,
            alunos_por_turma=alunos_por_turma,
            disciplinas_por_professor=disciplinas_por_professor,
            historico_importacoes=historico_importacoes,
            ultima_importacao=ultima_importacao,
            tipos=tipos,
            labels_turma=labels_turma,
            valores_turma=valores_turma,
            labels_prof=labels_prof,
            valores_prof=valores_prof,
            notas_por_aluno=notas_por_aluno,
            media_por_disciplina=media_por_disciplina,
            instituicoes=Instituicao.query.all()
        )
    except Exception as e:
        flash(f"Erro ao carregar painel: {str(e)}", 'danger')
        return render_template('painel/painel.html')

import os
import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import func
from app import db
from app.models import Importacao, Instituicao, Curso, Turma, Aluno, Professor, Disciplina

painel_bp = Blueprint('painel', __name__, url_prefix='/painel')

def registrar_importacao(tipo, status, detalhes):
    registro = Importacao(
        tipo=tipo,
        status=status,
        detalhes=detalhes,
        usuario_id=current_user.id,
        data_hora=datetime.now()
    )
    db.session.add(registro)
    db.session.commit()

@painel_bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    tipos = ['instituicoes', 'cursos', 'turmas', 'alunos', 'professores', 'disciplinas']
    if request.method == 'POST':
        tipo = request.form['tipo']
        arquivo = request.files['arquivo']

        if not arquivo or arquivo.filename == '':
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(url_for('painel.importar'))

        nome = secure_filename(arquivo.filename)
        caminho = os.path.join('uploads', nome)
        os.makedirs('uploads', exist_ok=True)
        arquivo.save(caminho)

        return redirect(url_for(f'painel.importar_{tipo}', caminho=caminho))

    return render_template('painel/importar.html', tipos=tipos)

def processar_importacao(caminho, tipo, modelo, campos_obrigatorios, campos_unico=None):
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        inseridos, ignorados, erros = 0, 0, 0
        
        for _, row in df.iterrows():
            try:
                dados = {}
                for campo in campos_obrigatorios:
                    if campo not in row:
                        raise ValueError(f"Campo obrigatório '{campo}' não encontrado")
                    dados[campo] = str(row[campo]).strip()
                    if not dados[campo]:
                        raise ValueError(f"Campo '{campo}' não pode ser vazio")

                # Verificar unicidade se especificado
                if campos_unico:
                    filtro = {campo: dados[campo] for campo in campos_unico}
                    existe = modelo.query.filter_by(**filtro).first()
                    if existe:
                        ignorados += 1
                        continue

                # Criar e adicionar o objeto
                db.session.add(modelo(**dados))
                inseridos += 1
                
            except Exception as e:
                erros += 1
                continue

        db.session.commit()
        mensagem = f"{tipo.capitalize()} importados: {inseridos} | Ignorados: {ignorados} | Erros: {erros}"
        registrar_importacao(tipo, 'sucesso', mensagem)
        flash(mensagem, 'success')
        
    except Exception as e:
        db.session.rollback()
        mensagem = f"Erro ao importar {tipo}: {str(e)}"
        registrar_importacao(tipo, 'erro', mensagem)
        flash(mensagem, 'danger')
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)

@painel_bp.route('/importar/instituicoes')
@login_required
def importar_instituicoes():
    caminho = request.args.get('caminho')
    campos_obrigatorios = ['nome', 'sigla', 'cidade', 'tipo']
    processar_importacao(
        caminho=caminho,
        tipo='instituicoes',
        modelo=Instituicao,
        campos_obrigatorios=campos_obrigatorios + ['media'],
        campos_unico=['sigla']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/cursos')
@login_required
def importar_cursos():
    caminho = request.args.get('caminho')
    campos_obrigatorios = ['nome', 'sigla', 'instituicao_id']
    processar_importacao(
        caminho=caminho,
        tipo='cursos',
        modelo=Curso,
        campos_obrigatorios=campos_obrigatorios,
        campos_unico=['sigla', 'instituicao_id']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/turmas')
@login_required
def importar_turmas():
    caminho = request.args.get('caminho')
    campos_obrigatorios = ['nome', 'codigo', 'turno', 'curso_id', 'instituicao_id']
    processar_importacao(
        caminho=caminho,
        tipo='turmas',
        modelo=Turma,
        campos_obrigatorios=campos_obrigatorios,
        campos_unico=['codigo']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/alunos')
@login_required
def importar_alunos():
    caminho = request.args.get('caminho')
    campos_obrigatorios = ['nome', 'email', 'matricula', 'turma_id']
    processar_importacao(
        caminho=caminho,
        tipo='alunos',
        modelo=Aluno,
        campos_obrigatorios=campos_obrigatorios,
        campos_unico=['email', 'matricula']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/professores')
@login_required
def importar_professores():
    caminho = request.args.get('caminho')
    campos_obrigatorios = ['nome', 'email']
    processar_importacao(
        caminho=caminho,
        tipo='professores',
        modelo=Professor,
        campos_obrigatorios=campos_obrigatorios,
        campos_unico=['email']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/disciplinas')
@login_required
def importar_disciplinas():
    caminho = request.args.get('caminho')
    campos_obrigatorios = ['nome', 'sigla', 'turma_id', 'professor_id']
    processar_importacao(
        caminho=caminho,
        tipo='disciplinas',
        modelo=Disciplina,
        campos_obrigatorios=campos_obrigatorios,
        campos_unico=['sigla', 'turma_id']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/')
@login_required
def painel():
    # Estatísticas básicas
    total_instituicoes = Instituicao.query.count()
    total_turmas = Turma.query.count()
    total_alunos = Aluno.query.count()
    total_professores = Professor.query.count()
    total_disciplinas = Disciplina.query.count()

    # Dados para gráficos
    alunos_por_turma = db.session.query(
        Turma.nome.label('turma'),
        func.count(Aluno.id).label('quantidade')
    ).join(Aluno).group_by(Turma.id).order_by(func.count(Aluno.id).desc()).limit(10).all()

    disciplinas_por_professor = db.session.query(
        Professor.nome.label('professor'),
        func.count(Disciplina.id).label('quantidade')
    ).join(Disciplina).group_by(Professor.id).order_by(func.count(Disciplina.id).desc()).limit(10).all()

    # Histórico de importações
    historico_importacoes = Importacao.query.order_by(Importacao.data.desc()).limit(10).all()

    # Última importação
    ultima_importacao = Importacao.query.order_by(Importacao.data.desc()).first()

    return render_template(
        'painel/painel.html',
        total_instituicoes=total_instituicoes,
        total_turmas=total_turmas,
        total_alunos=total_alunos,
        total_professores=total_professores,
        total_disciplinas=total_disciplinas,
        alunos_por_turma=alunos_por_turma,
        disciplinas_por_professor=disciplinas_por_professor,
        historico_importacoes=historico_importacoes,
        ultima_importacao=ultima_importacao
    )
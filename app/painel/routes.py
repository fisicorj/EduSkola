import os
import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import func, desc
from app import db
from app.models import Importacao, Instituicao, Curso, Turma, Aluno, Professor, Disciplina

painel_bp = Blueprint('painel', __name__, url_prefix='/painel')

# Constants
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
UPLOAD_FOLDER = 'uploads'
TEMPLATES_FOLDER = os.path.join('static', 'templates_importacao')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def registrar_importacao(tipo, status, detalhes):
    """Registra uma operação de importação no banco de dados"""
    try:
        registro = Importacao(
            tipo=tipo,
            status=status,
            detalhes=detalhes,
            usuario_id=current_user.id,
            data=datetime.now()
        )
        db.session.add(registro)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao registrar importação: {str(e)}")

@painel_bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    """Handle file upload and redirect to appropriate import function"""
    tipos = ['instituicoes', 'cursos', 'turmas', 'alunos', 'professores', 'disciplinas']
    
    if request.method == 'POST':
        # Validate form inputs
        tipo = request.form.get('tipo')
        arquivo = request.files.get('arquivo')
        
        if not tipo or tipo not in tipos:
            flash('Tipo de importação inválido.', 'danger')
            return redirect(url_for('painel.importar'))
            
        if not arquivo or arquivo.filename == '':
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(url_for('painel.importar'))
            
        if not allowed_file(arquivo.filename):
            flash('Tipo de arquivo não permitido. Use CSV ou XLSX.', 'danger')
            return redirect(url_for('painel.importar'))

        # Save uploaded file
        nome = secure_filename(arquivo.filename)
        caminho = os.path.join(UPLOAD_FOLDER, nome)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        arquivo.save(caminho)
        
        return redirect(url_for(f'painel.importar_{tipo}', caminho=caminho))

    return render_template('painel/importar.html', tipos=tipos)

def processar_importacao(caminho, tipo, modelo, campos_obrigatorios, campos_unico=None):
    """Processa a importação de dados de um arquivo"""
    try:
        # Read file based on extension
        if caminho.endswith('.xlsx'):
            df = pd.read_excel(caminho, dtype=str)  # Read all as string to avoid type issues
        else:
            df = pd.read_csv(caminho, dtype=str)
            
        df = df.where(pd.notnull(df), None)  # Convert NaN to None
        inseridos, ignorados, erros = 0, 0, 0
        
        for _, row in df.iterrows():
            try:
                dados = {}
                # Validate required fields
                for campo in campos_obrigatorios:
                    if campo not in row:
                        raise ValueError(f"Campo obrigatório '{campo}' não encontrado")
                    value = str(row[campo]).strip() if row[campo] is not None else ''
                    if not value:
                        raise ValueError(f"Campo '{campo}' não pode ser vazio")
                    dados[campo] = value

                # Check uniqueness constraints
                if campos_unico:
                    filtro = {campo: dados[campo] for campo in campos_unico}
                    if modelo.query.filter_by(**filtro).first():
                        ignorados += 1
                        continue

                # Create and add the object
                db.session.add(modelo(**dados))
                inseridos += 1
                
            except Exception as e:
                erros += 1
                current_app.logger.warning(f"Erro ao processar linha {_+1}: {str(e)}")
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
        current_app.logger.error(f"Erro na importação de {tipo}: {str(e)}")
    finally:
        if os.path.exists(caminho):
            try:
                os.remove(caminho)
            except Exception as e:
                current_app.logger.error(f"Erro ao remover arquivo {caminho}: {str(e)}")

# Individual import routes (kept simple by using the processar_importacao function)
@painel_bp.route('/importar/instituicoes')
@login_required
def importar_instituicoes():
    caminho = request.args.get('caminho')
    processar_importacao(
        caminho=caminho,
        tipo='instituicoes',
        modelo=Instituicao,
        campos_obrigatorios=['nome', 'sigla', 'cidade', 'tipo', 'media'],
        campos_unico=['sigla']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/cursos')
@login_required
def importar_cursos():
    caminho = request.args.get('caminho')
    processar_importacao(
        caminho=caminho,
        tipo='cursos',
        modelo=Curso,
        campos_obrigatorios=['nome', 'sigla', 'instituicao_id'],
        campos_unico=['sigla', 'instituicao_id']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/turmas')
@login_required
def importar_turmas():
    caminho = request.args.get('caminho')
    processar_importacao(
        caminho=caminho,
        tipo='turmas',
        modelo=Turma,
        campos_obrigatorios=['nome', 'codigo', 'turno', 'curso_id', 'instituicao_id'],
        campos_unico=['codigo']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/alunos')
@login_required
def importar_alunos():
    caminho = request.args.get('caminho')
    processar_importacao(
        caminho=caminho,
        tipo='alunos',
        modelo=Aluno,
        campos_obrigatorios=['nome', 'email', 'matricula', 'turma_id'],
        campos_unico=['email', 'matricula']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/professores')
@login_required
def importar_professores():
    caminho = request.args.get('caminho')
    processar_importacao(
        caminho=caminho,
        tipo='professores',
        modelo=Professor,
        campos_obrigatorios=['nome', 'email'],
        campos_unico=['email']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/disciplinas')
@login_required
def importar_disciplinas():
    caminho = request.args.get('caminho')
    processar_importacao(
        caminho=caminho,
        tipo='disciplinas',
        modelo=Disciplina,
        campos_obrigatorios=['nome', 'sigla', 'turma_id', 'professor_id'],
        campos_unico=['sigla', 'turma_id']
    )
    return redirect(url_for('painel.painel'))

@painel_bp.route('/template/<nome>')
@login_required
def baixar_template(nome):
    """Serve template files for download"""
    try:
        caminho = os.path.join(current_app.root_path, TEMPLATES_FOLDER)
        return send_from_directory(caminho, nome, as_attachment=True)
    except Exception as e:
        flash(f"Erro ao baixar template: {str(e)}", 'danger')
        current_app.logger.error(f"Erro ao baixar template {nome}: {str(e)}")
        return redirect(url_for('painel.importar'))

@painel_bp.route('/')
@login_required
def painel():
    """Dashboard with statistics and import history"""
    try:
        # Basic statistics
        stats = {
            'instituicoes': Instituicao.query.count(),
            'turmas': Turma.query.count(),
            'alunos': Aluno.query.count(),
            'professores': Professor.query.count(),
            'disciplinas': Disciplina.query.count()
        }

        # Data for charts
        alunos_por_turma = db.session.query(
            Turma.nome.label('turma'),
            func.count(Aluno.id).label('quantidade')
        ).join(Aluno).group_by(Turma.id).order_by(desc('quantidade')).limit(10).all()

        disciplinas_por_professor = db.session.query(
            Professor.nome.label('professor'),
            func.count(Disciplina.id).label('quantidade')
        ).join(Disciplina).group_by(Professor.id).order_by(desc('quantidade')).limit(10).all()

        # Import history
        historico_importacoes = Importacao.query.order_by(desc(Importacao.data)).limit(5).all()
        ultima_importacao = Importacao.query.order_by(desc(Importacao.data)).first()

        return render_template(
            'painel/painel.html',
            stats=stats,
            alunos_por_turma=alunos_por_turma,
            disciplinas_por_professor=disciplinas_por_professor,
            historico_importacoes=historico_importacoes,
            ultima_importacao=ultima_importacao,
            tipos=['instituicoes', 'cursos', 'turmas', 'alunos', 'professores', 'disciplinas']
        )
    except Exception as e:
        flash(f"Erro ao carregar painel: {str(e)}", 'danger')
        current_app.logger.error(f"Erro no painel: {str(e)}")
        return render_template('painel/painel.html')
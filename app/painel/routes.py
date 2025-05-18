import os
import pandas as pd
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.models import Instituicao, Curso, Turma, Aluno, Professor, Disciplina

painel_bp = Blueprint('painel', __name__, url_prefix='/painel')

@painel_bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    tipos = ['instituicoes', 'cursos', 'turmas', 'alunos', 'professores', 'disciplinas']
    if request.method == 'POST':
        tipo = request.form['tipo']
        arquivo = request.files['arquivo']

        if not arquivo:
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(url_for('painel.importar'))

        nome = secure_filename(arquivo.filename)
        caminho = os.path.join('uploads', nome)
        os.makedirs('uploads', exist_ok=True)
        arquivo.save(caminho)

        return redirect(url_for(f'painel.importar_{tipo}', caminho=caminho))

    return render_template('painel/importar.html', tipos=tipos)

@painel_bp.route('/importar/instituicoes')
@login_required
def importar_instituicoes():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        inseridos, ignorados = 0, 0
        for _, row in df.iterrows():
            nome = str(row['nome']).strip()
            sigla = str(row['sigla']).strip()
            cidade = str(row['cidade']).strip()
            tipo = str(row['tipo']).strip()
            media = float(row.get('media', 7.0))
            
            if not nome or not sigla:
                continue
                
            existe = Instituicao.query.filter_by(sigla=sigla).first()
            if existe:
                ignorados += 1
                continue
                
            db.session.add(Instituicao(
                nome=nome,
                sigla=sigla,
                cidade=cidade,
                tipo=tipo,
                media=media
            ))
            inseridos += 1
            
        db.session.commit()
        flash(f'Instituições importadas: {inseridos} | Ignoradas: {ignorados}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/cursos')
@login_required
def importar_cursos():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        inseridos, ignorados = 0, 0
        for _, row in df.iterrows():
            nome = str(row['nome']).strip()
            sigla = str(row['sigla']).strip()
            instituicao_id = int(row['instituicao_id'])
            
            if not nome or not sigla:
                continue
                
            existe = Curso.query.filter_by(sigla=sigla, instituicao_id=instituicao_id).first()
            if existe:
                ignorados += 1
                continue
                
            db.session.add(Curso(
                nome=nome,
                sigla=sigla,
                instituicao_id=instituicao_id
            ))
            inseridos += 1
            
        db.session.commit()
        flash(f'Cursos importados: {inseridos} | Ignorados: {ignorados}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/turmas')
@login_required
def importar_turmas():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        inseridos, ignorados = 0, 0
        for _, row in df.iterrows():
            nome = str(row['nome']).strip()
            codigo = str(row['codigo']).strip()
            turno = str(row['turno']).strip()
            curso_id = int(row['curso_id'])
            instituicao_id = int(row['instituicao_id'])
            
            if not codigo:
                continue
                
            existe = Turma.query.filter_by(codigo=codigo).first()
            if existe:
                ignorados += 1
                continue
                
            db.session.add(Turma(
                nome=nome,
                codigo=codigo,
                turno=turno,
                curso_id=curso_id,
                instituicao_id=instituicao_id
            ))
            inseridos += 1
            
        db.session.commit()
        flash(f'Turmas importadas: {inseridos} | Ignoradas: {ignorados}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/alunos')
@login_required
def importar_alunos():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        inseridos, ignorados = 0, 0
        for _, row in df.iterrows():
            nome = str(row['nome']).strip()
            email = str(row['email']).strip().lower()
            matricula = str(row['matricula']).strip()
            turma_id = int(row['turma_id'])
            
            if not email or not matricula or not nome:
                continue
                
            existe = Aluno.query.filter((Aluno.email == email) | (Aluno.matricula == matricula)).first()
            if existe:
                ignorados += 1
                continue
                
            db.session.add(Aluno(
                nome=nome,
                email=email,
                matricula=matricula,
                turma_id=turma_id
            ))
            inseridos += 1
            
        db.session.commit()
        flash(f'Alunos importados: {inseridos} | Ignorados: {ignorados}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/professores')
@login_required
def importar_professores():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        inseridos, ignorados = 0, 0
        for _, row in df.iterrows():
            nome = str(row['nome']).strip()
            email = str(row['email']).strip().lower()
            
            if not email or not nome:
                continue
                
            existe = Professor.query.filter_by(email=email).first()
            if existe:
                ignorados += 1
                continue
                
            db.session.add(Professor(
                nome=nome,
                email=email
            ))
            inseridos += 1
            
        db.session.commit()
        flash(f'Professores importados: {inseridos} | Ignorados: {ignorados}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/disciplinas')
@login_required
def importar_disciplinas():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        inseridos, ignorados = 0, 0
        for _, row in df.iterrows():
            nome = str(row['nome']).strip()
            sigla = str(row['sigla']).strip()
            turma_id = int(row['turma_id'])
            professor_id = int(row['professor_id'])
            
            if not sigla or not turma_id:
                continue
                
            existe = Disciplina.query.filter_by(sigla=sigla, turma_id=turma_id).first()
            if existe:
                ignorados += 1
                continue
                
            db.session.add(Disciplina(
                nome=nome,
                sigla=sigla,
                turma_id=turma_id,
                professor_id=professor_id
            ))
            inseridos += 1
            
        db.session.commit()
        flash(f'Disciplinas importadas: {inseridos} | Ignoradas: {ignorados}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)
    return redirect(url_for('painel.painel'))

@painel_bp.route('/')
@login_required
def painel():
    total_instituicoes = Instituicao.query.count()
    total_turmas = Turma.query.count()
    total_alunos = Aluno.query.count()
    total_professores = Professor.query.count()
    return render_template(
        'painel/painel.html',
        total_instituicoes=total_instituicoes,
        total_turmas=total_turmas,
        total_alunos=total_alunos,
        total_professores=total_professores
    )
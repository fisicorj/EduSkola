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
    from flask import render_template
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

# Handlers individuais

@painel_bp.route('/importar/instituicoes')
@login_required
def importar_instituicoes():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        for _, row in df.iterrows():
            item = Instituicao(nome=row['nome'], sigla=row['sigla'], cidade=row['cidade'], tipo=row['tipo'], media=row.get('media', 7.0))
            db.session.add(item)
        db.session.commit()
        flash('Instituições importadas com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/cursos')
@login_required
def importar_cursos():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        for _, row in df.iterrows():
            item = Curso(nome=row['nome'], sigla=row['sigla'], instituicao_id=row['instituicao_id'])
            db.session.add(item)
        db.session.commit()
        flash('Cursos importados com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/turmas')
@login_required
def importar_turmas():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        for _, row in df.iterrows():
            item = Turma(nome=row['nome'], codigo=row['codigo'], turno=row['turno'],
                         curso_id=row['curso_id'], instituicao_id=row['instituicao_id'])
            db.session.add(item)
        db.session.commit()
        flash('Turmas importadas com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/alunos')
@login_required
def importar_alunos():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        for _, row in df.iterrows():
            item = Aluno(nome=row['nome'], email=row['email'], matricula=row['matricula'], turma_id=row['turma_id'])
            db.session.add(item)
        db.session.commit()
        flash('Alunos importados com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/professores')
@login_required
def importar_professores():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        for _, row in df.iterrows():
            item = Professor(nome=row['nome'], email=row['email'])
            db.session.add(item)
        db.session.commit()
        flash('Professores importados com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('painel.painel'))

@painel_bp.route('/importar/disciplinas')
@login_required
def importar_disciplinas():
    caminho = request.args.get('caminho')
    try:
        df = pd.read_excel(caminho) if caminho.endswith('.xlsx') else pd.read_csv(caminho)
        for _, row in df.iterrows():
            item = Disciplina(nome=row['nome'], sigla=row['sigla'], turma_id=row['turma_id'], professor_id=row['professor_id'])
            db.session.add(item)
        db.session.commit()
        flash('Disciplinas importadas com sucesso.', 'success')
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('painel.painel'))


@painel_bp.route('/')
@login_required
def painel():
    total = Instituicao.query.count()
    total_turmas = Turma.query.count()
    return render_template('painel/painel.html', total=total, total_turmas=total_turmas)

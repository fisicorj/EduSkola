from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Curso, Instituicao, Disciplina, CursoDisciplina

cursos_bp = Blueprint('cursos', __name__, url_prefix='/cursos')

@cursos_bp.route('/')
@login_required
def listar():
    cursos = Curso.query.all()
    return render_template('cursos/listar.html', cursos=cursos)

@cursos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        curso = Curso(
            nome=request.form['nome'],
            sigla=request.form['sigla'],
            instituicao_id=request.form['instituicao_id']
        )
        db.session.add(curso)
        db.session.commit()
        flash('Curso cadastrado com sucesso.', 'success')
        return redirect(url_for('cursos.listar'))
    instituicoes = Instituicao.query.all()
    return render_template('cursos/form.html', titulo='Novo Curso', instituicoes=instituicoes)

@cursos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    curso = Curso.query.get_or_404(id)
    if request.method == 'POST':
        curso.nome = request.form['nome']
        curso.sigla = request.form['sigla']
        curso.instituicao_id = request.form['instituicao_id']
        db.session.commit()
        flash('Curso atualizado.', 'info')
        return redirect(url_for('cursos.listar'))
    instituicoes = Instituicao.query.all()
    return render_template('cursos/form.html', curso=curso, titulo='Editar Curso', instituicoes=instituicoes)

@cursos_bp.route('/<int:id>/disciplinas', methods=['GET', 'POST'])
@login_required
def gerenciar_disciplinas(id):
    curso = Curso.query.get_or_404(id)
    disciplinas_todas = Disciplina.query.all()
    if request.method == 'POST':
        CursoDisciplina.query.filter_by(curso_id=curso.id).delete()
        for disciplina_id in request.form.getlist('disciplinas'):
            disciplina = Disciplina.query.get(int(disciplina_id))
            if disciplina:
                associacao = CursoDisciplina(curso=curso, disciplina=disciplina)
                db.session.add(associacao)
        db.session.commit()
        flash('Disciplinas atualizadas para o curso.', 'success')
        return redirect(url_for('cursos.listar'))
    return render_template('cursos/disciplinas.html', curso=curso, disciplinas_todas=disciplinas_todas)

@cursos_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    curso = Curso.query.get_or_404(id)
    db.session.delete(curso)
    db.session.commit()
    flash('Curso excluído.', 'danger')
    return redirect(url_for('cursos.listar'))
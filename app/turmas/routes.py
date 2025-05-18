from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Turma, Instituicao, Curso

turmas_bp = Blueprint('turmas', __name__, url_prefix='/turmas')

@turmas_bp.route('/')
@login_required
def listar():
    turmas = Turma.query.all()
    return render_template('turmas/listar.html', turmas=turmas)

@turmas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if request.method == 'POST':
        t = Turma(
            nome=request.form['nome'],
            codigo=request.form['codigo'],
            turno=request.form['turno'],
            curso_id=request.form['curso_id'],
            instituicao_id=request.form['instituicao_id']
        )
        db.session.add(t)
        db.session.commit()
        flash('Turma cadastrada com sucesso.', 'success')
        return redirect(url_for('turmas.listar'))
    instituicoes = Instituicao.query.all()
    cursos = Curso.query.all()
    return render_template('turmas/form.html', titulo='Nova Turma', instituicoes=instituicoes)
    cursos = Curso.query.all()
    return render_template('turmas/form.html', titulo='Nova Turma', cursos=cursos)

@turmas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    t = Turma.query.get_or_404(id)
    if request.method == 'POST':
        t.nome = request.form['nome']
        t.codigo = request.form['codigo']
        t.turno = request.form['turno']
        t.curso_id = request.form['curso_id']
        t.instituicao_id = request.form['instituicao_id']
        db.session.commit()
        flash('Turma atualizada.', 'info')
        return redirect(url_for('turmas.listar'))
    instituicoes = Instituicao.query.all()
    cursos = Curso.query.all()
    return render_template('turmas/form.html', turma=t, titulo='Editar Turma', instituicoes=instituicoes)

@turmas_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    t = Turma.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash('Turma excluída.', 'danger')
    return redirect(url_for('turmas.listar'))
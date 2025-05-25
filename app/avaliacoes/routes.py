from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Avaliacao, Turma, Disciplina, SemestreLetivo

avaliacoes_bp = Blueprint('avaliacoes', __name__, url_prefix='/avaliacoes')

from app.models import Avaliacao, Turma, SemestreLetivo, Disciplina

@avaliacoes_bp.route('/')
@login_required
def listar():
    turma_id = request.args.get('turma_id', type=int)
    semestre_id = request.args.get('semestre_id', type=int)
    disciplina_id = request.args.get('disciplina_id', type=int)

    turmas = Turma.query.all()
    semestres = SemestreLetivo.query.all()
    disciplinas = Disciplina.query.all()

    avaliacoes_query = Avaliacao.query

    if turma_id:
        avaliacoes_query = avaliacoes_query.filter_by(turma_id=turma_id)
    if disciplina_id:
        avaliacoes_query = avaliacoes_query.filter_by(disciplina_id=disciplina_id)
    elif semestre_id:
        avaliacoes_query = avaliacoes_query.join(Turma).filter(Turma.semestre_letivo_id == semestre_id)

    avaliacoes = avaliacoes_query.all()

    return render_template('avaliacoes/listar.html',
                           avaliacoes=avaliacoes, 
                           turmas=turmas,
                           semestres=semestres,
                           disciplinas=disciplinas,
                           turma_id=turma_id, 
                           semestre_id=semestre_id, 
                           disciplina_id=disciplina_id)



@avaliacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        nome = request.form['nome']
        peso = float(request.form['peso'])
        turma_id = request.form['turma_id']
        disciplina_id = request.form['disciplina_id']
        semestre_letivo_id = request.form['semestre_letivo_id']

        avaliacao = Avaliacao(
            nome=nome,
            peso=peso,
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            semestre_letivo_id=semestre_letivo_id
        )
        db.session.add(avaliacao)
        db.session.commit()
        flash('Avaliação cadastrada com sucesso.', 'success')
        return redirect(url_for('avaliacoes.listar'))

    return render_template('avaliacoes/form.html', titulo='Nova Avaliação', 
                           turmas=turmas, disciplinas=disciplinas, semestres=semestres)

@avaliacoes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    avaliacao = Avaliacao.query.get_or_404(id)
    turmas = Turma.query.all()
    disciplinas = Disciplina.query.all()
    semestres = SemestreLetivo.query.all()

    if request.method == 'POST':
        avaliacao.nome = request.form['nome']
        avaliacao.peso = float(request.form['peso'])
        avaliacao.turma_id = request.form['turma_id']
        avaliacao.disciplina_id = request.form['disciplina_id']
        avaliacao.semestre_letivo_id = request.form['semestre_letivo_id']
        
        db.session.commit()
        flash('Avaliação atualizada com sucesso.', 'info')
        return redirect(url_for('avaliacoes.listar'))

    return render_template('avaliacoes/form.html',
                           titulo='Editar Avaliação',
                           avaliacao=avaliacao,
                           turmas=turmas,
                           disciplinas=disciplinas,
                           semestres=semestres)


@avaliacoes_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    avaliacao = Avaliacao.query.get_or_404(id)
    db.session.delete(avaliacao)
    db.session.commit()
    flash('Avaliação excluída.', 'danger')
    return redirect(url_for('avaliacoes.listar'))

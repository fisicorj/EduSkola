from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Professor

professores_bp = Blueprint('professores', __name__, url_prefix='/professores')

@professores_bp.route('/')
@login_required
def listar():
    professores = Professor.query.all()
    return render_template('professores/listar.html', professores=professores)

@professores_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        if Professor.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'danger')
            return redirect(url_for('professores.novo'))
        prof = Professor(nome=nome, email=email)
        db.session.add(prof)
        db.session.commit()
        flash('Professor cadastrado com sucesso.', 'success')
        return redirect(url_for('professores.listar'))
    return render_template('professores/form.html', titulo='Novo Professor')

@professores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    prof = Professor.query.get_or_404(id)
    if request.method == 'POST':
        prof.nome = request.form['nome']
        prof.email = request.form['email']
        db.session.commit()
        flash('Professor atualizado com sucesso.', 'info')
        return redirect(url_for('professores.listar'))
    return render_template('professores/form.html', professor=prof, titulo='Editar Professor')

@professores_bp.route('/excluir/<int:id>')
@login_required
def excluir(id):
    prof = Professor.query.get_or_404(id)
    db.session.delete(prof)
    db.session.commit()
    flash('Professor excluído com sucesso.', 'danger')
    return redirect(url_for('professores.listar'))
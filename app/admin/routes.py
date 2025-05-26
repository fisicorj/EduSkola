from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from app.utils.file_utils import save_file
from app.auth.decorators import role_required  #Importa o decorador
from app import db
from app.models import User

admin_bp = Blueprint('admin', __name__)

def allowed_file(filename):
    """Verifica se a extensão do arquivo é segura."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@admin_bp.route('/admin')
@role_required('admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/coordenacao')
@role_required('admin', 'coordenador')
def coordenacao_dashboard():
    return render_template('coordenacao/dashboard.html')

@admin_bp.route('/perfil')
@role_required('admin', 'coordenador', 'professor')
def perfil_dashboard():
    return render_template('perfil/dashboard.html')

@admin_bp.route('/usuarios')
@login_required
@role_required('admin')
def listar_usuarios():
    perfil = request.args.get('perfil')
    busca = request.args.get('busca')

    query = User.query

    if perfil:
        query = query.filter_by(role=perfil)

    if busca:
        query = query.filter(User.username.ilike(f"%{busca}%"))

    page = request.args.get('page', 1, type=int)
    per_page = 10  # Ajuste conforme necessário
    pagination = query.paginate(page=page, per_page=per_page)

    return render_template(
        'admin/listar_usuarios.html',
        pagination=pagination,
        usuarios=pagination.items,
        perfil=perfil,
        busca=busca
    )

@admin_bp.route('/usuarios/cadastro', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def cadastro_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        avatar = request.files.get('avatar')

        # Dados para professor
        nome = request.form.get('nome')
        email = request.form.get('email')

        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'warning')
            return redirect(url_for('admin.cadastro_usuario'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)

        # Processamento de avatar
        if avatar and avatar.filename != '':
            filename = save_file(avatar, 'app/static/uploads')
            if filename:
                new_user.avatar = filename
            else:
                flash('Tipo de arquivo não permitido.', 'danger')
                return redirect(url_for('admin.cadastro_usuario'))

        db.session.add(new_user)
        db.session.flush()  # Garante que new_user.id já existe.

        # Se for professor, cria automaticamente o Professor associado
        if role == 'professor':
            if not nome or not email:
                flash('Nome e E-mail são obrigatórios para cadastrar Professor.', 'danger')
                db.session.rollback()
                return redirect(url_for('admin.cadastro_usuario'))
            from app.models import Professor
            professor = Professor(nome=nome, email=email, user_id=new_user.id)
            db.session.add(professor)

        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('admin.listar_usuarios'))

    return render_template('admin/cadastro_usuario.html')


@admin_bp.route('/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_usuario(user_id):
    usuario = User.query.get_or_404(user_id)

    if request.method == 'POST':
        usuario.username = request.form['username']
        usuario.role = request.form['role']

        # Atualiza ou cria dados do Professor se perfil for professor
        if usuario.role == 'professor':
            nome = request.form.get('nome')
            email = request.form.get('email')

            if usuario.professor:
                # Atualiza professor existente
                usuario.professor.nome = nome
                usuario.professor.email = email
            else:
                # Cria novo professor associado
                from app.models import Professor  # Importa local para evitar loops
                novo_professor = Professor(nome=nome, email=email, user=usuario)
                db.session.add(novo_professor)
        else:
            # Se não for mais professor, remove associação
            if usuario.professor:
                db.session.delete(usuario.professor)

        # Atualiza avatar, se enviado
        avatar = request.files.get('avatar')
        if avatar and avatar.filename != '':
            filename = save_file(avatar, 'app/static/uploads')
            if filename:
                usuario.avatar = filename
            else:
                flash('Tipo de arquivo não permitido.', 'danger')
                return redirect(url_for('admin.editar_usuario', user_id=user_id))

        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.listar_usuarios'))

    return render_template('admin/editar_usuario.html', usuario=usuario)


@admin_bp.route('/usuarios/excluir/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def excluir_usuario(user_id):
    usuario = User.query.get_or_404(user_id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuarios/trocar_senha/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def trocar_senha(user_id):
    usuario = User.query.get_or_404(user_id)
    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        usuario.password = generate_password_hash(nova_senha)
        db.session.commit()
        flash('Senha atualizada com sucesso!', 'success')
        return redirect(url_for('admin.listar_usuarios'))
    return render_template('admin/trocar_senha.html', usuario=usuario)
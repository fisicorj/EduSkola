from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

   # dentro da função create_app()
    migrate = Migrate(app, db)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.models import User
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', password=generate_password_hash('admin123'))
            db.session.add(user)
            db.session.commit()

    from app.auth.routes import auth_bp
    from app.painel.routes import painel_bp
    from app.instituicoes.routes import inst_bp
    from app.disciplinas.routes import disciplinas_bp
    from app.turmas.routes import turmas_bp
    from app.cursos.routes import cursos_bp
    from app.professores.routes import professores_bp
    from app.alunos.routes import alunos_bp
    from app.avaliacoes.routes import avaliacoes_bp
    from app.notas.routes import notas_bp
    from app.semestres.routes import semestres_bp

    
    app.register_blueprint(auth_bp)
    app.register_blueprint(painel_bp)
    app.register_blueprint(inst_bp)
    app.register_blueprint(disciplinas_bp)
    app.register_blueprint(turmas_bp)
    app.register_blueprint(cursos_bp)
    app.register_blueprint(professores_bp)
    app.register_blueprint(alunos_bp)
    app.register_blueprint(avaliacoes_bp)
    app.register_blueprint(notas_bp)
    app.register_blueprint(semestres_bp)


    return app
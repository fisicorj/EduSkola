from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.extensions import db, login_manager, migrate, mail
from flask_migrate import Migrate
from app.config import DevelopmentConfig  # ou ProductionConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    mail.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

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
    from app.admin.routes import admin_bp

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
    app.register_blueprint(admin_bp)

    return app

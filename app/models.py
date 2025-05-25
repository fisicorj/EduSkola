from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
class Instituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    cidade = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # Pública ou Privada
    media_aprovacao = db.Column(db.Float, nullable=False, default=5.0)

    cursos = db.relationship('Curso', backref='instituicao', lazy=True)
    turmas = db.relationship('Turma', backref='instituicao', lazy=True)

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(20), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)

    turmas = db.relationship('Turma', backref='curso', lazy=True)

class Turma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    turno = db.Column(db.String(20), nullable=False)  # Manhã, Tarde, Noite
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    disciplinas = db.relationship('Disciplina', backref='turma', lazy=True)

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)

    disciplinas = db.relationship('Disciplina', backref='professor', lazy=True)

class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'))
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)

from app import db

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    matricula = db.Column(db.String(20), nullable=False, unique=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)
    semestre_letivo = db.relationship('SemestreLetivo', backref='alunos')
    notas = db.relationship('Nota', back_populates='aluno', cascade='all, delete-orphan')

class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    peso = db.Column(db.Float, nullable=False, default=0.0)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)
    turma = db.relationship('Turma', backref='avaliacoes')
    disciplina = db.relationship('Disciplina', backref='avaliacoes')
    semestre_letivo = db.relationship('SemestreLetivo', backref='avaliacoes')


class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacao.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)

    aluno = db.relationship('Aluno', backref='notas', lazy=True)
    avaliacao = db.relationship('Avaliacao', backref='notas', lazy=True)

class Importacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)
    detalhes = db.Column(db.Text)
    usuario_id = db.Column(db.Integer,db.ForeignKey('user.id', name='fk_importacao_usuario'),nullable=True)
    usuario = db.relationship('User', backref='importacoes')

class SemestreLetivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    semestre = db.Column(db.Integer, nullable=False)  # 1 ou 2
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)

    turmas = db.relationship('Turma', backref='semestre_letivo', lazy=True)
    disciplinas = db.relationship('Disciplina', backref='semestre_letivo', lazy=True)

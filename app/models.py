from app import db
from flask_login import UserMixin

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

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    matricula = db.Column(db.String(20), nullable=False, unique=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)

class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    peso = db.Column(db.Float, nullable=False, default=0.0)
    
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)

    turma = db.relationship('Turma', backref='avaliacoes')
    disciplina = db.relationship('Disciplina', backref='avaliacoes')

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacao.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)

    aluno = db.relationship('Aluno', backref='notas', lazy=True)
    avaliacao = db.relationship('Avaliacao', backref='notas', lazy=True)


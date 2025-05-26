from app import db
from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

# Modelo Associativo

class DisciplinaTurmaProfessor(db.Model):
    __tablename__ = 'disciplina_turma_professor'
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), primary_key=True)
    disciplina = db.relationship('Disciplina', backref='associacoes')
    turma = db.relationship('Turma', backref='associacoes')
    professor = db.relationship('Professor', backref='associacoes')

# Modelos

# Modelos principais

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='professor')
    professor = db.relationship('Professor', backref='user', uselist=False, lazy=True)

class Instituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    cidade = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
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
    turno = db.Column(db.String(20), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    avaliacoes = db.relationship('Avaliacao', backref='turma', lazy=True)
    # Acesso às disciplinas via associacoes

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    # Acesso às disciplinas via associacoes

class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)
    avaliacoes = db.relationship('Avaliacao', backref='disciplina', lazy=True)
    # Acesso a turmas e professores via associacoes

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    matricula = db.Column(db.String(20), nullable=False, unique=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)
    semestre_letivo = db.relationship('SemestreLetivo', backref='alunos')
    notas = db.relationship('Nota', backref='aluno', cascade="all, delete", lazy=True)

class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    peso = db.Column(db.Float, nullable=False, default=0.0)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    semestre_letivo_id = db.Column(db.Integer, db.ForeignKey('semestre_letivo.id'), nullable=False)
    notas = db.relationship('Nota', backref='avaliacao', lazy=True)

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacao.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)

class Importacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)
    detalhes = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_importacao_usuario'), nullable=True)
    usuario = db.relationship('User', backref='importacoes')

class SemestreLetivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    turmas = db.relationship('Turma', backref='semestre_letivo', lazy=True)
    disciplinas = db.relationship('Disciplina', backref='semestre_letivo', lazy=True)
    avaliacoes = db.relationship('Avaliacao', backref='semestre_letivo', lazy=True)
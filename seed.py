from app import create_app, db
from app.models import Instituicao, Curso, Turma, Aluno, Professor
import random

app = create_app()
with app.app_context():
    # Apagar dados anteriores respeitando a ordem de dependência
    db.session.query(Aluno).delete()
    db.session.query(Turma).delete()
    db.session.query(Curso).delete()
    db.session.query(Professor).delete()
    db.session.query(Instituicao).delete()
    db.session.commit()

    # 1. Criar instituições
    i1 = Instituicao(nome="Instituto Federal A", sigla="IFA", cidade="São Paulo", tipo="Pública", media_aprovacao=6.0)
    i2 = Instituicao(nome="Universidade B", sigla="UNIB", cidade="Rio de Janeiro", tipo="Privada", media_aprovacao=7.0)
    i3 = Instituicao(nome="Faculdade C", sigla="FAC", cidade="Belo Horizonte", tipo="Privada", media_aprovacao=5.5)
    db.session.add_all([i1, i2, i3])
    db.session.commit()

    # 2. Criar cursos
    c1 = Curso(nome="Engenharia da Computação", sigla="ENGCOMP", instituicao_id=i1.id)
    c2 = Curso(nome="Administração", sigla="ADM", instituicao_id=i1.id)
    c3 = Curso(nome="Direito", sigla="DIR", instituicao_id=i2.id)
    c4 = Curso(nome="Pedagogia", sigla="PED", instituicao_id=i3.id)
    c5 = Curso(nome="Ciência de Dados", sigla="CDA", instituicao_id=i3.id)
    db.session.add_all([c1, c2, c3, c4, c5])
    db.session.commit()

    # 3. Criar professores
    professores = []
    for i in range(1, 6):
        p = Professor(nome=f"Professor {i}", email=f"prof{i}@teste.com")
        db.session.add(p)
        professores.append(p)
    db.session.commit()

    # 4. Criar turmas
    turnos = ["Manhã", "Tarde", "Noite"]
    t1 = Turma(nome="Turma A", codigo="TURMA01", turno=turnos[0], curso_id=c1.id, instituicao_id=c1.instituicao_id)
    t2 = Turma(nome="Turma B", codigo="TURMA02", turno=turnos[1], curso_id=c2.id, instituicao_id=c2.instituicao_id)
    t3 = Turma(nome="Turma C", codigo="TURMA03", turno=turnos[2], curso_id=c3.id, instituicao_id=c3.instituicao_id)
    t4 = Turma(nome="Turma D", codigo="TURMA04", turno=turnos[0], curso_id=c4.id, instituicao_id=c4.instituicao_id)
    t5 = Turma(nome="Turma E", codigo="TURMA05", turno=turnos[1], curso_id=c5.id, instituicao_id=c5.instituicao_id)
    t6 = Turma(nome="Turma F", codigo="TURMA06", turno=turnos[2], curso_id=c1.id, instituicao_id=c1.instituicao_id)
    db.session.add_all([t1, t2, t3, t4, t5, t6])
    db.session.commit()

    # 5. Criar alunos
    turmas = [t1, t2, t3, t4, t5, t6]
    for i in range(1, 21):
        turma = random.choice(turmas)
        aluno = Aluno(
            nome=f"Aluno {i}",
            email=f"aluno{i}@teste.com",
            matricula=f"2024{i:03}",
            turma_id=turma.id
        )
        db.session.add(aluno)

    db.session.commit()
    print("Base de dados esvaziada e repovoada com sucesso!")
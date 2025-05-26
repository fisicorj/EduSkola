from app import create_app, db
from app.models import Instituicao, Curso, Turma, Aluno, Professor, Disciplina, Avaliacao, Nota, SemestreLetivo, DisciplinaTurmaProfessor
from datetime import date
import random

app = create_app()

with app.app_context():
    # ⚠️ Limpeza das tabelas (em ambiente de desenvolvimento)
    db.session.query(Nota).delete()
    db.session.query(Avaliacao).delete()
    db.session.query(Aluno).delete()
    db.session.query(DisciplinaTurmaProfessor).delete()
    db.session.query(Disciplina).delete()
    db.session.query(Turma).delete()
    db.session.query(Curso).delete()
    db.session.query(Professor).delete()
    db.session.query(Instituicao).delete()
    db.session.query(SemestreLetivo).delete()
    db.session.commit()

    # ✅ Criar Semestres Letivos
    semestres = [
        SemestreLetivo(ano=2024, semestre=1, data_inicio=date(2024, 2, 1), data_fim=date(2024, 6, 30)),
        SemestreLetivo(ano=2024, semestre=2, data_inicio=date(2024, 8, 1), data_fim=date(2024, 12, 15)),
        SemestreLetivo(ano=2025, semestre=1, data_inicio=date(2025, 2, 1), data_fim=date(2025, 6, 30)),
        SemestreLetivo(ano=2025, semestre=2, data_inicio=date(2025, 8, 1), data_fim=date(2025, 12, 15))
    ]
    db.session.add_all(semestres)
    db.session.commit()

    # ✅ Criar Instituições
    inst1 = Instituicao(nome='Instituto Alpha', sigla='IAL', cidade='São Paulo', tipo='Pública', media_aprovacao=6.0)
    inst2 = Instituicao(nome='Faculdade Beta', sigla='FAB', cidade='Rio de Janeiro', tipo='Privada', media_aprovacao=7.0)
    db.session.add_all([inst1, inst2])
    db.session.commit()

    # ✅ Criar Cursos
    curso1 = Curso(nome='Engenharia de Software', sigla='ESW', instituicao_id=inst1.id)
    curso2 = Curso(nome='Administração', sigla='ADM', instituicao_id=inst2.id)
    db.session.add_all([curso1, curso2])
    db.session.commit()

    # ✅ Criar Professores
    professores = [
        Professor(nome='João Silva', email='joao.silva@ial.edu.br'),
        Professor(nome='Maria Souza', email='maria.souza@fab.edu.br')
    ]
    db.session.add_all(professores)
    db.session.commit()

    # ✅ Criar Turmas
    turmas = []
    for i, sem in enumerate(semestres):
        turma = Turma(
            nome=f'Turma {chr(65 + i)}',
            codigo=f'TURMA{chr(65 + i)}',
            turno=random.choice(['Manhã', 'Tarde', 'Noite']),
            curso_id=curso1.id if i % 2 == 0 else curso2.id,
            instituicao_id=curso1.instituicao_id if i % 2 == 0 else curso2.instituicao_id,
            semestre_letivo_id=sem.id
        )
        turmas.append(turma)
    db.session.add_all(turmas)
    db.session.commit()

    # ✅ Criar Disciplinas
    disciplinas = []
    for nome_disciplina in ['Algoritmos', 'Matemática', 'Gestão']:
        disciplina = Disciplina(
            nome=nome_disciplina,
            sigla=nome_disciplina[:3].upper(),
            semestre_letivo_id=random.choice(semestres).id
        )
        db.session.add(disciplina)
        disciplinas.append(disciplina)
    db.session.commit()

    # ✅ Criar associações Disciplina - Turma - Professor
    for disciplina in disciplinas:
        for turma in random.sample(turmas, k=random.randint(1, len(turmas))):
            prof = random.choice(professores)
            assoc = DisciplinaTurmaProfessor(
                disciplina_id=disciplina.id,
                turma_id=turma.id,
                professor_id=prof.id
            )
            db.session.add(assoc)
    db.session.commit()

    # ✅ Criar Alunos
    for i in range(1, 21):
        turma = random.choice(turmas)
        aluno = Aluno(
            nome=f'Aluno {i}',
            email=f'aluno{i}@exemplo.com',
            matricula=f'2024{i:03}',
            turma_id=turma.id,
            semestre_letivo_id=turma.semestre_letivo_id
        )
        db.session.add(aluno)
    db.session.commit()

    # ✅ Criar Avaliações e Notas
    alunos = Aluno.query.all()
    for assoc in DisciplinaTurmaProfessor.query.all():
        for i in range(1, 4):  # P1, P2, P3
            avaliacao = Avaliacao(
                nome=f'P{i}',
                peso=0.3,
                turma_id=assoc.turma_id,
                disciplina_id=assoc.disciplina_id,
                semestre_letivo_id=assoc.turma.semestre_letivo_id
            )
            db.session.add(avaliacao)
            db.session.commit()

            for aluno in [a for a in alunos if a.turma_id == assoc.turma_id]:
                nota = Nota(
                    aluno_id=aluno.id,
                    avaliacao_id=avaliacao.id,
                    valor=round(random.uniform(0.0, 10.0), 2)
                )
                db.session.add(nota)
    db.session.commit()

    print('✅ Base de dados populada com sucesso!')

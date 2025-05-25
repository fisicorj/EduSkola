import pandas as pd
import os

def gerar_templates_xlsx(pasta_destino='modelos'):
    os.makedirs(pasta_destino, exist_ok=True)

    templates = {
        'instituicoes.xlsx': ['nome', 'sigla', 'cidade', 'tipo', 'media'],
        'cursos.xlsx': ['nome', 'sigla', 'instituicao_id'],
        'turmas.xlsx': ['nome', 'codigo', 'turno', 'curso_id', 'instituicao_id', 'semestre_letivo_id'],
        'professores.xlsx': ['nome', 'email'],
        'alunos.xlsx': ['nome', 'email', 'matricula', 'turma_id', 'semestre_letivo_id'],
        'disciplinas.xlsx': ['nome', 'sigla', 'turma_id', 'professor_id', 'semestre_letivo_id'],
        'avaliacoes.xlsx': ['nome', 'peso', 'turma_id', 'disciplina_id', 'semestre_letivo_id']
    }

    for nome_arquivo, colunas in templates.items():
        df = pd.DataFrame(columns=colunas)
        caminho = os.path.join(pasta_destino, nome_arquivo)
        df.to_excel(caminho, index=False)
        print(f"Template criado: {caminho}")

if __name__ == '__main__':
    gerar_templates_xlsx()
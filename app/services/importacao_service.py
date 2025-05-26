import os
import pandas as pd
from flask import current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Importacao
from datetime import datetime

class ImportacaoService:
    TIPOS_SUPORTADOS = ['instituicoes', 'cursos', 'turmas', 'alunos', 'professores', 'disciplinas']
    UPLOAD_FOLDER = 'uploads'

    @staticmethod
    def processar_upload(tipo, arquivo, usuario):
        """Processa o upload de arquivo e chama a importação correspondente."""
        if tipo not in ImportacaoService.TIPOS_SUPORTADOS:
            raise ValueError(f"Tipo de importação não suportado: {tipo}")

        if not ImportacaoService._allowed_file(arquivo.filename):
            raise ValueError("Tipo de arquivo não permitido. Use CSV ou XLSX.")

        os.makedirs(ImportacaoService.UPLOAD_FOLDER, exist_ok=True)
        nome = secure_filename(arquivo.filename)
        caminho = os.path.join(ImportacaoService.UPLOAD_FOLDER, nome)
        arquivo.save(caminho)

        # Determina o modelo e os campos conforme o tipo
        from app.models import Instituicao, Curso, Turma, Aluno, Professor, Disciplina

        config = {
            'instituicoes': {'modelo': Instituicao, 'campos': ['nome', 'sigla', 'cidade', 'tipo', 'media_aprovacao'], 'unico': ['sigla']},
            'cursos': {'modelo': Curso, 'campos': ['nome', 'sigla', 'instituicao_id'], 'unico': ['sigla', 'instituicao_id']},
            'turmas': {'modelo': Turma, 'campos': ['nome', 'codigo', 'turno', 'curso_id', 'instituicao_id', 'semestre_letivo_id'], 'unico': ['codigo']},
            'alunos': {'modelo': Aluno, 'campos': ['nome', 'email', 'matricula', 'turma_id', 'semestre_letivo_id'], 'unico': ['email', 'matricula']},
            'professores': {'modelo': Professor, 'campos': ['nome', 'email'], 'unico': ['email']},
            'disciplinas': {'modelo': Disciplina, 'campos': ['nome', 'sigla', 'turma_id', 'professor_id', 'semestre_letivo_id'], 'unico': ['sigla', 'turma_id']}
        }

        conf = config[tipo]

        ImportacaoService._processar_importacao(
            caminho=caminho,
            tipo=tipo,
            modelo=conf['modelo'],
            campos_obrigatorios=conf['campos'],
            campos_unico=conf['unico'],
            usuario=usuario
        )

    @staticmethod
    def _processar_importacao(caminho, tipo, modelo, campos_obrigatorios, campos_unico, usuario):
        """Processa efetivamente a importação de um arquivo para o modelo."""
        try:
            if caminho.endswith('.xlsx'):
                df = pd.read_excel(caminho, dtype=str)
            else:
                df = pd.read_csv(caminho, dtype=str)

            df = df.where(pd.notnull(df), None)

            inseridos, ignorados, erros = 0, 0, 0

            for index, row in df.iterrows():
                try:
                    dados = {campo: str(row[campo]).strip() for campo in campos_obrigatorios}

                    # Checa unicidade
                    filtro = {campo: dados[campo] for campo in campos_unico}
                    if modelo.query.filter_by(**filtro).first():
                        ignorados += 1
                        continue

                    db.session.add(modelo(**dados))
                    inseridos += 1

                except Exception as e:
                    erros += 1
                    current_app.logger.warning(f"Erro linha {index+1}: {str(e)}")

            db.session.commit()

            mensagem = f"{tipo.capitalize()} importados: {inseridos}, Ignorados: {ignorados}, Erros: {erros}"
            ImportacaoService._registrar_importacao(tipo, 'sucesso', mensagem, usuario)

        except Exception as e:
            db.session.rollback()
            mensagem = f"Erro ao importar {tipo}: {str(e)}"
            ImportacaoService._registrar_importacao(tipo, 'erro', mensagem, usuario)
            raise e
        finally:
            if os.path.exists(caminho):
                os.remove(caminho)

    @staticmethod
    def _registrar_importacao(tipo, status, detalhes, usuario):
        """Registra log da importação no banco."""
        try:
            registro = Importacao(
                tipo=tipo,
                status=status,
                detalhes=detalhes,
                usuario_id=usuario.id,
                data=datetime.now()
            )
            db.session.add(registro)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao registrar importação: {str(e)}")

    @staticmethod
    def _allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}
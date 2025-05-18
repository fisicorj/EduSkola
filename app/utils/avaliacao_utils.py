def calcular_media(aluno, disciplina, turma):
    avaliacoes = disciplina.avaliacoes
    notas_dict = { (n.avaliacao_id): n.valor for n in aluno.notas }

    media = 0
    peso_total = 0

    for avaliacao in avaliacoes:
        if avaliacao.turma_id != turma.id:
            continue  # pular avaliações de outras turmas
        nota = notas_dict.get(avaliacao.id)
        if nota is not None:
            media += nota * avaliacao.peso
            peso_total += avaliacao.peso

    if peso_total == 0:
        return None  # ainda sem notas suficientes
    return round(media / peso_total, 2)

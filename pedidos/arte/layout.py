"""Cálculo das posições das peças na folha A4 (em milímetros)."""

A4_LARGURA_MM = 210
A4_ALTURA_MM = 297
MARGEM_MM = 10
ESPACO_MM = 4  # distância entre as peças, para o corte


def posicoes_na_folha(largura_mm, altura_mm, itens_por_folha):
    """Devolve a lista de (x, y) do canto inferior esquerdo de cada peça.

    A grade é preenchida da esquerda para a direita, de cima para baixo.
    Se o kit pedir mais itens do que cabem na folha, vale o que cabe.
    """
    colunas = int((A4_LARGURA_MM - 2 * MARGEM_MM + ESPACO_MM) // (largura_mm + ESPACO_MM))
    linhas = int((A4_ALTURA_MM - 2 * MARGEM_MM + ESPACO_MM) // (altura_mm + ESPACO_MM))
    capacidade = min(itens_por_folha, colunas * linhas)
    if capacidade < 1:
        raise ValueError("A peça é grande demais para caber em uma folha A4.")

    posicoes = []
    for indice in range(capacidade):
        linha, coluna = divmod(indice, colunas)
        x = MARGEM_MM + coluna * (largura_mm + ESPACO_MM)
        y = A4_ALTURA_MM - MARGEM_MM - (linha + 1) * altura_mm - linha * ESPACO_MM
        posicoes.append((x, y))
    return posicoes

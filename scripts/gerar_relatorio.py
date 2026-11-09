"""Apresenta os resultados do notebook em um PDF de exatamente duas páginas."""

import json
import os
from datetime import date
from pathlib import Path
from textwrap import fill


def numero(valor, casas=0):
    return f"{valor:,.{casas}f}".translate(str.maketrans({",": ".", ".": ","}))


def data_pt(valor):
    return date.fromisoformat(valor).strftime("%d/%m/%Y")


def gerar_relatorio(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    os.environ.setdefault("MPLCONFIGDIR", str(root / ".cache/matplotlib"))
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.patches import Rectangle

    reports = root / "reports"
    resumo = json.loads((reports / "resumo_resultados.json").read_text(encoding="utf-8"))
    destino = reports / "relatorio_executivo.pdf"
    azul = "#153547"
    texto = "#263b48"

    def pagina(numero_pagina, titulo, subtitulo):
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        fig.text(0.07, 0.963, "FABIANA · PROJETO EDA",
                 fontsize=9, color="#287c8e", weight="bold")
        fig.text(0.07, 0.927, titulo, fontsize=21, color=azul, weight="bold")
        fig.text(0.07, 0.902, subtitulo, fontsize=9, color=texto)
        fig.text(0.07, 0.043, "Fonte: COVID Tracking Project · CSV histórico e cálculos do notebook",
                 fontsize=7.5, color=texto, url="https://covidtracking.com/data/download/")
        fig.text(0.07, 0.028, "Definições: covidtracking.com/about-data/data-definitions/",
                 fontsize=7.5, color=texto,
                 url="https://covidtracking.com/about-data/data-definitions/")
        fig.text(0.93, 0.03, f"{numero_pagina}/2", ha="right", fontsize=8, color=texto)
        return fig

    def paragrafo(fig, y, texto_paragrafo, width=103, size=9.5):
        wrapped = fill(texto_paragrafo, width=width)
        fig.text(0.07, y, wrapped, fontsize=size, color=texto, va="top", linespacing=1.4)
        return y - (wrapped.count("\n") + 1) * 0.016 - 0.012

    with PdfPages(destino, metadata={
        "Title": "COVID-19 nos Estados Unidos — relatório executivo",
        "Author": "Projeto EDA de Fabiana",
        "Subject": "Análise exploratória histórica, nível médio",
    }) as pdf:
        fig = pagina(1, "COVID-19 nos Estados Unidos",
                     f"Relatório executivo · Dados de {data_pt(resumo['data_inicial'])} a {data_pt(resumo['data_final'])}")
        cards = [
            ("CASOS ACUMULADOS", numero(resumo["total_casos"])),
            ("ÓBITOS ACUMULADOS", numero(resumo["total_obitos"])),
            ("JURISDIÇÕES", str(resumo["jurisdicoes"])),
        ]
        for i, (label, valor) in enumerate(cards):
            x = 0.07 + i * 0.295
            fig.add_artist(Rectangle((x, 0.811), 0.275, 0.066,
                                     transform=fig.transFigure, color="#eef5f6"))
            fig.text(x + 0.012, 0.855, label, fontsize=7.5, color=texto)
            fig.text(x + 0.012, 0.824, valor, fontsize=17, color=azul, weight="bold")
        fig.text(0.07, 0.79, f"Acumulados na mesma data: {data_pt(resumo['data_final'])}. Valores absolutos, sem ajuste populacional.",
                 fontsize=8.5, color=texto)
        ax = fig.add_axes([0.055, 0.36, 0.89, 0.41])
        ax.imshow(mpimg.imread(reports / "figures/06_evolucao_temporal.png"))
        ax.axis("off")
        fig.text(0.07, 0.329, "Maior volume de registros no fim de 2020 e início de 2021",
                 fontsize=12, color=azul, weight="bold")
        y = paragrafo(fig, 0.303,
            f"O maior incremento diário de casos foi {numero(resumo['pico_casos_valor'])}, em "
            f"{data_pt(resumo['pico_casos_data'])}. O de óbitos foi {numero(resumo['pico_obitos_valor'])}, "
            f"em {data_pt(resumo['pico_obitos_data'])}. São máximos de registros líquidos; "
            "não necessariamente máximos de ocorrências nessas datas.")
        y = paragrafo(fig, y,
            f"Entre os meses completos, {resumo['mes_maior_casos']} teve o maior total de incrementos "
            f"de casos: {numero(resumo['mes_maior_casos_valor'])}. Março de 2021 contém somente sete dias "
            "e não entra nessa comparação.")
        paragrafo(fig, y,
            f"A série exibida usa {resumo['dias_cobertura_completa']} dias com registros das "
            f"{resumo['jurisdicoes']} jurisdições, desde {data_pt(resumo['inicio_cobertura_completa'])}. "
            "A média móvel de sete dias facilita a leitura. Notificações atrasadas e revisões "
            "impedem interpretar a distância entre os picos como um intervalo biológico.")
        pdf.savefig(fig)
        plt.close(fig)

        fig = pagina(2, "Concentração e limites da análise",
                     "Decisões devem considerar o volume registrado e a qualidade da informação.")
        paragrafo(fig, 0.87,
            f"Califórnia, Texas e Flórida concentram {numero(resumo['top3_participacao_pct'], 1)}% "
            "dos casos acumulados na data final. Isso mede participação no total registrado, "
            "não risco por habitante.")
        ax = fig.add_axes([0.055, 0.455, 0.89, 0.365])
        ax.imshow(mpimg.imread(reports / "figures/04_ranking_casos.png"))
        ax.axis("off")
        fig.text(0.07, 0.431, "Uma associação forte, com interpretação limitada",
                 fontsize=12, color=azul, weight="bold")
        y = paragrafo(fig, 0.407,
            f"Casos e óbitos acumulados têm correlação de Pearson r = "
            f"{numero(resumo['correlacao_casos_obitos'], 3)} nas {resumo['pares_casos_obitos']} "
            "jurisdições. População, detecção e critérios de registro podem influenciar os dois "
            "totais. A correlação não estabelece causalidade nem estima o risco individual.")
        fig.text(0.07, y - 0.005, "Qualidade dos dados: decisões que preservam o significado",
                 fontsize=11.5, color=azul, weight="bold")
        y = paragrafo(fig, y - 0.032,
            f"Foram analisadas {numero(resumo['linhas_brutas'])} linhas e {resumo['colunas_brutas']} "
            f"colunas originais. Não houve duplicados exatos. "
            f"{resumo['colunas_mais_80_pct_nulos']} colunas têm mais de 80% de nulos; "
            f"faltam {numero(resumo['nulos_hospitalizacao'])} registros do indicador hospitalar.")
        y = paragrafo(fig, y,
            f"Preservamos os nulos, {resumo['correcoes_casos']} incrementos negativos de casos e "
            f"{resumo['correcoes_obitos']} de óbitos. Ausência não significa zero; revisões não "
            "devem ser apagadas. Valores atípicos são sinalizados, sem exclusão automática.")
        paragrafo(fig, y,
            "Próximo passo recomendado: acrescentar população para comparar taxas, verificar "
            "a cobertura de cada indicador e usar uma fonte atualizada para decisões atuais. "
            "Este estudo descreve registros históricos até março de 2021.")
        pdf.savefig(fig)
        plt.close(fig)
    return destino


if __name__ == "__main__":
    print(gerar_relatorio())

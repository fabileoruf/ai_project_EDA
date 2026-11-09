"""Presenta los resultados del notebook en un PDF de exactamente dos páginas."""

import json
import os
from datetime import date
from pathlib import Path
from textwrap import fill


def numero(valor, decimales=0):
    return f"{valor:,.{decimales}f}".translate(str.maketrans({",": ".", ".": ","}))


def fecha_es(valor):
    return date.fromisoformat(valor).strftime("%d/%m/%Y")


def generar_informe(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    os.environ.setdefault("MPLCONFIGDIR", str(root / ".cache/matplotlib"))
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.patches import Rectangle

    reports = root / "reports"
    resumen = json.loads((reports / "resumen_resultados.json").read_text(encoding="utf-8"))
    destino = reports / "informe_ejecutivo.pdf"
    azul = "#153547"
    texto = "#263b48"

    def pagina(numero_pagina, titulo, subtitulo):
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        fig.text(0.07, 0.963, "FABIANA · PROYECTO EDA",
                 fontsize=9, color="#287c8e", weight="bold")
        fig.text(0.07, 0.927, titulo, fontsize=21, color=azul, weight="bold")
        fig.text(0.07, 0.902, subtitulo, fontsize=9, color=texto)
        fig.text(0.07, 0.043, "Fuente: COVID Tracking Project · CSV histórico y cálculos del notebook",
                 fontsize=7.5, color=texto, url="https://covidtracking.com/data/download/")
        fig.text(0.07, 0.028, "Definiciones: covidtracking.com/about-data/data-definitions/",
                 fontsize=7.5, color=texto,
                 url="https://covidtracking.com/about-data/data-definitions/")
        fig.text(0.93, 0.03, f"{numero_pagina}/2", ha="right", fontsize=8, color=texto)
        return fig

    def parrafo(fig, y, texto_parrafo, width=103, size=9.5):
        wrapped = fill(texto_parrafo, width=width)
        fig.text(0.07, y, wrapped, fontsize=size, color=texto, va="top", linespacing=1.4)
        return y - (wrapped.count("\n") + 1) * 0.016 - 0.012

    with PdfPages(destino, metadata={
        "Title": "COVID-19 en Estados Unidos — informe ejecutivo",
        "Author": "Proyecto EDA de Fabiana",
        "Subject": "Análisis exploratorio histórico, nivel medio",
    }) as pdf:
        fig = pagina(1, "COVID-19 en Estados Unidos",
                     f"Informe ejecutivo · Datos del {fecha_es(resumen['fecha_inicial'])} al {fecha_es(resumen['fecha_final'])}")
        tarjetas = [
            ("CASOS ACUMULADOS", numero(resumen["total_casos"])),
            ("FALLECIMIENTOS ACUMULADOS", numero(resumen["total_fallecimientos"])),
            ("JURISDICCIONES", str(resumen["jurisdicciones"])),
        ]
        for i, (etiqueta, valor) in enumerate(tarjetas):
            x = 0.07 + i * 0.295
            fig.add_artist(Rectangle((x, 0.811), 0.275, 0.066,
                                     transform=fig.transFigure, color="#eef5f6"))
            fig.text(x + 0.012, 0.855, etiqueta, fontsize=7.5, color=texto)
            fig.text(x + 0.012, 0.824, valor, fontsize=17, color=azul, weight="bold")
        fig.text(0.07, 0.79, f"Acumulados en la misma fecha: {fecha_es(resumen['fecha_final'])}. Valores absolutos, sin ajuste por población.",
                 fontsize=8.5, color=texto)
        ax = fig.add_axes([0.055, 0.36, 0.89, 0.41])
        ax.imshow(mpimg.imread(reports / "figures/06_evolucion_temporal.png"))
        ax.axis("off")
        fig.text(0.07, 0.329, "Mayor volumen de registros a finales de 2020 y principios de 2021",
                 fontsize=11.5, color=azul, weight="bold")
        y = parrafo(fig, 0.303,
            f"El mayor incremento diario de casos fue {numero(resumen['pico_casos_valor'])}, el "
            f"{fecha_es(resumen['fecha_pico_casos'])}. El de fallecimientos fue {numero(resumen['pico_fallecimientos_valor'])}, "
            f"el {fecha_es(resumen['fecha_pico_fallecimientos'])}. Son máximos de registros netos; "
            "no necesariamente de hechos ocurridos en esas fechas.")
        y = parrafo(fig, y,
            f"Entre los meses completos, {resumen['mes_mayor_casos']} presentó el mayor total de incrementos "
            f"de casos: {numero(resumen['mes_mayor_casos_valor'])}. Marzo de 2021 solo contiene siete días "
            "y no entra en esta comparación.")
        parrafo(fig, y,
            f"La serie mostrada utiliza {resumen['dias_cobertura_completa']} días con registros de las "
            f"{resumen['jurisdicciones']} jurisdicciones, desde el {fecha_es(resumen['inicio_cobertura_completa'])}. "
            "La media móvil de siete días facilita la lectura. Las notificaciones atrasadas y las revisiones "
            "impiden interpretar la distancia entre los picos como un intervalo biológico.")
        pdf.savefig(fig)
        plt.close(fig)

        fig = pagina(2, "Concentración y límites del análisis",
                     "Las decisiones deben considerar el volumen registrado y la calidad de la información.")
        parrafo(fig, 0.87,
            f"California, Texas y Florida concentran el {numero(resumen['top3_participacion_pct'], 1)}% "
            "de los casos acumulados en la fecha final. Esto mide su participación en el total registrado, "
            "no el riesgo por habitante.")
        ax = fig.add_axes([0.055, 0.455, 0.89, 0.365])
        ax.imshow(mpimg.imread(reports / "figures/04_ranking_casos.png"))
        ax.axis("off")
        fig.text(0.07, 0.431, "Una asociación fuerte, con una interpretación limitada",
                 fontsize=12, color=azul, weight="bold")
        y = parrafo(fig, 0.407,
            f"Los casos y los fallecimientos acumulados tienen una correlación de Pearson r = "
            f"{numero(resumen['correlacion_casos_fallecimientos'], 3)} en las {resumen['pares_casos_fallecimientos']} "
            "jurisdicciones. La población, la detección y los criterios de registro pueden influir en ambos "
            "totales. La correlación no establece causalidad ni estima el riesgo individual.")
        fig.text(0.07, y - 0.005, "Calidad de los datos: decisiones que conservan su significado",
                 fontsize=11.5, color=azul, weight="bold")
        y = parrafo(fig, y - 0.032,
            f"Se analizaron {numero(resumen['filas_brutas'])} filas y {resumen['columnas_brutas']} "
            f"columnas originales. No hubo duplicados exactos. "
            f"{resumen['columnas_mas_80_pct_nulos']} columnas tienen más del 80% de nulos; "
            f"faltan {numero(resumen['nulos_hospitalizacion'])} valores del indicador hospitalario.")
        y = parrafo(fig, y,
            f"Conservamos los nulos, {resumen['correcciones_casos']} incrementos negativos de casos y "
            f"{resumen['correcciones_fallecimientos']} de fallecimientos. La ausencia no significa cero; las revisiones "
            "no deben borrarse. Los valores atípicos se señalan sin eliminarlos automáticamente.")
        parrafo(fig, y,
            "Siguiente paso recomendado: añadir población para comparar tasas, comprobar la cobertura "
            "de cada indicador y utilizar una fuente actualizada para decisiones actuales. "
            "Este estudio describe registros históricos hasta marzo de 2021.")
        pdf.savefig(fig)
        plt.close(fig)
    return destino


if __name__ == "__main__":
    print(generar_informe())

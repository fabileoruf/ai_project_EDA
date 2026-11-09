# EDA de COVID-19 en Estados Unidos — nivel medio

Proyecto de Fabiana para Factoria F5: comprender, limpiar, explorar y comunicar los datos históricos del COVID Tracking Project. El notebook está escrito en español, con explicaciones antes del código e interpretación de los resultados.

Se conserva íntegramente el [enunciado original](docs/enunciado.md). El [notebook de Elena Almansa Campos](https://github.com/elenaalmansacampos/ai_project_EDA/blob/main/notebooks/eda_covid19.ipynb) se consultó como referencia de organización; esta versión desarrolla el nivel medio, con decisiones y cálculos propios.

## Por dónde empezar

1. Abre [notebooks/eda_covid19.ipynb](notebooks/eda_covid19.ipynb).
2. Lee las secciones **1 y 1.1**, que convierten el encargo en preguntas y explican qué representa una fila.
3. Para usar Google Colab dentro de VS Code, sigue la configuración de abajo y selecciona **Select Kernel → Colab → Auto Connect**. Para ejecutar en tu ordenador, selecciona el Python de **.venv**.
4. Lee cada explicación, ejecuta la siguiente celda con **Shift + Enter** y observa la salida.
5. Al terminar, utiliza **Restart Kernel** y **Run All** para comprobar la reproducibilidad.

El notebook tiene 70 celdas, de las cuales 33 contienen código. El recorrido de estudio se divide en los bloques indicados más abajo.

## Qué vamos a investigar

- ¿Cómo evolucionaron los incrementos diarios registrados de casos y fallecimientos?
- ¿Qué jurisdicciones concentraron más casos acumulados en la misma fecha final?
- ¿Existe asociación entre los casos y los fallecimientos acumulados por jurisdicción?
- ¿Qué problemas de calidad limitan la interpretación de los indicadores?

## Fuente y significado de los datos

- **Fuente primaria:** [COVID Tracking Project](https://covidtracking.com/data/download/).
- **Archivo oficial:** <https://api.covidtracking.com/v1/states/daily.csv>.
- **Diccionario:** [definiciones oficiales](https://covidtracking.com/about-data/data-definitions/).
- **Dimensiones observadas:** 20.780 filas y 56 columnas originales.
- **Unidad de observación:** un estado o territorio en una fecha de recogida/notificación.
- **Cobertura:** 56 jurisdicciones, incluidos los estados, el Distrito de Columbia y los territorios.
- **Periodo observado:** del 13/01/2020 al 07/03/2021. La fuente dejó de recopilar datos; no son datos actuales.
- **Procedencia local:** [data/raw/covid_us.metadata.json](data/raw/covid_us.metadata.json) registra la URL, la fecha de descarga, el tamaño y el SHA-256.

La primera ejecución descarga el CSV; las siguientes utilizan la copia local. El archivo original se conserva y no se incluye en Git. El notebook guarda otra tabla en `data/processed/covid_us_clean.csv`, manteniendo los nulos y las revisiones.

## Instalación

Entorno utilizado: **Python 3.14.6**. Las versiones de las bibliotecas principales están fijadas en [requirements.txt](requirements.txt).

En el terminal, desde la carpeta del proyecto:

```bash
bash scripts/preparar_entorno.sh
```

Este comando crea `.venv` si es necesario, instala las bibliotecas y descarga el CSV oficial. La primera preparación necesita conexión a Internet. El script utiliza `uv` cuando está disponible y `pip` como alternativa.

Para instalar manualmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/descargar_datos.py
```

## Ejecutar el notebook

### Google Colab dentro de VS Code

1. Abre esta carpeta en VS Code. En **Extensions** (`Cmd + Shift + X` en Mac), instala la extensión oficial [Colab, de Google](https://marketplace.visualstudio.com/items?itemName=google.colab) y **Jupyter**, de Microsoft. El proyecto recomienda estas extensiones.
2. Abre [notebooks/eda_covid19.ipynb](notebooks/eda_covid19.ipynb) y pulsa **Select Kernel → Colab → Auto Connect**. Si aparece **Select Another Kernel**, entra primero en esa opción. Inicia sesión con tu cuenta de Google cuando se solicite. Este EDA puede ejecutarse con CPU.
3. Después de conectar, haz clic derecho en la carpeta **scripts** del explorador de VS Code y elige **Upload to Colab**. Comprueba en **Colab → Contents** que existe `/content/scripts/descargar_datos.py`. Envía la carpeta `scripts` completa para incluir también `generar_informe.py`.
4. Ejecuta las celdas en orden con **Shift + Enter**, empezando por la sección 2. La primera celda busca los scripts en el proyecto local o en `/content`. El notebook descarga el CSV oficial en el servidor de Colab.
5. Guarda el notebook con **Cmd + S** para conservar las celdas y sus salidas en el archivo local.

En Colab, Python y las bibliotecas pertenecen al servidor remoto; no hace falta instalar `.venv` localmente. Utiliza primero las bibliotecas incluidas en Colab. Si falta alguna, ejecuta en una celda temporal:

```python
%pip install pandas numpy matplotlib seaborn requests
```

Después reinicia el kernel y ejecuta el notebook de nuevo. El `requirements.txt` documenta el entorno local con Python 3.14.6; las versiones disponibles en Colab pueden ser diferentes.

**Dónde se guardan los archivos:** los gráficos, las tablas, el CSV y el PDF se generan en el servidor de Colab, dentro de la carpeta indicada por `ROOT`. No se copian automáticamente al ordenador y pueden desaparecer al eliminar el servidor. Para conservar los resultados en Google Drive, utiliza **Colab: Mount Google Drive to Server...** en la paleta de comandos, ejecuta la celda que inserte la extensión y, después del análisis, ejecuta:

```python
from pathlib import Path
import shutil

destino = Path("/content/drive/MyDrive/ai_project_EDA")
shutil.copytree(ROOT / "reports", destino / "reports", dirs_exist_ok=True)
shutil.copytree(ROOT / "data", destino / "data", dirs_exist_ok=True)
print("Resultados guardados en:", destino)
```

Utiliza la ruta de montaje indicada por la extensión si es diferente de `/content/drive`. Estas copias sustituyen los archivos con el mismo nombre en esa carpeta de Drive. Al conectar con un servidor nuevo, vuelve a enviar la carpeta `scripts`.

Referencia: [guía oficial de la extensión Colab](https://github.com/googlecolab/colab-vscode/wiki/User-Guide).

### Python local en VS Code o JupyterLab

En VS Code, abre el notebook y selecciona el intérprete `.venv/bin/python`. Si se solicita, instala las extensiones Python y Jupyter.

También puedes iniciar JupyterLab desde el terminal:

```bash
source .venv/bin/activate
jupyter lab notebooks/eda_covid19.ipynb
```

Para ejecutar todo desde el terminal y guardar las salidas:

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=180 notebooks/eda_covid19.ipynb
```

La ejecución completa genera tablas, nueve gráficos, conclusiones y el informe ejecutivo. Para regenerar únicamente el PDF después de ejecutar el notebook:

```bash
.venv/bin/python scripts/generar_informe.py
```

## Recorrido de estudio, paso a paso

| Bloque | Secciones | Qué debes ser capaz de explicar |
|---|---|---|
| Comprender el problema | 1 y 1.1 | El encargo; qué representa una fila; acumulado, incremento y nulo |
| Cargar y observar | 2 a 4 | Entorno virtual, DataFrame, shape, head, info y describe |
| Limpiar con justificación | 5 | Clave única, copia exacta, conflicto, tipos, selección y nulos |
| Construir información | 6 | Año, mes, día de la semana e indicadores de revisión |
| Explorar distribuciones | 7 y 8 | Histograma, recuento, boxplot y candidatos a valores atípicos |
| Resumir y relacionar | 9 y 10 | groupby, agg, pivot_table, clasificación y dispersión |
| Analizar tiempo y asociación | 11 y 12 | Cobertura, meses completos, tendencias y correlación |
| Comunicar resultados | 13 a 15 | Respuestas fundamentadas, limitaciones e informe ejecutivo |

## Decisiones metodológicas

- **Duplicados:** eliminar únicamente copias exactas; detener el análisis ante valores contradictorios para estado + fecha. No se encontraron duplicados en esta base.
- **Nulos:** conservarlos. Un dato no informado no equivale a cero. No imputamos la media, la mediana ni el último acumulado conocido.
- **Incrementos negativos:** conservarlos e identificarlos como revisiones. Sustituirlos por cero alteraría los totales netos.
- **Acumulados:** compararlos en una fecha común, el 07/03/2021. No sumar acumulados de varios días.
- **Cobertura temporal:** utilizar los 357 días con registros de las 56 jurisdicciones e incrementos conocidos, del 16/03/2020 al 07/03/2021, para los picos y la serie comparable.
- **Meses parciales:** identificarlos y excluirlos de la clasificación de meses completos. Marzo de 2021 solo contiene siete días.
- **Valores atípicos:** señalarlos mediante la regla del IQR, sin eliminarlos automáticamente ni asumir que son errores.
- **Pruebas diagnósticas:** mantener las columnas seleccionadas como referencia de calidad; no mezclar unidades heterogéneas para estimar la positividad.
- **Comparaciones:** los totales no están ajustados por población. La correlación no implica causalidad ni mide el riesgo individual.

## Entregables

| Archivo o carpeta | Contenido |
|---|---|
| [Notebook](notebooks/eda_covid19.ipynb) | Análisis completo y explicaciones paso a paso |
| [Informe ejecutivo](reports/informe_ejecutivo.pdf) | Dos páginas para un público no técnico |
| [Conclusiones](reports/conclusiones.md) | Respuestas a las cuatro preguntas |
| [Resumen de resultados](reports/resumen_resultados.json) | Cifras utilizadas para generar el informe |
| [Gráficos](reports/figures/) | Nueve figuras exportadas |
| [Tablas](reports/tables/) | Calidad, decisiones, agrupaciones, valores atípicos y correlaciones |
| [Dependencias](requirements.txt) | Bibliotecas y versiones principales |

## Comprobar el nivel medio

La entrega incluye el nivel esencial: inspección, limpieza justificada, tres variables univariadas, tres relaciones bivariadas, al menos cinco gráficos, respuestas y texto explicativo. Añade IQR/valores atípicos, `groupby`, `agg`, `pivot_table`, cinco variables nuevas, un mapa de calor de correlación, tendencias temporales y un informe de dos páginas.

El repositorio Git con mensajes de commit claros también forma parte del enunciado. Antes de entregar, comprueba `git status` y `git remote -v`, organiza las ramas y registra los cambios con mensajes descriptivos. El `.gitignore` excluye el entorno virtual, las cachés y las copias CSV; el notebook, el informe, los gráficos y las instrucciones forman parte de la entrega.

# EDA de COVID-19 nos Estados Unidos — nível médio

Projeto de Fabiana para a Factoria F5: entender, limpar, explorar e comunicar os dados históricos do COVID Tracking Project. O notebook foi escrito em português, com explicações antes do código e interpretação dos resultados.

O [enunciado original em espanhol](docs/enunciado.md) foi preservado integralmente. O [notebook da Elena Almansa Campos](https://github.com/elenaalmansacampos/ai_project_EDA/blob/main/notebooks/eda_covid19.ipynb) foi consultado como referência de organização; esta versão desenvolve o nível médio, com decisões e cálculos próprios.

## Por onde começar

1. Abra [notebooks/eda_covid19.ipynb](notebooks/eda_covid19.ipynb).
2. Leia as etapas **1 e 1.1**, que traduzem o pedido em perguntas e explicam o significado de uma linha.
3. Para usar Google Colab dentro do VS Code, siga a configuração abaixo e selecione **Select Kernel → Colab → Auto Connect**. Para executar no computador, selecione o Python da pasta **.venv**.
4. Leia cada explicação, execute a próxima célula com **Shift + Enter** e observe a saída.
5. Ao terminar, use **Restart Kernel** e **Run All** para conferir a reprodução.

O notebook tem 70 células, das quais 33 são de código. Não é necessário aprender tudo de uma vez: o roteiro de estudo está dividido em blocos abaixo.

## O que vamos investigar

- Como evoluíram os incrementos diários registrados de casos e óbitos?
- Quais jurisdições concentraram mais casos acumulados na mesma data final?
- Existe associação entre casos e óbitos acumulados entre jurisdições?
- Quais problemas de qualidade limitam a interpretação dos indicadores?

## Fonte e significado dos dados

- **Fonte primária:** [COVID Tracking Project](https://covidtracking.com/data/download/).
- **Arquivo oficial:** <https://api.covidtracking.com/v1/states/daily.csv>.
- **Dicionário:** [definições oficiais](https://covidtracking.com/about-data/data-definitions/).
- **Dimensão observada:** 20.780 linhas e 56 colunas originais.
- **Unidade de observação:** um estado ou território em uma data de coleta/notificação.
- **Cobertura:** 56 jurisdições, incluindo estados, Distrito de Colúmbia e territórios.
- **Período observado:** 13/01/2020 a 07/03/2021. A fonte encerrou a coleta; não são dados atuais.
- **Proveniência local:** [data/raw/covid_us.metadata.json](data/raw/covid_us.metadata.json) registra URL, data de download, tamanho e SHA-256.

A primeira execução baixa o CSV; as seguintes usam a cópia local. O arquivo bruto fica preservado e não é versionado. O notebook salva outra tabela em `data/processed/covid_us_clean.csv`, mantendo nulos e revisões.

## Instalação

Ambiente utilizado neste projeto: **Python 3.14.6**. As versões das bibliotecas principais estão fixadas em [requirements.txt](requirements.txt).

No terminal, dentro da pasta do projeto:

```bash
bash scripts/preparar_ambiente.sh
```

Esse comando cria `.venv` se necessário, instala as bibliotecas e baixa o CSV oficial. A primeira preparação precisa de acesso à internet. O script usa `uv` quando disponível e `pip` como alternativa.

Para instalar manualmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/baixar_dados.py
```

## Executar o notebook

### Google Colab dentro do VS Code

1. Abra esta pasta no VS Code. Em **Extensions** (`Cmd + Shift + X` no Mac), instale a extensão oficial [Colab, do Google](https://marketplace.visualstudio.com/items?itemName=google.colab) e a extensão **Jupyter**, da Microsoft. O projeto já recomenda essas extensões.
2. Abra [notebooks/eda_covid19.ipynb](notebooks/eda_covid19.ipynb) e clique em **Select Kernel → Colab → Auto Connect**. Se aparecer **Select Another Kernel**, entre nessa opção primeiro. Faça login com sua conta Google quando solicitado. Este EDA pode ser executado com CPU.
3. Depois de conectar, clique com o botão direito na pasta **scripts** do Explorer do VS Code e escolha **Upload to Colab**. Confirme no painel **Colab → Contents** que existe `/content/scripts/baixar_dados.py`. Envie a pasta `scripts` inteira para incluir também `gerar_relatorio.py`.
4. Execute as células em ordem com **Shift + Enter**, começando pela seção 2. A primeira célula procura os scripts no projeto local ou em `/content`. O CSV oficial será baixado pelo próprio notebook para o servidor Colab.
5. Salve o notebook com **Cmd + S** para guardar as células e suas saídas no arquivo local.

No Colab, o Python e as bibliotecas pertencem ao servidor remoto; a instalação local de `.venv` não é necessária. Use inicialmente as bibliotecas fornecidas pelo Colab. Se uma importação indicar que falta alguma delas, execute em uma célula temporária:

```python
%pip install pandas numpy matplotlib seaborn requests
```

Depois reinicie o kernel e execute o notebook novamente. O `requirements.txt` registra o ambiente local com Python 3.14.6; as versões disponíveis no Colab podem ser diferentes.

**Onde ficam os arquivos:** os gráficos, tabelas, CSV e PDF gerados ficam no servidor Colab, dentro da pasta indicada por `ROOT`. Eles não são copiados automaticamente para o computador e podem desaparecer quando o servidor for removido. Para guardar os resultados no Google Drive, use **Colab: Mount Google Drive to Server...** na paleta de comandos, execute a célula que a extensão inserir e, depois da análise, execute:

```python
from pathlib import Path
import shutil

destino = Path("/content/drive/MyDrive/ai_project_EDA")
shutil.copytree(ROOT / "reports", destino / "reports", dirs_exist_ok=True)
shutil.copytree(ROOT / "data", destino / "data", dirs_exist_ok=True)
print("Resultados salvos em:", destino)
```

Use o caminho de montagem mostrado pela extensão se ele for diferente de `/content/drive`. As cópias acima substituem arquivos de mesmo nome nessa pasta do Drive. Ao conectar a um servidor novo, envie novamente a pasta `scripts`.

Referência: [guia oficial da extensão Colab](https://github.com/googlecolab/colab-vscode/wiki/User-Guide).

### Python local no VS Code ou JupyterLab

No VS Code, abra o notebook e selecione o interpretador `.venv/bin/python`. Se solicitado, use as extensões Python e Jupyter.

Ou inicie o JupyterLab pelo terminal:

```bash
source .venv/bin/activate
jupyter lab notebooks/eda_covid19.ipynb
```

Para executar tudo pelo terminal e salvar as saídas:

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=180 notebooks/eda_covid19.ipynb
```

A execução completa gera tabelas, nove gráficos, conclusões e o relatório executivo. Para regenerar apenas o PDF depois de executar o notebook:

```bash
.venv/bin/python scripts/gerar_relatorio.py
```

## Roteiro de estudo, passo a passo

| Bloco | Etapas do notebook | O que você deve conseguir explicar |
|---|---|---|
| Entender o problema | 1 e 1.1 | O pedido do cliente; o que é uma linha; acumulado, incremento e nulo |
| Carregar e observar | 2 a 4 | Ambiente virtual, DataFrame, shape, head, info e describe |
| Limpar com justificativa | 5 | Chave única, cópia exata, conflito, tipos, seleção e nulos |
| Construir informação | 6 | Ano, mês, dia da semana e indicadores de revisão |
| Explorar distribuições | 7 e 8 | Histograma, contagem, boxplot e candidatos a outlier |
| Resumir e relacionar | 9 e 10 | groupby, agg, pivot_table, ranking e dispersão |
| Analisar tempo e associação | 11 e 12 | Cobertura, meses completos, tendências e correlação |
| Comunicar resultados | 13 a 15 | Respostas fundamentadas, limitações e relatório executivo |

## Decisões metodológicas

- **Duplicados:** remover somente cópias exatas; interromper diante de valores conflitantes para estado + data. Não foram encontrados duplicados nesta base.
- **Nulos:** preservar. Um dado não informado não equivale a zero. Não imputamos média, mediana nem o último acumulado conhecido.
- **Incrementos negativos:** conservar e identificar como revisões. Zerá-los alteraria os totais líquidos.
- **Acumulados:** comparar em uma data comum, 07/03/2021. Não somar acumulados de vários dias.
- **Cobertura temporal:** usar os 357 dias com registros das 56 jurisdições e incrementos conhecidos, de 16/03/2020 a 07/03/2021, para os picos e a série comparável.
- **Meses parciais:** identificar e excluir do ranking de meses completos. Março de 2021 contém apenas sete dias.
- **Outliers:** sinalizar pela regra do IQR, sem exclusão automática e sem presumir erro.
- **Testes:** manter as colunas selecionadas como referência de qualidade; não misturar unidades heterogêneas para estimar positividade.
- **Comparações:** os totais não são ajustados pela população. Correlação não é causalidade nem risco individual.

## Entregas

| Arquivo ou pasta | Conteúdo |
|---|---|
| [Notebook](notebooks/eda_covid19.ipynb) | Análise completa e explicações passo a passo |
| [Relatório executivo](reports/relatorio_executivo.pdf) | Duas páginas para público não técnico |
| [Conclusões](reports/conclusoes.md) | Respostas às quatro perguntas |
| [Resumo dos resultados](reports/resumo_resultados.json) | Números usados para gerar o relatório |
| [Gráficos](reports/figures/) | Nove figuras exportadas |
| [Tabelas](reports/tables/) | Qualidade, decisões, agrupamentos, outliers e correlações |
| [Dependências](requirements.txt) | Bibliotecas e versões principais |

## Conferir o nível médio

A entrega inclui o nível essencial: inspeção, limpeza justificada, três variáveis univariadas, três relações bivariadas, pelo menos cinco gráficos, respostas e texto explicativo. Acrescenta IQR/outliers, `groupby`, `agg`, `pivot_table`, cinco variáveis novas, heatmap de correlação, tendências temporais e relatório de duas páginas.

O repositório Git com commits claros também faz parte do enunciado. Antes da entrega, confira `git status` e `git remote -v`, trabalhe em uma branch própria e registre as etapas com mensagens que expliquem as mudanças. O `.gitignore` exclui o ambiente virtual, os caches e as cópias CSV; o notebook, o relatório, os gráficos e as instruções fazem parte da entrega.

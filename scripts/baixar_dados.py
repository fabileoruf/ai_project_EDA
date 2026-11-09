"""Baixa o CSV oficial uma vez e registra a origem, a data e o hash do arquivo."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/covid_us.csv"
URL = "https://api.covidtracking.com/v1/states/daily.csv"


def baixar_dados():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = DATA_PATH.with_suffix(".metadata.json")
    if DATA_PATH.exists():
        print(f"Usando o arquivo local: {DATA_PATH}")
    else:
        response = requests.get(URL, timeout=(15, 120))
        response.raise_for_status()
        content = response.content
        # Falhar claramente se o servidor devolver HTML ou um CSV inesperado.
        header = next(csv.reader(content.decode("utf-8-sig").splitlines()))
        required = {"date", "state", "positive", "death", "positiveIncrease"}
        if not required.issubset(header):
            raise ValueError("A resposta nao contem as colunas esperadas do CSV.")
        temporary = DATA_PATH.with_suffix(".part")
        temporary.write_bytes(content)
        temporary.replace(DATA_PATH)
        metadata_path.write_text(
            json.dumps(
                {
                    "source_url": URL,
                    "documentation": "https://covidtracking.com/about-data/data-definitions/",
                    "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "bytes": len(content),
                },
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"Dados oficiais salvos: {DATA_PATH}")
    return DATA_PATH


if __name__ == "__main__":
    baixar_dados()

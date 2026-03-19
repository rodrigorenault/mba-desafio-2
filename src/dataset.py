"""
Módulo para gestão de datasets de avaliação.

Responsabilidades:
1. Carregar dataset de avaliação de arquivo .jsonl
2. Criar/atualizar dataset no LangSmith
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from langsmith import Client


DEFAULT_JSONL_PATH = "datasets/bug_to_user_story.jsonl"


def load_dataset_from_jsonl(jsonl_path: str = DEFAULT_JSONL_PATH) -> List[Dict[str, Any]]:
    """
    Carrega exemplos de avaliação de um arquivo .jsonl.

    Cada linha do arquivo deve conter um objeto JSON com:
    - inputs: dict com os dados de entrada (ex: {"bug_report": "..."})
    - outputs: dict com a saída esperada (ex: {"reference": "..."})

    Args:
        jsonl_path: Caminho para o arquivo .jsonl

    Returns:
        Lista de dicionários com os exemplos
    """
    examples = []

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    example = json.loads(line)
                    examples.append(example)

        return examples

    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {jsonl_path}")
        print("\nCertifique-se de que o arquivo datasets/bug_to_user_story.jsonl existe.")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSONL: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        return []


def create_evaluation_dataset(
    client: Client,
    dataset_name: str,
    jsonl_path: str = DEFAULT_JSONL_PATH
) -> str:
    """
    Cria ou reutiliza um dataset de avaliação no LangSmith.

    Se o dataset já existir, reutiliza. Caso contrário, cria um novo
    com os exemplos do arquivo .jsonl.

    Args:
        client: Cliente LangSmith
        dataset_name: Nome do dataset
        jsonl_path: Caminho para o arquivo .jsonl

    Returns:
        Nome do dataset criado/existente
    """
    print(f"Criando dataset de avaliação: {dataset_name}...")

    examples = load_dataset_from_jsonl(jsonl_path)

    if not examples:
        print("❌ Nenhum exemplo carregado do arquivo .jsonl")
        return dataset_name

    print(f"  ✓ Carregados {len(examples)} exemplos do arquivo {jsonl_path}")

    try:
        datasets = client.list_datasets(dataset_name=dataset_name)
        existing_dataset = None

        for ds in datasets:
            if ds.name == dataset_name:
                existing_dataset = ds
                break

        if existing_dataset:
            print(f"  ✓ Dataset '{dataset_name}' já existe, usando existente")
            return dataset_name
        else:
            dataset = client.create_dataset(dataset_name=dataset_name)

            for example in examples:
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=example["inputs"],
                    outputs=example["outputs"]
                )

            print(f"  ✓ Dataset criado com {len(examples)} exemplos")
            return dataset_name

    except Exception as e:
        print(f"  ⚠️ Erro ao criar dataset: {e}")
        return dataset_name

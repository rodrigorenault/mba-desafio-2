"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt no Hub (ex: mba-test/bug_to_user_story_v2)
        prompt_data: Dados do prompt (system_prompt, user_prompt, etc.)

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        print(f"  Fazendo push: {prompt_name}")
        hub.push(prompt_name, prompt_template, new_repo_is_public=True)
        print(f"  ✓ Prompt publicado com sucesso!")
        print(f"  🔗 https://smith.langchain.com/hub/{prompt_name}")
        return True

    except Exception as e:
        print(f"  ❌ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    print(f"Username: {username}")
    print(f"Arquivo: {PROMPT_FILE}\n")

    yaml_data = load_yaml(PROMPT_FILE)
    if yaml_data is None:
        print(f"\n❌ Não foi possível carregar {PROMPT_FILE}")
        print("Certifique-se de que o arquivo existe e está bem formatado.")
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = yaml_data.get(prompt_key)

    if prompt_data is None:
        print(f"\n❌ Chave '{prompt_key}' não encontrada no YAML")
        print(f"Chaves disponíveis: {list(yaml_data.keys())}")
        return 1

    print("Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print(f"\n❌ Prompt inválido! Erros encontrados:")
        for error in errors:
            print(f"  - {error}")
        print(f"\nCorrija os erros em {PROMPT_FILE} e tente novamente.")
        return 1

    print("  ✓ Prompt válido!\n")

    prompt_name = f"{username}/{prompt_key}"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if success:
        print(f"\n✓ Push concluído com sucesso!")
        print(f"\nPróximos passos:")
        print(f"  1. Verifique no LangSmith: https://smith.langchain.com/hub/{prompt_name}")
        print(f"  2. Execute a avaliação: python src/evaluate.py")
        return 0
    else:
        print(f"\n❌ Falha no push")
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"
RAW_OUTPUT_PATH = "prompts/raw_prompts.yml"


def pull_prompts_from_langsmith() -> dict:
    """
    Faz pull do prompt do LangSmith Hub e converte para dicionário YAML-friendly.

    Returns:
        Dicionário com dados do prompt ou None se falhar
    """
    try:
        print(f"  Puxando prompt: {PROMPT_NAME}")
        prompt = hub.pull(PROMPT_NAME)
        print(f"  ✓ Prompt carregado com sucesso")

        system_content = ""
        user_content = "{bug_report}"

        for msg in prompt.messages:
            if msg.prompt.input_variables:
                template = msg.prompt.template
            else:
                template = msg.prompt.template

            if hasattr(msg, '__class__') and 'System' in msg.__class__.__name__:
                system_content = template
            elif hasattr(msg, '__class__') and 'Human' in msg.__class__.__name__:
                user_content = template

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_content,
                "user_prompt": user_content,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        return prompt_data

    except Exception as e:
        print(f"  ❌ Erro ao fazer pull do prompt: {e}")
        return None


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    print(f"Prompt a puxar: {PROMPT_NAME}")
    print(f"Destino: {OUTPUT_PATH}\n")

    prompt_data = pull_prompts_from_langsmith()

    if prompt_data is None:
        print("\n❌ Falha ao fazer pull do prompt")
        return 1

    if save_yaml(prompt_data, OUTPUT_PATH):
        print(f"\n✓ Prompt salvo em: {OUTPUT_PATH}")

        if save_yaml(prompt_data, RAW_OUTPUT_PATH):
            print(f"✓ Prompt salvo em: {RAW_OUTPUT_PATH}")
        else:
            print(f"⚠️ Erro ao salvar cópia em: {RAW_OUTPUT_PATH}")

        print(f"\nPróximo passo:")
        print(f"  1. Analise o prompt em {OUTPUT_PATH}")
        print(f"  2. Crie sua versão otimizada em prompts/bug_to_user_story_v2.yml")
        return 0
    else:
        print(f"\n❌ Erro ao salvar prompt em: {OUTPUT_PATH}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

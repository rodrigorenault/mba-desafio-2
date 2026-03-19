"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


@pytest.fixture
def prompt_data():
    """Carrega dados do prompt v2."""
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        assert prompt_data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data["system_prompt"].lower()
        role_indicators = [
            "você é",
            "you are",
            "atue como",
            "seu papel",
            "your role",
            "product manager",
        ]
        has_role = any(indicator in system_prompt for indicator in role_indicators)
        assert has_role, (
            "Prompt não define uma persona/papel. "
            "Use expressões como 'Você é um Product Manager...'"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"].lower()
        format_indicators = [
            "markdown",
            "user story",
            "como um",
            "eu quero",
            "para que",
            "critérios de aceitação",
            "given-when-then",
            "dado que",
        ]
        has_format = any(indicator in system_prompt for indicator in format_indicators)
        assert has_format, (
            "Prompt não menciona formato de saída esperado. "
            "Deve mencionar Markdown, User Story ou critérios de aceitação."
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"].lower()
        example_indicators = [
            "exemplo",
            "example",
            "bug report:",
            "bug simples",
            "bug médio",
            "bug complexo",
            "**bug report:**",
        ]
        has_examples = any(indicator in system_prompt for indicator in example_indicators)
        assert has_examples, (
            "Prompt não contém exemplos few-shot. "
            "Adicione pelo menos 2 exemplos de entrada/saída."
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        full_text = system_prompt + user_prompt

        assert "[TODO]" not in full_text, (
            "Prompt ainda contém '[TODO]'. "
            "Remova todos os placeholders antes de finalizar."
        )
        assert "[todo]" not in full_text.lower() or "[todo]" not in full_text, (
            "Prompt contém variações de TODO."
        )

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}. "
            f"Adicione o campo 'techniques_applied' com pelo menos 2 técnicas."
        )

    def test_prompt_structure_valid(self, prompt_data):
        """Valida a estrutura completa do prompt usando validate_prompt_structure."""
        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Prompt inválido: {'; '.join(errors)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

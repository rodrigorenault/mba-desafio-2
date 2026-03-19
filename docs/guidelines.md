# Development Guidelines

## Projeto: Desafio 2 — Pull, Otimização e Avaliação de Prompts

**Versão:** 1.0
**Data:** 2026-03-19

---

## 1. Linguagem e Estilo de Código

### 1.1 Python
- **Versão mínima:** Python 3.9+
- **Estilo:** PEP 8 com tipagem (type hints)
- **Docstrings:** Google style para todas as funções públicas
- **Encoding:** UTF-8 em todos os arquivos

### 1.2 Convenções de Nomenclatura

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Variáveis | snake_case | `prompt_data`, `f1_score` |
| Funções | snake_case | `pull_prompts_from_langsmith()` |
| Classes | PascalCase | `TestPrompts` |
| Constantes | UPPER_SNAKE_CASE | `MIN_SCORE_THRESHOLD` |
| Arquivos | snake_case | `pull_prompts.py` |

### 1.3 Imports
Ordenação:
1. Standard library
2. Third-party packages
3. Local modules

```python
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub

from utils import load_yaml, check_env_vars
```

---

## 2. Gestão de Configuração

### 2.1 Variáveis de Ambiente
- Todas as credenciais e configurações vão no `.env`
- **Nunca** commit do `.env` (está no `.gitignore`)
- Manter `.env.example` atualizado com todas as variáveis
- Usar `python-dotenv` para carregar no início de cada script
- Validar variáveis obrigatórias antes de prosseguir

### 2.2 Padrão de Validação
```python
required_vars = ["LANGSMITH_API_KEY", "LLM_PROVIDER"]
if not check_env_vars(required_vars):
    sys.exit(1)
```

---

## 3. Gestão de Prompts (YAML)

### 3.1 Estrutura Obrigatória

```yaml
prompt_name:
  description: "Descrição curta"
  system_prompt: |
    Conteúdo do system prompt...
  user_prompt: "{bug_report}"
  version: "v2"
  created_at: "YYYY-MM-DD"
  tags: ["tag1", "tag2"]
  techniques_applied: ["Técnica 1", "Técnica 2"]
```

### 3.2 Regras para o Prompt

- `system_prompt` **não pode** estar vazio
- `system_prompt` **não pode** conter `[TODO]`
- `techniques_applied` deve ter **mínimo 2 técnicas**
- `user_prompt` deve conter `{bug_report}` como placeholder
- Usar `|` para multiline strings no YAML
- Manter encoding UTF-8 para suporte a acentos

---

## 4. Regras de Código

### 4.1 Código Existente (Não Alterar)

Os seguintes arquivos **NÃO devem ser modificados**:
- `src/evaluate.py`
- `src/metrics.py`
- `src/utils.py`
- `datasets/bug_to_user_story.jsonl`

### 4.2 Código a Implementar

Os seguintes arquivos **devem ser implementados**:
- `src/pull_prompts.py` — Implementar stubs (`...`)
- `src/push_prompts.py` — Implementar stubs (`...`)
- `tests/test_prompts.py` — Implementar 6 testes obrigatórios
- `prompts/bug_to_user_story_v2.yml` — Criar prompt otimizado

### 4.3 Tratamento de Erros

- Usar try/except com mensagens amigáveis no CLI
- Exibir emoji de status: ✓ sucesso, ❌ erro, ⚠️ warning
- Retornar exit codes: 0 = sucesso, 1 = falha
- Logar erros com contexto suficiente para debugging

---

## 5. Testes

### 5.1 Framework
- **pytest** 8.3.4
- Executar com: `pytest tests/test_prompts.py -v`

### 5.2 Convenções
- Classes de teste: `TestPrompts`
- Métodos de teste: `test_<o_que_testa>`
- Usar fixtures para carregar dados compartilhados
- Assertions claras com mensagens descritivas

### 5.3 Testes Obrigatórios
Mínimo de 6 testes validando a estrutura do prompt v2 (ver FRD seção 6.2).

---

## 6. Git e Versionamento

### 6.1 Commits
- Formato: Conventional Commits
- Exemplos:
  - `feat: implement pull_prompts.py`
  - `feat: create optimized prompt v2`
  - `test: implement prompt validation tests`
  - `docs: update README with techniques and results`
  - `fix: adjust prompt tone for higher score`

### 6.2 Branch Strategy
- `main` — branch principal (entregável)
- Feature branches opcionais para iterações maiores

### 6.3 .gitignore
- `.env`, `venv/`, `__pycache__/`, `.pytest_cache/`
- Nunca commitar credenciais ou dados sensíveis

---

## 7. Documentação

### 7.1 README.md (Obrigatório)

Deve conter 3 seções principais:

**A) Técnicas Aplicadas:**
- Quais técnicas de Prompt Engineering foram usadas
- Justificativa para cada técnica
- Exemplos práticos

**B) Resultados Finais:**
- Link público do LangSmith
- Screenshots das avaliações
- Tabela comparativa v1 vs v2

**C) Como Executar:**
- Pré-requisitos
- Setup do ambiente virtual
- Comandos para cada fase

### 7.2 Documentação Técnica
- `/docs/` contém documentação do processo de desenvolvimento
- ADRs documentam decisões arquiteturais
- Manter docs atualizados a cada iteração significativa

---

## 8. Workflow de Iteração

1. Editar `prompts/bug_to_user_story_v2.yml`
2. Executar `pytest tests/test_prompts.py -v` (validação local)
3. Executar `python src/push_prompts.py` (push para Hub)
4. Executar `python src/evaluate.py` (avaliação)
5. Analisar reasoning das métricas com score < 0.9
6. Voltar ao passo 1 se necessário
7. Commit quando todas métricas >= 0.9

---

## 9. Segurança

- API keys **nunca** em código ou commits
- `.env` no `.gitignore`
- `.env.example` com valores vazios como template
- Validar inputs antes de enviar para APIs externas

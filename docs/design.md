# System Design

## Projeto: Desafio 2 — Pull, Otimização e Avaliação de Prompts

**Versão:** 1.0
**Data:** 2026-03-19

---

## 1. Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Application                          │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  ┌─────────┐ │
│  │ pull_prompts│  │push_prompts │  │ evaluate  │  │  tests  │ │
│  │     .py     │  │    .py      │  │    .py    │  │   .py   │ │
│  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  └────┬────┘ │
│         │                │               │              │      │
│  ┌──────┴────────────────┴───────────────┴──────────────┘      │
│  │                    utils.py                                  │
│  │  (load_yaml, save_yaml, get_llm, validate_prompt)           │
│  └──────────────────────┬───────────────────────────┘          │
│                         │                                       │
│  ┌──────────────────────┴───────────────────────────┐          │
│  │                   metrics.py                      │          │
│  │  (F1, Clarity, Precision, Tone, AC, Format, Comp) │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
   ┌──────────────┐  ┌──────────────┐  ┌─────────────┐
   │  LangSmith   │  │   LLM API    │  │  Local FS   │
   │  Prompt Hub  │  │ (OpenAI /    │  │  (YAML +    │
   │  (pull/push) │  │  Gemini)     │  │   JSONL)    │
   └──────────────┘  └──────────────┘  └─────────────┘
```

---

## 2. Componentes (C4 Level 3 — Component)

### 2.1 Context (C4 Level 1)

```
┌──────────────┐        ┌────────────────────────┐
│              │        │                        │
│   Developer  │───────▶│  Prompt Optimization   │
│   (Usuário)  │  CLI   │       System           │
│              │        │                        │
└──────────────┘        └────────┬───────────────┘
                                 │
                    ┌────────────┼────────────────┐
                    │            │                │
                    ▼            ▼                ▼
             ┌──────────┐ ┌──────────┐    ┌────────────┐
             │LangSmith │ │ LLM API  │    │   GitHub   │
             │  (Hub +  │ │(Gemini / │    │(Repositório│
             │ Tracing) │ │ OpenAI)  │    │  Público)  │
             └──────────┘ └──────────┘    └────────────┘
```

### 2.2 Container (C4 Level 2)

| Container | Tecnologia | Responsabilidade |
|-----------|-----------|------------------|
| CLI Scripts | Python 3.9+ | Ponto de entrada para cada operação |
| Utils Module | Python | Funções compartilhadas (YAML, LLM, validação) |
| Metrics Module | Python | 7 métricas de avaliação via LLM-as-Judge |
| Local Storage | YAML + JSONL | Prompts e datasets |
| LangSmith Hub | SaaS | Armazenamento e versionamento de prompts |
| LLM Provider | SaaS (API) | Geração de respostas e avaliação |

### 2.3 Componentes Detalhados

#### `src/pull_prompts.py`
- **Responsabilidade:** Pull do prompt v1 do LangSmith Hub
- **Dependências:** `langchain.hub`, `utils.save_yaml`
- **I/O:** Hub → `prompts/bug_to_user_story_v1.yml`

#### `src/push_prompts.py`
- **Responsabilidade:** Validar e push do prompt v2 para o Hub
- **Dependências:** `langchain.hub`, `utils.load_yaml`, `utils.check_env_vars`
- **I/O:** `prompts/bug_to_user_story_v2.yml` → Hub

#### `src/evaluate.py` (pré-existente)
- **Responsabilidade:** Orquestrar avaliação completa
- **Dependências:** `langchain.hub`, `langsmith.Client`, `metrics.*`, `utils.*`
- **I/O:** Hub prompt + JSONL dataset → Scores no terminal + LangSmith dashboard

#### `src/metrics.py` (pré-existente)
- **Responsabilidade:** 7 métricas via LLM-as-Judge
- **Dependências:** `utils.get_eval_llm`
- **I/O:** (question, answer, reference) → `{"score": float, "reasoning": str}`

#### `src/utils.py` (pré-existente)
- **Responsabilidade:** Funções auxiliares compartilhadas
- **Dependências:** `pyyaml`, `python-dotenv`, LLM providers
- **Funções-chave:** `load_yaml`, `save_yaml`, `get_llm`, `get_eval_llm`, `validate_prompt_structure`

#### `tests/test_prompts.py`
- **Responsabilidade:** Validação estrutural do prompt v2
- **Dependências:** `pytest`, `pyyaml`, `utils.validate_prompt_structure`
- **I/O:** `prompts/bug_to_user_story_v2.yml` → pass/fail

---

## 3. Fluxo de Dados

### 3.1 Pull Flow

```
LangSmith Hub                  Local
─────────────                  ─────
leonanluppi/bug_to_user_story_v1
        │
        │  hub.pull()
        ▼
  ChatPromptTemplate
        │
        │  serialize → YAML
        ▼
  prompts/bug_to_user_story_v1.yml
```

### 3.2 Push Flow

```
Local                           LangSmith Hub
─────                           ─────────────
prompts/bug_to_user_story_v2.yml
        │
        │  load_yaml()
        ▼
  YAML Dict
        │
        │  validate_prompt()
        ▼
  ChatPromptTemplate
        │
        │  hub.push()
        ▼
  {username}/bug_to_user_story_v2
```

### 3.3 Evaluation Flow

```
LangSmith Hub              LLM API              LangSmith
─────────────              ───────               ────────
{user}/bug_to_user_story_v2
        │
        │  hub.pull()
        ▼
  prompt_template
        │
        │  Para cada exemplo do dataset:
        │  ┌──────────────────────────┐
        │  │ 1. prompt | llm.invoke() │──── LLM Response ────┐
        │  │ 2. answer = response     │                       │
        │  │ 3. metrics.evaluate_*()  │── LLM Judge ──┐      │
        │  │ 4. score + reasoning     │◄──────────────┘      │
        │  └──────────────────────────┘                       │
        │                                                     │
        ▼                                                     ▼
  Scores Summary                              LangSmith Dashboard
  (terminal output)                           (tracing + metrics)
```

---

## 4. Modelo de Dados

### 4.1 Prompt YAML Schema

```yaml
# Root key: nome do prompt
prompt_name:
  description: string          # Descrição curta
  system_prompt: string        # Prompt de sistema (multiline)
  user_prompt: string          # Template com {bug_report}
  version: string              # "v1" ou "v2"
  created_at: string           # ISO date
  tags: list[string]           # Categorias
  techniques_applied: list[string]  # Técnicas usadas (v2 only)
```

### 4.2 Dataset JSONL Schema

```json
{
  "inputs": {
    "bug_report": "string - descrição do bug"
  },
  "outputs": {
    "reference": "string - user story esperada (ground truth)"
  },
  "metadata": {
    "domain": "string - e-commerce|saas|mobile|erp|crm",
    "type": "string - UI/UX|validation|integration|security|performance|business_logic",
    "complexity": "string - simple|medium|complex",
    "severity": "string? - critical (optional)"
  }
}
```

### 4.3 Metric Result Schema

```json
{
  "score": 0.95,
  "reasoning": "string - explicação do LLM judge",
  "precision": 0.9,
  "recall": 0.99
}
```

---

## 5. Integrações Externas

### 5.1 LangSmith

| Operação | API/SDK | Endpoint |
|----------|---------|----------|
| Pull prompt | `langchain.hub.pull()` | `https://api.smith.langchain.com` |
| Push prompt | `langchain.hub.push()` | `https://api.smith.langchain.com` |
| Create dataset | `langsmith.Client.create_dataset()` | `https://api.smith.langchain.com` |
| Create example | `langsmith.Client.create_example()` | `https://api.smith.langchain.com` |
| List examples | `langsmith.Client.list_examples()` | `https://api.smith.langchain.com` |
| Tracing | Automático via `LANGSMITH_TRACING=true` | `https://api.smith.langchain.com` |

### 5.2 LLM Providers

| Provider | SDK | Modelos |
|----------|-----|---------|
| Google Gemini | `langchain-google-genai` | `gemini-2.5-flash` (resposta + avaliação) |
| OpenAI | `langchain-openai` | `gpt-4o-mini` (resposta) + `gpt-4o` (avaliação) |

---

## 6. Decisões de Design

1. **CLI-first**: Scripts independentes executáveis via `python src/<script>.py`
2. **Stateless**: Cada script lê do disco/Hub, processa e salva — sem estado compartilhado em memória
3. **Configuration via Environment**: Todas as configurações no `.env`
4. **Separation of Concerns**: Cada arquivo tem uma responsabilidade clara
5. **Template Pattern**: Código base fornecido com stubs (`...`) para implementação

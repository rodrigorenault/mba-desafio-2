# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Exemplo no CLI

```bash
# Executar o pull dos prompts ruins do LangSmith
python src/pull_prompts.py

# Executar avaliação inicial (prompts ruins)
python src/evaluate.py

Executando avaliação dos prompts...
================================
Prompt: support_bot_v1a
- Helpfulness: 0.45
- Correctness: 0.52
- F1-Score: 0.48
- Clarity: 0.50
- Precision: 0.46
================================
Status: FALHOU - Métricas abaixo do mínimo de 0.9

# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação final (prompts otimizados)
python src/evaluate.py

Executando avaliação dos prompts...
================================
Prompt: support_bot_v2_optimized
- Helpfulness: 0.94
- Correctness: 0.96
- F1-Score: 0.93
- Clarity: 0.95
- Precision: 0.92
================================
Status: APROVADO ✓ - Todas as métricas atingiram o mínimo de 0.9
```

---

## Tecnologias obrigatórias

* **Linguagem:** Python 3.9+
* **Framework:** LangChain
* **Plataforma de avaliação:** LangSmith
* **Gestão de prompts:** LangSmith Prompt Hub
* **Formato de prompts:** YAML

---

## Pacotes recomendados

```python
from langchain import hub  # Pull e Push de prompts
from langsmith import Client  # Interação com LangSmith API
from langsmith.evaluation import evaluate  # Avaliação de prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

---

## OpenAI

* Crie uma **API Key** da OpenAI: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
* **Modelo de LLM para responder:** `gpt-4o-mini`
* **Modelo de LLM para avaliação:** `gpt-4o`
* **Custo estimado:** ~$1-5

## Gemini (modelo free)

* Crie uma **API Key** da Google: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
* **Modelo de LLM para responder:** `gemini-2.5-flash`
* **Modelo de LLM para avaliação:** `gemini-2.5-flash`
* **Limite:** 15 req/min, 1500 req/dia

---

## Requisitos

### 1. Pull dos Prompt inicial do LangSmith

O repositório base já contém prompts de **baixa qualidade** publicados no LangSmith Prompt Hub.

**Tarefas:**

1. Configurar credenciais no `.env`
2. Usar `src/pull_prompts.py` para:

   * Conectar ao LangSmith
   * Fazer pull do prompt:

     * `leonanluppi/bug_to_user_story_v1`
   * Salvar em `prompts/raw_prompts.yml`

---

### 2. Otimização do Prompt

**Tarefas:**

1. Analisar `prompts/bug_to_user_story_v1.yml`
2. Criar `prompts/bug_to_user_story_v2.yml`
3. Aplicar **pelo menos duas técnicas**:

* Few-shot Learning
* Chain of Thought (CoT)
* Tree of Thought
* Skeleton of Thought
* ReAct
* Role Prompting

4. Documentar no `README.md`

**Requisitos do prompt otimizado:**

* Instruções claras
* Regras explícitas
* Exemplos (few-shot)
* Edge cases
* Separação System vs User

---

### 3. Push e Avaliação

**Tarefas:**

1. Criar `src/push_prompts.py`:

   * Ler prompts otimizados
   * Fazer push:

     ```
     {seu_username}/bug_to_user_story_v2
     ```
   * Adicionar metadados

2. Validar no LangSmith

3. Tornar público

---

### 4. Iteração

* Fazer 3–5 iterações
* Ajustar prompts com base nas métricas
* Repetir até:

```
TODAS as métricas >= 0.9
```

**Critério de Aprovação:**

```
- Tone Score >= 0.9
- Acceptance Criteria Score >= 0.9
- User Story Format Score >= 0.9
- Completeness Score >= 0.9

MÉDIA >= 0.9
```

⚠️ Todas as métricas devem atingir 0.9

---

### 5. Testes de Validação

Implementar em `tests/test_prompts.py`:

* `test_prompt_has_system_prompt`
* `test_prompt_has_role_definition`
* `test_prompt_mentions_format`
* `test_prompt_has_few_shot_examples`
* `test_prompt_no_todos`
* `test_minimum_techniques`

```bash
pytest tests/test_prompts.py
```

---

## Estrutura obrigatória do projeto

```bash
desafio-prompt-engineer/
├── .env.example
├── requirements.txt
├── README.md
│
├── prompts/
│   ├── bug_to_user_story_v1.yml
│   └── bug_to_user_story_v2.yml
│
├── src/
│   ├── pull_prompts.py
│   ├── push_prompts.py
│   ├── evaluate.py
│   ├── metrics.py
│   ├── dataset.py
│   └── utils.py
│
├── tests/
│   └── test_prompts.py
```

---

## O que você vai criar

* `prompts/bug_to_user_story_v2.yml`
* `tests/test_prompts.py`
* Scripts de pull/push
* `README.md`

---

## O que já vem pronto

* Dataset com 15 bugs
* 4 métricas
* Suporte OpenAI + Gemini

---

## Repositórios úteis

* [https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)
* [https://docs.smith.langchain.com/](https://docs.smith.langchain.com/)
* [https://www.promptingguide.ai/](https://www.promptingguide.ai/)

---

## VirtualEnv para Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Ordem de execução

### 1. Pull

```bash
python src/pull_prompts.py
```

### 2. Refatorar

Editar:

```
prompts/bug_to_user_story_v2.yml
```

### 3. Push

```bash
python src/push_prompts.py
```

### 4. Avaliação

```bash
python src/evaluate.py
```

---

## Entregável

### 1. Repositório público

* Código completo
* Prompt otimizado
* README atualizado

---

### 2. README deve conter

#### A) Técnicas Aplicadas

* Técnicas usadas
* Justificativa
* Exemplos

#### B) Resultados Finais

* Link LangSmith
* Screenshots
* Comparação v1 vs v2

#### C) Como Executar

* Instruções completas
* Dependências
* Comandos

---

### 3. Evidências no LangSmith

* Dataset ≥ 20 exemplos
* Execuções v1 e v2
* Métricas ≥ 0.9
* Tracing detalhado

---

## Dicas Finais

* Seja específico e use contexto/persona
* Use few-shot (2–3 exemplos)
* Use Chain of Thought para tarefas complexas
* Use tracing do LangSmith para debug
* Não altere datasets
* Itere várias vezes
* Documente todo o processo

---

# Functional Requirements Document (FRD)

## Projeto: Desafio 2 — Pull, Otimização e Avaliação de Prompts

**Versão:** 1.0
**Data:** 2026-03-19

---

## 1. Visão Geral dos Módulos

O sistema é composto por 4 módulos funcionais executados sequencialmente via CLI:

```
[Pull] → [Otimização Manual] → [Push] → [Avaliação]
   ↑                                         |
   └──────── Iteração (3-5x) ←──────────────┘
```

---

## 2. Módulo 1 — Pull de Prompts (`src/pull_prompts.py`)

### 2.1 Descrição
Conecta ao LangSmith Prompt Hub e baixa o prompt baseline (v1) de baixa qualidade para o ambiente local.

### 2.2 Fluxo Funcional

1. Carregar variáveis de ambiente do `.env`
2. Validar que `LANGSMITH_API_KEY` está configurada
3. Conectar ao LangSmith Hub via `langchain.hub.pull()`
4. Fazer pull do prompt `leonanluppi/bug_to_user_story_v1`
5. Serializar o prompt para formato YAML
6. Salvar em `prompts/bug_to_user_story_v1.yml`
7. Exibir confirmação no terminal

### 2.3 Entrada e Saída

| Item | Valor |
|------|-------|
| **Entrada** | Nome do prompt no Hub: `leonanluppi/bug_to_user_story_v1` |
| **Saída** | Arquivo `prompts/bug_to_user_story_v1.yml` |
| **Dependências** | `LANGSMITH_API_KEY` no `.env` |

### 2.4 Tratamento de Erros

- Prompt não encontrado no Hub → mensagem explicativa com ações necessárias
- API key inválida → mensagem indicando verificação do `.env`
- Erro de rede → retry com mensagem amigável

### 2.5 Execução

```bash
python src/pull_prompts.py
```

---

## 3. Módulo 2 — Otimização do Prompt (`prompts/bug_to_user_story_v2.yml`)

### 3.1 Descrição
Criação manual (com apoio de IA) do prompt otimizado, aplicando técnicas avançadas de Prompt Engineering.

### 3.2 Requisitos Estruturais do YAML

O arquivo `prompts/bug_to_user_story_v2.yml` deve conter:

```yaml
bug_to_user_story_v2:
  description: "..."           # Descrição do prompt
  system_prompt: |             # Prompt de sistema (obrigatório, não-vazio)
    ...
  user_prompt: "..."           # Template do prompt do usuário
  version: "v2"               # Versão
  created_at: "..."           # Data de criação
  tags: [...]                 # Tags relevantes
  techniques_applied: [...]   # Mínimo 2 técnicas (obrigatório)
```

### 3.3 Técnicas Obrigatórias (mínimo 2)

| Técnica | Descrição | Aplicação |
|---------|-----------|-----------|
| **Role Prompting** | Definir persona detalhada | "Você é um Product Manager sênior com 10+ anos de experiência..." |
| **Few-shot Learning** | Fornecer 2-3 exemplos entrada/saída | Exemplos de bug simples, médio e complexo com user stories esperadas |
| **Chain of Thought (CoT)** | Instrução de raciocínio passo a passo | "Pense passo a passo: 1) Analise o bug... 2) Identifique o usuário..." |
| **Tree of Thought** | Explorar múltiplos caminhos de raciocínio | Considerar múltiplas personas e cenários |
| **Skeleton of Thought** | Estruturar resposta em etapas claras | Template obrigatório da user story |
| **ReAct** | Raciocínio + Ação | Analisar → Categorizar → Gerar |

### 3.4 Requisitos do Conteúdo

O `system_prompt` do v2 **deve** conter:

1. **Definição de Persona** — papel, experiência, responsabilidades
2. **Instruções Claras** — o que fazer com o bug report
3. **Regras Explícitas** — formato, tom, estrutura obrigatória
4. **Exemplos (Few-shot)** — pelo menos 2 exemplos de entrada/saída
5. **Tratamento de Edge Cases** — bugs simples vs complexos, multi-issue
6. **Formato de Saída** — template obrigatório da user story
7. **Nenhum `[TODO]`** — prompt deve estar 100% completo

### 3.5 Formato Esperado da User Story Gerada

```markdown
Como um [tipo de usuário específico],
eu quero [ação/funcionalidade desejada],
para que [benefício/valor de negócio].

## Critérios de Aceitação
- Dado que [pré-condição]
- Quando [ação]
- Então [resultado esperado]
- E [resultado adicional]

## Contexto Técnico (quando aplicável)
- [Detalhes técnicos relevantes]

## Tasks Técnicas (para bugs complexos)
1. [Task 1]
2. [Task 2]
```

---

## 4. Módulo 3 — Push de Prompts (`src/push_prompts.py`)

### 4.1 Descrição
Lê o prompt otimizado do YAML local, valida sua estrutura e faz push público para o LangSmith Prompt Hub.

### 4.2 Fluxo Funcional

1. Carregar variáveis de ambiente
2. Validar `LANGSMITH_API_KEY` e `USERNAME_LANGSMITH_HUB`
3. Ler `prompts/bug_to_user_story_v2.yml`
4. Validar estrutura do prompt:
   - `system_prompt` não vazio
   - Sem `[TODO]` no texto
   - `techniques_applied` com >= 2 técnicas
5. Converter YAML → `ChatPromptTemplate` (system + user messages)
6. Fazer push via `langchain.hub.push()` com nome `{username}/bug_to_user_story_v2`
7. Configurar como público
8. Exibir URL do prompt publicado

### 4.3 Entrada e Saída

| Item | Valor |
|------|-------|
| **Entrada** | `prompts/bug_to_user_story_v2.yml` |
| **Saída** | Prompt publicado em `{username}/bug_to_user_story_v2` no LangSmith Hub |
| **Dependências** | `LANGSMITH_API_KEY`, `USERNAME_LANGSMITH_HUB` no `.env` |

### 4.4 Validação Pre-Push

| Validação | Critério | Ação se falhar |
|-----------|----------|----------------|
| system_prompt não vazio | `len(system_prompt.strip()) > 0` | Abort com mensagem |
| Sem TODOs | `"TODO" not in system_prompt` | Abort com lista de TODOs |
| Mínimo 2 técnicas | `len(techniques_applied) >= 2` | Abort com contagem |
| Versão definida | `version` presente | Warning |

### 4.5 Execução

```bash
python src/push_prompts.py
```

---

## 5. Módulo 4 — Avaliação (`src/evaluate.py`)

### 5.1 Descrição
Avalia o prompt otimizado contra o dataset de bugs usando LLM-as-Judge com 4 métricas específicas para Bug-to-User-Story.

### 5.2 Fluxo Funcional

1. Carregar configuração (provider, modelos)
2. Validar variáveis de ambiente
3. Carregar dataset de `datasets/bug_to_user_story.jsonl` (15 exemplos)
4. Criar/atualizar dataset no LangSmith
5. Fazer pull do prompt `{username}/bug_to_user_story_v2` do Hub
6. Para cada exemplo do dataset (top 10):
   a. Invocar prompt com o bug_report
   b. Obter resposta do LLM (user story gerada)
   c. Calcular F1-Score, Clarity, Precision (métricas gerais)
7. Calcular médias e derivar Helpfulness e Correctness
8. Exibir resultados com indicadores de aprovação/reprovação

### 5.3 Métricas Gerais (calculadas em `evaluate.py`)

| Métrica | Cálculo | Descrição |
|---------|---------|-----------|
| **F1-Score** | `2 × (P × R) / (P + R)` via LLM-as-Judge | Precisão e recall da resposta |
| **Clarity** | Média de 4 subcritérios via LLM-as-Judge | Organização, linguagem, clareza, concisão |
| **Precision** | Média de 3 subcritérios via LLM-as-Judge | Ausência de alucinações, foco, correção factual |
| **Helpfulness** | `(Clarity + Precision) / 2` | Derivada |
| **Correctness** | `(F1 + Precision) / 2` | Derivada |

### 5.4 Métricas Específicas Bug-to-User-Story (em `metrics.py`)

| Métrica | Subcritérios | Descrição |
|---------|-------------|-----------|
| **Tone Score** | Profissionalismo, Empatia, Foco em Valor, Linguagem Positiva | Tom da user story |
| **Acceptance Criteria Score** | Formato Estruturado, Testabilidade, Quantidade, Cobertura | Qualidade dos critérios de aceitação |
| **User Story Format Score** | Template Padrão, Persona, Ação, Benefício, Separação de Seções | Formato correto |
| **Completeness Score** | Cobertura do Problema, Contexto Técnico, Impacto, Tasks, Informações Adicionais | Completude |

### 5.5 Critério de Aprovação

```
Tone Score             >= 0.9
Acceptance Criteria    >= 0.9
User Story Format      >= 0.9
Completeness Score     >= 0.9
────────────────────────────
MÉDIA das 4 métricas   >= 0.9
```

### 5.6 Execução

```bash
python src/evaluate.py
```

---

## 6. Módulo 5 — Testes (`tests/test_prompts.py`)

### 6.1 Descrição
Testes automatizados com pytest para validar estrutura e qualidade do prompt otimizado v2.

### 6.2 Testes Obrigatórios

| Teste | Descrição | Critério de Sucesso |
|-------|-----------|---------------------|
| `test_prompt_has_system_prompt` | Campo `system_prompt` existe e não está vazio | `len(data['system_prompt'].strip()) > 0` |
| `test_prompt_has_role_definition` | Prompt define uma persona | Contém "Você é", "You are", "Atue como" ou similar |
| `test_prompt_mentions_format` | Prompt exige formato Markdown ou User Story | Contém "Markdown", "User Story", "Como um" ou similar |
| `test_prompt_has_few_shot_examples` | Prompt contém exemplos de entrada/saída | Contém "Exemplo", "Example", "Bug Report:" + resposta |
| `test_prompt_no_todos` | Não há `[TODO]` esquecidos | `"[TODO]" not in system_prompt` |
| `test_minimum_techniques` | Pelo menos 2 técnicas listadas em metadados | `len(techniques_applied) >= 2` |

### 6.3 Execução

```bash
pytest tests/test_prompts.py -v
```

---

## 7. Fluxo de Iteração

```
┌─────────────────────────────────────────────┐
│ 1. Analisar resultados da avaliação         │
│ 2. Identificar métricas com score < 0.9     │
│ 3. Ler reasoning das métricas baixas        │
│ 4. Ajustar prompt v2 no YAML               │
│ 5. Push: python src/push_prompts.py         │
│ 6. Avaliar: python src/evaluate.py          │
│ 7. Se TODAS >= 0.9 → FIM ✓                 │
│ 8. Senão → voltar ao passo 1               │
└─────────────────────────────────────────────┘
Repetir 3-5 vezes até convergência
```

---

## 8. Configuração de Ambiente

### 8.1 Variáveis de Ambiente (`.env`)

| Variável | Obrigatória | Descrição |
|----------|------------|-----------|
| `LANGSMITH_TRACING` | Sim | Habilitar tracing (`true`) |
| `LANGSMITH_ENDPOINT` | Sim | `https://api.smith.langchain.com` |
| `LANGSMITH_API_KEY` | Sim | API key do LangSmith |
| `LANGSMITH_PROJECT` | Sim | Nome do projeto no LangSmith |
| `USERNAME_LANGSMITH_HUB` | Sim | Username para push de prompts |
| `LLM_PROVIDER` | Sim | `openai` ou `google` |
| `LLM_MODEL` | Sim | Modelo para respostas (`gpt-4o-mini` ou `gemini-2.5-flash`) |
| `EVAL_MODEL` | Sim | Modelo para avaliação (`gpt-4o` ou `gemini-2.5-flash`) |
| `OPENAI_API_KEY` | Cond. | Obrigatória se `LLM_PROVIDER=openai` |
| `GOOGLE_API_KEY` | Cond. | Obrigatória se `LLM_PROVIDER=google` |

---

## 9. Dependências do Projeto

```
langchain==0.3.13
langchain-core==0.3.28
langchain-community==0.3.13
langsmith==0.2.7
langchain-openai==0.2.14
langchain-google-genai==2.0.8
python-dotenv==1.0.1
pyyaml==6.0.2
pydantic==2.10.4
pytest==8.3.4
```

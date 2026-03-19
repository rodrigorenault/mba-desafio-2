# Architectural Decision Records (ADR)

## Projeto: Desafio 2 — Pull, Otimização e Avaliação de Prompts

**Versão:** 1.0
**Data:** 2026-03-19

---

## ADR-001: Escolha do LLM Provider

**Status:** Active
**Data:** 2026-03-19

### Contexto

O projeto precisa de um LLM para duas funções distintas:
1. **Modelo de resposta** — gerar user stories a partir de bug reports
2. **Modelo de avaliação (judge)** — avaliar a qualidade das user stories geradas

São oferecidas duas opções: OpenAI (pago) e Google Gemini (free tier).

### Decisão

Utilizar **Google Gemini** (`gemini-2.5-flash`) como provider padrão para ambos os modelos (resposta e avaliação).

### Justificativa

| Critério | OpenAI | Google Gemini |
|----------|--------|---------------|
| Custo | ~$1-5 estimados | Gratuito |
| Rate Limit | Alto | 15 req/min, 1500 req/dia |
| Qualidade | Alta (gpt-4o para eval) | Boa (gemini-2.5-flash) |
| Configuração | API key paga necessária | API key gratuita |

- O free tier do Gemini é suficiente para o volume do projeto (15 exemplos × 3 métricas × 5 iterações = ~225 requests)
- Custo zero elimina barreira de entrada
- Se necessário, a arquitetura permite fallback para OpenAI mudando apenas o `.env`

### Consequências

- (+) Sem custo para desenvolvimento e iterações
- (+) Arquitetura multi-provider permite troca fácil
- (-) Rate limit de 15 req/min requer atenção em avaliações com muitos exemplos
- (-) Qualidade pode ser marginalmente inferior ao gpt-4o como judge

---

## ADR-002: Formato YAML para Prompts

**Status:** Active
**Data:** 2026-03-19

### Contexto

O prompt otimizado precisa ser armazenado localmente em formato legível e versionável, antes de ser pushado para o LangSmith Hub.

### Decisão

Utilizar **YAML** como formato de armazenamento local dos prompts.

### Justificativa

- YAML é human-readable e fácil de editar manualmente
- Suporta multiline strings nativamente (ideal para system prompts longos)
- Formato exigido pelo enunciado do desafio
- Integração nativa com PyYAML para leitura/escrita
- Facilita versionamento com git (diffs legíveis)

### Consequências

- (+) Fácil de editar e revisar
- (+) Diffs legíveis em pull requests
- (-) YAML é sensível a indentação (potencial fonte de erros)
- (-) Strings com caracteres especiais ({, }, :) precisam de escape

---

## ADR-003: LLM-as-Judge para Avaliação

**Status:** Active
**Data:** 2026-03-19

### Contexto

Avaliar a qualidade de prompts/respostas de LLM requer métricas que vão além de simples comparação textual. Métricas como "tom profissional", "clareza" e "completude" são subjetivas.

### Decisão

Utilizar a abordagem **LLM-as-Judge**, onde um LLM avalia as respostas de outro LLM com base em critérios estruturados.

### Justificativa

- Permite avaliação de aspectos qualitativos (tom, clareza, completude)
- Escalável para grandes datasets
- Cada métrica tem critérios explícitos e subcritérios ponderados
- Retorna score numérico (0.0-1.0) + reasoning (explicação textual)
- Abordagem padrão na indústria para avaliação de LLMs (LangSmith, Ragas, etc.)

### Estrutura das Métricas

```
7 métricas total:
├── Gerais (3):
│   ├── F1-Score (Precision × Recall)
│   ├── Clarity (4 subcritérios)
│   └── Precision (3 subcritérios)
└── Bug-to-User-Story (4):
    ├── Tone Score (4 subcritérios)
    ├── Acceptance Criteria Score (4 subcritérios)
    ├── User Story Format Score (5 subcritérios)
    └── Completeness Score (5 subcritérios)
```

### Consequências

- (+) Avaliação rica e multidimensional
- (+) Reasoning permite debug de scores baixos
- (-) Resultados podem variar entre execuções (não-determinístico)
- (-) Custo computacional proporcional a (exemplos × métricas)
- (-) Dependência de um LLM judge de alta qualidade

---

## ADR-004: Estratégia de Otimização do Prompt — Técnicas Selecionadas

**Status:** Active
**Data:** 2026-03-19

### Contexto

O prompt v1 é genérico e produz scores < 0.5. Precisamos aplicar pelo menos 2 técnicas avançadas para atingir >= 0.9 em todas as métricas.

### Decisão

Aplicar as seguintes técnicas (mínimo 3 para maior robustez):

1. **Role Prompting** — Definir persona de Product Manager sênior
2. **Few-shot Learning** — 2-3 exemplos cobrindo bugs simples, médio e complexo
3. **Chain of Thought (CoT)** — Instrução passo-a-passo para análise do bug

### Justificativa

| Técnica | Impacto Esperado | Métricas Beneficiadas |
|---------|-----------------|----------------------|
| Role Prompting | Tom profissional e empático | Tone Score, User Story Format |
| Few-shot | Formato consistente e completo | Todas as métricas |
| CoT | Análise mais profunda de bugs complexos | Completeness, Acceptance Criteria |

- **Role Prompting** é a base: define o contexto, expertise e estilo do "assistente"
- **Few-shot** é o técnica de maior impacto: exemplos concretos guiam o formato exato
- **CoT** complementa para bugs complexos: garante análise de impacto, tasks técnicas, etc.

### Consequências

- (+) Combinação de 3 técnicas maximiza cobertura das métricas
- (+) Few-shot com exemplos de diferentes complexidades cobre edge cases
- (-) Prompt v2 será significativamente maior que v1 (mais tokens, mais custo)
- (-) Exemplos few-shot precisam ser cuidadosamente alinhados com o ground truth

---

## ADR-005: Estrutura do Projeto Baseada no Template

**Status:** Active
**Data:** 2026-03-19

### Contexto

O desafio fornece um repositório template com estrutura obrigatória e código base (evaluate.py, metrics.py, utils.py, dataset).

### Decisão

Manter a estrutura exata do template, implementando os stubs fornecidos sem alterar os módulos pré-existentes.

### Justificativa

- Estrutura é requisito obrigatório do desafio
- Código de avaliação e métricas já está completo e testado
- Alterar o código base pode causar incompatibilidades na avaliação
- Foco deve ser na otimização do prompt, não na refatoração do código

### Estrutura Mantida

```
desafio-2/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── datasets/
│   └── bug_to_user_story.jsonl    # NÃO ALTERAR
├── prompts/
│   ├── bug_to_user_story_v1.yml   # Pull do Hub
│   └── bug_to_user_story_v2.yml   # CRIAR (principal entregável)
├── src/
│   ├── __init__.py
│   ├── pull_prompts.py            # IMPLEMENTAR
│   ├── push_prompts.py            # IMPLEMENTAR
│   ├── evaluate.py                # NÃO ALTERAR
│   ├── metrics.py                 # NÃO ALTERAR
│   └── utils.py                   # NÃO ALTERAR
├── tests/
│   ├── __init__.py
│   └── test_prompts.py            # IMPLEMENTAR
└── docs/                          # Documentação do projeto
```

### Consequências

- (+) Avaliação consistente com o esperado pelo desafio
- (+) Menos risco de bugs por alteração de código funcional
- (-) Limitado pelas decisões de design do template (ex: métricas fixas)

---

## ADR-006: Separação System Prompt vs User Prompt

**Status:** Active
**Data:** 2026-03-19

### Contexto

O LangChain suporta `ChatPromptTemplate` com mensagens `system` e `human` separadas. O prompt v1 mistura instruções e variáveis no system prompt.

### Decisão

No v2, separar claramente:
- **System Prompt:** Persona, regras, formato, exemplos (estável entre invocações)
- **User Prompt:** Apenas a variável `{bug_report}` (varia por execução)

### Justificativa

- System prompt define o comportamento fixo do assistente
- User prompt contém apenas o input variável
- Separação permite que o LLM trate o system como "instruções imutáveis"
- Melhor aderência ao padrão do LangChain `ChatPromptTemplate`
- Facilita manutenção e debugging

### Consequências

- (+) Comportamento mais consistente do LLM
- (+) Facilita debugging (system fixo, user variável)
- (+) Padrão da indústria para prompt engineering
- (-) System prompt pode ficar muito longo com todos os exemplos few-shot

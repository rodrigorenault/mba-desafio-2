# Product Requirements Document (PRD)

## Projeto: Desafio 2 — Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

**Versão:** 1.0
**Data:** 2026-03-19
**Autor:** Rodrigo Renault
**Programa:** MBA de Engenharia de Software com IA — Full Cycle

---

## 1. Visão Geral do Produto

Este projeto é uma ferramenta CLI em Python para o ciclo completo de gestão e otimização de prompts de IA utilizando o ecossistema LangChain/LangSmith. O software automatiza o processo de pull, otimização, push e avaliação de prompts, permitindo medir quantitativamente a qualidade de prompts aplicados ao domínio de conversão de Bug Reports em User Stories.

---

## 2. Problema

Prompts mal-estruturados para LLMs geram respostas inconsistentes, vagas, com informações faltantes ou formatação inadequada. No contexto de Product Management, converter bug reports em user stories exige:

- Tom profissional e empático
- Formato padrão de user story ("Como um..., eu quero..., para que...")
- Critérios de aceitação estruturados (Given-When-Then)
- Completude proporcional à complexidade do bug
- Contexto técnico quando relevante

O prompt v1 (baseline) é genérico, sem exemplos, sem definição de persona, sem regras explícitas — produzindo user stories que falham consistentemente nas métricas de qualidade (scores < 0.5).

---

## 3. Objetivos

| # | Objetivo | Métrica de Sucesso |
|---|----------|--------------------|
| 1 | Fazer pull do prompt v1 do LangSmith Hub | Arquivo `prompts/bug_to_user_story_v1.yml` salvo localmente |
| 2 | Otimizar o prompt aplicando >= 2 técnicas avançadas | Prompt v2 com Role Prompting, Few-shot, CoT documentados |
| 3 | Fazer push do prompt v2 para LangSmith Hub | Prompt público em `{username}/bug_to_user_story_v2` |
| 4 | Avaliar qualidade com 4 métricas específicas | Todas >= 0.9 |
| 5 | Iterar 3-5 vezes até aprovação | Convergência dentro de 5 iterações |

---

## 4. Público-Alvo

- **Primário:** Avaliadores do MBA (professores e mentores Full Cycle)
- **Secundário:** Desenvolvedores e PMs que queiram automatizar conversão de bugs em user stories
- **Usuário técnico:** Quem executa os scripts CLI

---

## 5. Escopo

### 5.1 Dentro do Escopo

- Scripts Python CLI para pull, push e avaliação
- Otimização manual do prompt v2 em YAML
- Testes automatizados com pytest (6 testes mínimos)
- Documentação completa no README.md
- Suporte a OpenAI e Google Gemini como LLM providers
- Integração com LangSmith para tracing e avaliação

### 5.2 Fora do Escopo

- Interface gráfica (web ou desktop)
- API REST
- Alteração do dataset de avaliação
- Alteração dos scripts de métricas (`metrics.py`, `evaluate.py`)
- Deploy em produção

---

## 6. Requisitos Funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-01 | Pull do prompt `leonanluppi/bug_to_user_story_v1` do LangSmith Hub | Alta |
| RF-02 | Salvar prompt em `prompts/bug_to_user_story_v1.yml` (formato YAML) | Alta |
| RF-03 | Criar prompt otimizado `prompts/bug_to_user_story_v2.yml` com >= 2 técnicas | Alta |
| RF-04 | Push do prompt v2 para `{username}/bug_to_user_story_v2` no LangSmith Hub | Alta |
| RF-05 | Prompt v2 deve ser público no LangSmith | Alta |
| RF-06 | Avaliação automática contra dataset de 15 bugs | Alta |
| RF-07 | Exibir resultados no terminal com indicadores visuais | Média |
| RF-08 | Testes pytest para validar estrutura do prompt | Alta |
| RF-09 | README com técnicas aplicadas, resultados e instruções | Alta |

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Critério |
|----|-----------|----------|
| RNF-01 | Python 3.9+ | Compatibilidade |
| RNF-02 | Tempo de avaliação < 10 min (10 exemplos) | Performance |
| RNF-03 | Suporte multi-provider (OpenAI + Gemini) | Portabilidade |
| RNF-04 | Credenciais via `.env` (nunca hardcoded) | Segurança |
| RNF-05 | Código limpo e documentado | Manutenibilidade |

---

## 8. Métricas de Avaliação (Critério de Aprovação)

Todas as 4 métricas específicas devem atingir >= 0.9:

| Métrica | Descrição | Mínimo |
|---------|-----------|--------|
| **Tone Score** | Tom profissional e empático | >= 0.9 |
| **Acceptance Criteria Score** | Qualidade dos critérios de aceitação (Given-When-Then) | >= 0.9 |
| **User Story Format Score** | Formato padrão "Como um..., eu quero..., para que..." | >= 0.9 |
| **Completeness Score** | Completude proporcional à complexidade do bug | >= 0.9 |
| **Média Geral** | Média das 4 métricas | >= 0.9 |

---

## 9. Dataset

- **Formato:** JSONL (`datasets/bug_to_user_story.jsonl`)
- **Total:** 15 exemplos
  - 5 bugs simples (UI/UX, validação)
  - 7 bugs médios (integração, segurança, performance, business logic)
  - 3 bugs complexos (multi-issue, críticos, com impacto financeiro)
- **Estrutura:** `inputs.bug_report` (texto do bug) → `outputs.reference` (user story esperada)
- **Restrição:** O dataset NÃO deve ser alterado

---

## 10. Entregáveis

1. Repositório público no GitHub com todo o código
2. Prompt otimizado v2 (`prompts/bug_to_user_story_v2.yml`)
3. README.md com: Técnicas Aplicadas, Resultados Finais, Como Executar
4. Evidências no LangSmith (dataset >= 20 exemplos, tracing, métricas >= 0.9)
5. Screenshots das avaliações

---

## 11. Cronograma

| Fase | Atividade | Estimativa |
|------|-----------|------------|
| 1 | Setup do projeto e pull do prompt v1 | 1h |
| 2 | Análise do v1 e criação do v2 (otimização) | 3-4h |
| 3 | Push e primeira avaliação | 30min |
| 4 | Iterações de refinamento (3-5x) | 2-3h |
| 5 | Testes e documentação | 1-2h |
| **Total** | | **~8-10h** |

---

## 12. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Métricas não atingem 0.9 após 5 iterações | Média | Alto | Analisar reasoning das métricas, ajustar técnicas |
| Rate limit do Gemini (15 req/min) | Alta | Médio | Usar batches menores ou fallback para OpenAI |
| Custo OpenAI excede $5 | Baixa | Baixo | Preferir Gemini (free), limitar iterações |
| API LangSmith indisponível | Baixa | Alto | Retry com backoff, salvar resultados locais |

---

## 13. Referências

- [Repositório Template](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangSmith Prompt Hub](https://smith.langchain.com/prompts)

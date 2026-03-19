# Infrastructure & CI/CD

## Projeto: Desafio 2 — Pull, Otimização e Avaliação de Prompts

**Versão:** 1.0
**Data:** 2026-03-19

---

## 1. Visão Geral

Este projeto é uma aplicação CLI local — não requer deploy em servidores, containers ou cloud. A infraestrutura se resume ao ambiente de desenvolvimento local e aos serviços SaaS utilizados.

---

## 2. Ambiente de Desenvolvimento

### 2.1 Requisitos do Sistema

| Componente | Versão | Notas |
|-----------|--------|-------|
| Python | 3.9+ | Necessário para type hints e features modernas |
| pip | 21+ | Gerenciador de pacotes |
| venv | built-in | Ambiente virtual Python |
| Git | 2.x+ | Controle de versão |
| Sistema Operacional | Linux/macOS/Windows | Cross-platform |

### 2.2 Setup do Ambiente

```bash
# 1. Clonar o repositório
git clone https://github.com/rodrigorenault/mba-desafio-2.git
cd mba-desafio-2

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 5. Verificar instalação
python -c "import langchain; print(langchain.__version__)"
```

---

## 3. Serviços Externos (SaaS)

### 3.1 LangSmith

| Aspecto | Detalhe |
|---------|---------|
| **URL** | https://smith.langchain.com |
| **Função** | Prompt Hub (armazenamento), Tracing (debug), Evaluation (dashboard) |
| **Autenticação** | API Key via `LANGSMITH_API_KEY` |
| **Custo** | Free tier suficiente para o projeto |
| **Dados armazenados** | Prompts, traces de execução, datasets, resultados de avaliação |

### 3.2 Google AI Studio (Gemini)

| Aspecto | Detalhe |
|---------|---------|
| **URL** | https://aistudio.google.com |
| **Função** | LLM para geração de respostas e avaliação (judge) |
| **Autenticação** | API Key via `GOOGLE_API_KEY` |
| **Custo** | Gratuito (free tier) |
| **Limites** | 15 req/min, 1500 req/dia |
| **Modelo** | `gemini-2.5-flash` |

### 3.3 OpenAI (alternativa)

| Aspecto | Detalhe |
|---------|---------|
| **URL** | https://platform.openai.com |
| **Função** | LLM alternativo (pago) |
| **Autenticação** | API Key via `OPENAI_API_KEY` |
| **Custo** | ~$1-5 estimado |
| **Modelos** | `gpt-4o-mini` (resposta), `gpt-4o` (avaliação) |

---

## 4. Gestão de Dependências

### 4.1 requirements.txt

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

### 4.2 Política de Versões
- Todas as dependências estão com versões fixas (pinned)
- Não usar ranges (`>=`, `~=`) para reprodutibilidade
- Atualizar manualmente quando necessário

---

## 5. Gestão de Secrets

### 5.1 Fluxo de Credenciais

```
.env.example (template, commitado)
      │
      │  cp .env.example .env
      ▼
.env (preenchido, NÃO commitado)
      │
      │  python-dotenv: load_dotenv()
      ▼
os.getenv("VARIABLE")
```

### 5.2 Variáveis Sensíveis

| Variável | Tipo | Fonte |
|----------|------|-------|
| `LANGSMITH_API_KEY` | API Key | https://smith.langchain.com/settings |
| `GOOGLE_API_KEY` | API Key | https://aistudio.google.com/app/apikey |
| `OPENAI_API_KEY` | API Key | https://platform.openai.com/api-keys |

### 5.3 Segurança
- `.env` está no `.gitignore`
- **Nunca** commitar credenciais
- `.env.example` contém apenas as chaves, sem valores

---

## 6. CI/CD

### 6.1 Status Atual
Não há pipeline de CI/CD automatizado — o projeto é executado manualmente via CLI.

### 6.2 Pipeline Sugerido (futuro)

Se necessário, um GitHub Actions workflow poderia:

```yaml
# .github/workflows/test.yml (sugestão para futuro)
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/test_prompts.py -v
```

Este pipeline validaria apenas os testes estruturais (não requer API keys).

---

## 7. Observabilidade

### 7.1 LangSmith Tracing

Quando `LANGSMITH_TRACING=true`, todas as chamadas ao LLM são automaticamente rastreadas no dashboard do LangSmith:

- **Inputs:** Prompt completo enviado ao LLM
- **Outputs:** Resposta gerada
- **Latência:** Tempo de cada chamada
- **Tokens:** Contagem de tokens de entrada/saída
- **Erros:** Stack traces de falhas

### 7.2 Logs do Terminal

Cada script produz output estruturado no terminal:
- Indicadores visuais (✓, ❌, ⚠️)
- Scores com threshold de aprovação
- Resumo final com status APROVADO/REPROVADO

---

## 8. Estrutura de Diretórios

```
desafio-2/
├── .env                  # Credenciais (local, não commitado)
├── .env.example          # Template de credenciais
├── .gitignore            # Regras de exclusão
├── requirements.txt      # Dependências Python (pinned)
├── README.md             # Documentação principal
│
├── docs/                 # Documentação do projeto
│   ├── prd.md
│   ├── frd.md
│   ├── adr.md
│   ├── guidelines.md
│   ├── design.md
│   └── infra.md
│
├── datasets/             # Dataset de avaliação (não alterar)
│   └── bug_to_user_story.jsonl
│
├── prompts/              # Prompts YAML
│   ├── bug_to_user_story_v1.yml    # Baseline (pull)
│   └── bug_to_user_story_v2.yml    # Otimizado (criar)
│
├── src/                  # Código-fonte
│   ├── __init__.py
│   ├── pull_prompts.py   # Script de pull
│   ├── push_prompts.py   # Script de push
│   ├── evaluate.py       # Avaliação (pré-existente)
│   ├── metrics.py        # Métricas (pré-existente)
│   └── utils.py          # Utilidades (pré-existente)
│
└── tests/                # Testes automatizados
    ├── __init__.py
    └── test_prompts.py   # Validação do prompt
```

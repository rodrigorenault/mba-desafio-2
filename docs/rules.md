# AI Behavioral Rules

## Projeto: Desafio 2 — Pull, Otimização e Avaliação de Prompts

**Versão:** 1.0
**Data:** 2026-03-19

---

## 1. Project Context

This is a Python CLI project for prompt optimization using LangChain and LangSmith. The goal is to transform a low-quality prompt (v1) into an optimized prompt (v2) that achieves >= 0.9 on all 4 evaluation metrics for converting Bug Reports into User Stories.

---

## 2. Code Rules

### 2.1 Do NOT Modify
- `src/evaluate.py` — Evaluation orchestrator (provided, complete)
- `src/metrics.py` — 7 LLM-as-Judge metrics (provided, complete)
- `src/utils.py` — Shared utilities (provided, complete)
- `datasets/bug_to_user_story.jsonl` — 15 bug examples (provided, immutable)

### 2.2 Must Implement
- `src/pull_prompts.py` — Fill in stubs (`...`) to pull prompt from LangSmith Hub
- `src/push_prompts.py` — Fill in stubs (`...`) to push prompt to LangSmith Hub
- `tests/test_prompts.py` — Implement 6 required test methods
- `prompts/bug_to_user_story_v2.yml` — Create the optimized prompt (main deliverable)

### 2.3 Python Standards
- Python 3.9+ with type hints
- PEP 8 style
- Google-style docstrings
- UTF-8 encoding
- Import order: stdlib → third-party → local

---

## 3. Prompt Engineering Rules

### 3.1 The prompt v2 MUST contain:
1. A detailed persona definition (Role Prompting)
2. At least 2-3 few-shot examples covering simple, medium, and complex bugs
3. Step-by-step reasoning instructions (Chain of Thought)
4. Explicit output format/template for user stories
5. Rules for handling edge cases (multi-issue bugs, critical severity)
6. Clear separation between system_prompt and user_prompt
7. No `[TODO]` placeholders

### 3.2 The prompt v2 MUST NOT contain:
- `[TODO]` or placeholder text
- Vague instructions ("do your best", "try to")
- References to the evaluation system or scores
- Hardcoded bug examples in the user_prompt

### 3.3 YAML Format
- Root key: `bug_to_user_story_v2`
- Required fields: `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied`
- `user_prompt` must contain `{bug_report}` placeholder
- `techniques_applied` must list >= 2 techniques

---

## 4. Evaluation Target

All 4 metrics must achieve >= 0.9:

| Metric | What it measures | Key tips to score high |
|--------|-----------------|----------------------|
| **Tone Score** | Professional + empathetic tone | Use "Como um [user]..." format; focus on value, not just bug fixing |
| **Acceptance Criteria** | Given-When-Then quality | 3-7 specific, testable criteria; include edge cases |
| **User Story Format** | "Como um..., eu quero..., para que..." | All 3 parts present; specific persona; real benefit |
| **Completeness** | Proportional to bug complexity | Simple bugs = concise; Complex bugs = technical context + tasks |

---

## 5. Iteration Workflow

1. Edit `prompts/bug_to_user_story_v2.yml`
2. Run `pytest tests/test_prompts.py -v` (structural validation)
3. Run `python src/push_prompts.py` (push to Hub)
4. Run `python src/evaluate.py` (evaluate scores)
5. If any metric < 0.9: read reasoning, adjust prompt, repeat from step 1
6. If all metrics >= 0.9: commit, update README, capture screenshots

---

## 6. Git Conventions

- Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`
- Never commit `.env` or API keys
- One feature per commit
- README must document: techniques, results (v1 vs v2), how to run

---

## 7. Documentation Rules

- Read existing docs before any implementation
- Update `frd.md` and `adr.md` after significant changes
- Keep `rules.md` current with any new behavioral guidelines
- README.md is the primary deliverable documentation

---

## 8. Testing Rules

- 6 mandatory tests in `tests/test_prompts.py`
- All tests must pass before push
- Tests validate prompt structure, not LLM output quality
- Run with: `pytest tests/test_prompts.py -v`

---

## 9. LLM Provider Configuration

- Default: Google Gemini (`gemini-2.5-flash`) — free tier
- Alternative: OpenAI (`gpt-4o-mini` + `gpt-4o`) — paid
- Switch provider by changing `LLM_PROVIDER` in `.env`
- Be aware of Gemini rate limits: 15 req/min

---

## 10. Security

- All credentials in `.env` only
- `.env` is in `.gitignore`
- `.env.example` has empty values as template
- Validate env vars before any API call

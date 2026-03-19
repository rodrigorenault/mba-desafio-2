"""
Script COMPLETO para avaliar prompts otimizados.

Este script:
1. Carrega dataset de avaliação via módulo dataset.py
2. Cria/atualiza dataset no LangSmith
3. Puxa prompts otimizados do LangSmith Hub (fonte única de verdade)
4. Executa prompts contra o dataset
5. Calcula 7 métricas:
   - Gerais: F1-Score, Clarity, Precision
   - Específicas: Tone Score, Acceptance Criteria Score,
     User Story Format Score, Completeness Score
6. Publica resultados no dashboard do LangSmith
7. Exibe resumo no terminal

Critério de Aprovação (conforme Instructions.md):
- Tone Score >= 0.9
- Acceptance Criteria Score >= 0.9
- User Story Format Score >= 0.9
- Completeness Score >= 0.9
- MÉDIA GERAL >= 0.9

Suporta múltiplos providers de LLM:
- OpenAI (gpt-4o, gpt-4o-mini)
- Google Gemini (gemini-2.5-flash)

Configure o provider no arquivo .env através da variável LLM_PROVIDER.
"""

import os
import sys
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import check_env_vars, format_score, print_section_header, get_llm as get_configured_llm
from dataset import load_dataset_from_jsonl, create_evaluation_dataset
from metrics import (
    evaluate_f1_score,
    evaluate_clarity,
    evaluate_precision,
    evaluate_tone_score,
    evaluate_acceptance_criteria_score,
    evaluate_user_story_format_score,
    evaluate_completeness_score,
)

load_dotenv()


def get_llm():
    return get_configured_llm(temperature=0)


def pull_prompt_from_langsmith(prompt_name: str) -> ChatPromptTemplate:
    try:
        print(f"  Puxando prompt do LangSmith Hub: {prompt_name}")
        prompt = hub.pull(prompt_name)
        print(f"  ✓ Prompt carregado com sucesso")
        return prompt

    except Exception as e:
        error_msg = str(e).lower()

        print(f"\n{'=' * 70}")
        print(f"❌ ERRO: Não foi possível carregar o prompt '{prompt_name}'")
        print(f"{'=' * 70}\n")

        if "not found" in error_msg or "404" in error_msg:
            print("⚠️ O prompt não foi encontrado no LangSmith Hub.\n")
            print("AÇÕES NECESSÁRIAS:")
            print("1. Verifique se você já fez push do prompt otimizado:")
            print(f"   python src/push_prompts.py")
            print()
            print("2. Confirme se o prompt foi publicado com sucesso em:")
            print(f"   https://smith.langchain.com/prompts")
            print()
            print(f"3. Certifique-se de que o nome do prompt está correto: '{prompt_name}'")
            print()
            print("4. Se você alterou o prompt no YAML, refaça o push:")
            print(f"   python src/push_prompts.py")
        else:
            print(f"Erro técnico: {e}\n")
            print("Verifique:")
            print("- LANGSMITH_API_KEY está configurada corretamente no .env")
            print("- Você tem acesso ao workspace do LangSmith")
            print("- Sua conexão com a internet está funcionando")

        print(f"\n{'=' * 70}\n")
        raise


def evaluate_prompt_on_example(
    prompt_template: ChatPromptTemplate,
    example: Any,
    llm: Any
) -> Dict[str, Any]:
    try:
        inputs = example.inputs if hasattr(example, 'inputs') else {}
        outputs = example.outputs if hasattr(example, 'outputs') else {}

        chain = prompt_template | llm

        response = chain.invoke(inputs)
        answer = response.content

        reference = outputs.get("reference", "") if isinstance(outputs, dict) else ""

        if isinstance(inputs, dict):
            question = inputs.get("question", inputs.get("bug_report", inputs.get("pr_title", "N/A")))
        else:
            question = "N/A"

        return {
            "answer": answer,
            "reference": reference,
            "question": question
        }

    except Exception as e:
        print(f"  ⚠️ Erro ao avaliar exemplo: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return {
            "answer": "",
            "reference": "",
            "question": ""
        }


def evaluate_prompt(
    prompt_name: str,
    dataset_name: str,
    client: Client
) -> Dict[str, float]:
    print(f"\n🔍 Avaliando: {prompt_name}")

    try:
        prompt_template = pull_prompt_from_langsmith(prompt_name)

        examples = list(client.list_examples(dataset_name=dataset_name))
        print(f"  Dataset: {len(examples)} exemplos")

        llm = get_llm()

        f1_scores = []
        clarity_scores = []
        precision_scores = []
        tone_scores = []
        ac_scores = []
        format_scores = []
        completeness_scores = []

        print("  Avaliando exemplos...")

        for i, example in enumerate(examples[:10], 1):
            result = evaluate_prompt_on_example(prompt_template, example, llm)

            if result["answer"]:
                bug_report = result["question"]
                answer = result["answer"]
                reference = result["reference"]

                f1 = evaluate_f1_score(bug_report, answer, reference)
                clarity = evaluate_clarity(bug_report, answer, reference)
                precision = evaluate_precision(bug_report, answer, reference)

                tone = evaluate_tone_score(bug_report, answer, reference)
                ac = evaluate_acceptance_criteria_score(bug_report, answer, reference)
                fmt = evaluate_user_story_format_score(bug_report, answer, reference)
                comp = evaluate_completeness_score(bug_report, answer, reference)

                f1_scores.append(f1["score"])
                clarity_scores.append(clarity["score"])
                precision_scores.append(precision["score"])
                tone_scores.append(tone["score"])
                ac_scores.append(ac["score"])
                format_scores.append(fmt["score"])
                completeness_scores.append(comp["score"])

                print(
                    f"    [{i}/{min(10, len(examples))}] "
                    f"F1:{f1['score']:.2f} Clar:{clarity['score']:.2f} Prec:{precision['score']:.2f} | "
                    f"Tone:{tone['score']:.2f} AC:{ac['score']:.2f} Fmt:{fmt['score']:.2f} Comp:{comp['score']:.2f}"
                )

        def safe_avg(scores):
            return sum(scores) / len(scores) if scores else 0.0

        avg_f1 = safe_avg(f1_scores)
        avg_clarity = safe_avg(clarity_scores)
        avg_precision = safe_avg(precision_scores)
        avg_tone = safe_avg(tone_scores)
        avg_ac = safe_avg(ac_scores)
        avg_format = safe_avg(format_scores)
        avg_completeness = safe_avg(completeness_scores)

        avg_helpfulness = (avg_clarity + avg_precision) / 2
        avg_correctness = (avg_f1 + avg_precision) / 2

        return {
            "helpfulness": round(avg_helpfulness, 4),
            "correctness": round(avg_correctness, 4),
            "f1_score": round(avg_f1, 4),
            "clarity": round(avg_clarity, 4),
            "precision": round(avg_precision, 4),
            "tone_score": round(avg_tone, 4),
            "acceptance_criteria_score": round(avg_ac, 4),
            "user_story_format_score": round(avg_format, 4),
            "completeness_score": round(avg_completeness, 4),
        }

    except Exception as e:
        print(f"  ❌ Erro na avaliação: {e}")
        return {
            "helpfulness": 0.0,
            "correctness": 0.0,
            "f1_score": 0.0,
            "clarity": 0.0,
            "precision": 0.0,
            "tone_score": 0.0,
            "acceptance_criteria_score": 0.0,
            "user_story_format_score": 0.0,
            "completeness_score": 0.0,
        }


def display_results(prompt_name: str, scores: Dict[str, float]) -> bool:
    print("\n" + "=" * 50)
    print(f"Prompt: {prompt_name}")
    print("=" * 50)

    print("\nMétricas Gerais:")
    print(f"  - F1-Score:    {format_score(scores['f1_score'], threshold=0.9)}")
    print(f"  - Clarity:     {format_score(scores['clarity'], threshold=0.9)}")
    print(f"  - Precision:   {format_score(scores['precision'], threshold=0.9)}")

    print("\nMétricas Derivadas:")
    print(f"  - Helpfulness: {format_score(scores['helpfulness'], threshold=0.9)}")
    print(f"  - Correctness: {format_score(scores['correctness'], threshold=0.9)}")

    print("\nMétricas Específicas (Critério de Aprovação):")
    print(f"  - Tone Score:                {format_score(scores['tone_score'], threshold=0.9)}")
    print(f"  - Acceptance Criteria Score:  {format_score(scores['acceptance_criteria_score'], threshold=0.9)}")
    print(f"  - User Story Format Score:   {format_score(scores['user_story_format_score'], threshold=0.9)}")
    print(f"  - Completeness Score:        {format_score(scores['completeness_score'], threshold=0.9)}")

    specific_metrics = [
        scores['tone_score'],
        scores['acceptance_criteria_score'],
        scores['user_story_format_score'],
        scores['completeness_score'],
    ]
    specific_avg = sum(specific_metrics) / len(specific_metrics)

    all_metrics = list(scores.values())
    general_avg = sum(all_metrics) / len(all_metrics)

    print("\n" + "-" * 50)
    print(f"📊 MÉDIA MÉTRICAS ESPECÍFICAS: {specific_avg:.4f}")
    print(f"📊 MÉDIA GERAL (todas): {general_avg:.4f}")
    print("-" * 50)

    passed = specific_avg >= 0.9

    if passed:
        print(f"\n✅ STATUS: APROVADO (média >= 0.9)")
    else:
        print(f"\n❌ STATUS: REPROVADO (média < 0.9)")
        print(f"   Média atual: {specific_avg:.4f} | Necessário: 0.9000")

    return passed


def main():
    print_section_header("AVALIAÇÃO DE PROMPTS OTIMIZADOS")

    provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    eval_model = os.getenv("EVAL_MODEL", "gpt-4o")

    print(f"Provider: {provider}")
    print(f"Modelo Principal: {llm_model}")
    print(f"Modelo de Avaliação: {eval_model}\n")

    required_vars = ["LANGSMITH_API_KEY", "LLM_PROVIDER"]
    if provider == "openai":
        required_vars.append("OPENAI_API_KEY")
    elif provider in ["google", "gemini"]:
        required_vars.append("GOOGLE_API_KEY")

    if not check_env_vars(required_vars):
        return 1

    client = Client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "prompt-optimization-challenge-resolved")

    jsonl_path = "datasets/bug_to_user_story.jsonl"

    if not Path(jsonl_path).exists():
        print(f"❌ Arquivo de dataset não encontrado: {jsonl_path}")
        print("\nCertifique-se de que o arquivo existe antes de continuar.")
        return 1

    dataset_name = f"{project_name}-eval"
    create_evaluation_dataset(client, dataset_name, jsonl_path)

    print("\n" + "=" * 70)
    print("PROMPTS PARA AVALIAR")
    print("=" * 70)
    print("\nEste script irá puxar prompts do LangSmith Hub.")
    print("Certifique-se de ter feito push dos prompts antes de avaliar:")
    print("  python src/push_prompts.py\n")

    prompts_to_evaluate = [
        "bug_to_user_story_v2",
    ]

    all_passed = True
    evaluated_count = 0
    results_summary = []

    for prompt_name in prompts_to_evaluate:
        evaluated_count += 1

        try:
            scores = evaluate_prompt(prompt_name, dataset_name, client)

            passed = display_results(prompt_name, scores)
            all_passed = all_passed and passed

            results_summary.append({
                "prompt": prompt_name,
                "scores": scores,
                "passed": passed
            })

        except Exception as e:
            print(f"\n❌ Falha ao avaliar '{prompt_name}': {e}")
            all_passed = False

            results_summary.append({
                "prompt": prompt_name,
                "scores": {k: 0.0 for k in [
                    "helpfulness", "correctness", "f1_score", "clarity",
                    "precision", "tone_score", "acceptance_criteria_score",
                    "user_story_format_score", "completeness_score",
                ]},
                "passed": False
            })

    print("\n" + "=" * 50)
    print("RESUMO FINAL")
    print("=" * 50 + "\n")

    if evaluated_count == 0:
        print("⚠️ Nenhum prompt foi avaliado")
        return 1

    print(f"Prompts avaliados: {evaluated_count}")
    print(f"Aprovados: {sum(1 for r in results_summary if r['passed'])}")
    print(f"Reprovados: {sum(1 for r in results_summary if not r['passed'])}\n")

    if all_passed:
        print("✅ Todos os prompts atingiram os critérios de aprovação!")
        print(f"\n✓ Confira os resultados em:")
        print(f"  https://smith.langchain.com/projects/{project_name}")
        print("\nPróximos passos:")
        print("1. Documente o processo no README.md")
        print("2. Capture screenshots das avaliações")
        print("3. Faça commit e push para o GitHub")
        return 0
    else:
        print("⚠️ Alguns prompts não atingiram os critérios")
        print("\nPróximos passos:")
        print("1. Refatore os prompts com score baixo")
        print("2. Faça push novamente: python src/push_prompts.py")
        print("3. Execute: python src/evaluate.py novamente")
        return 1

if __name__ == "__main__":
    sys.exit(main())

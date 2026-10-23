"""Classificacao por conceitos lexicais, sem dependencias externas."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SE_CONCEPTS = {
    "engenharia de software": ("software engineering",),
    "desenvolvimento de software": ("software development",),
    "testes de software": (
        "software testing", "unit testing", "unit tests",
        "test generation",
    ),
    "manutencao de software": ("software maintenance",),
    "requisitos de software": ("software requirements",),
    "projeto de software": ("software design",),
    "arquitetura de software": ("software architecture",),
    "qualidade de software": ("software quality",),
    "repositorios de software": (
        "software repository", "software repositories",
    ),
    "geracao de codigo": ("code generation",),
    "completamento de codigo": ("code completion",),
    "revisao de codigo": ("code review",),
    "sumarizacao de codigo": ("code summarization",),
    "reparo de programas": ("code repair", "program repair"),
    "sintese de programas": ("program synthesis",),
    "deteccao de defeitos": (
        "bug detection", "bug localization", "defect prediction",
    ),
    "codigo fonte": ("source code",),
}

AI_CONCEPTS = {
    "inteligencia artificial": (
        "artificial intelligence", "intelligent systems",
        "ai assisted", "ai powered",
    ),
    "aprendizado de maquina": ("machine learning",),
    "aprendizado profundo": (
        "deep learning", "neural network", "neural networks",
    ),
    "modelos de linguagem": (
        "large language model", "large language models",
        "language model", "language models", "llm", "llms",
    ),
    "aprendizado por reforco": ("reinforcement learning",),
    "agentes de IA": ("ai agent", "ai agents"),
}


def normalize(text):
    return " ".join(
        re.sub(r"[-\u2010-\u2015]", " ", text.lower()).split()
    )


def find_concepts(text, concepts):
    evidence = {}
    for concept, terms in concepts.items():
        matches = [
            term for term in terms
            if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text)
        ]
        if matches:
            evidence[concept] = matches
    return evidence


def classify(paper):
    text = normalize(paper["title"] + " " + paper["summary"])
    se = find_concepts(text, SE_CONCEPTS)
    ai = find_concepts(text, AI_CONCEPTS)
    selected = bool(se and ai)

    if selected:
        score = 3 + min(2, len(se) + len(ai) - 2)
        justification = (
            "Incluido por evidencias dos dois temas no titulo/resumo. "
            "Engenharia de Software: " + ", ".join(se) + ". "
            "Sistemas Inteligentes: " + ", ".join(ai) + ". "
            "Nota baseada no numero de conceitos lexicais distintos; "
            "nao mede qualidade cientifica nem confirma relacao semantica."
        )
    elif se or ai:
        score = min(2, len(se) + len(ai))
        missing = "Sistemas Inteligentes" if se else "Engenharia de Software"
        justification = (
            "Nao incluido: faltam evidencias lexicais de " + missing + "."
        )
    else:
        score = 0
        justification = "Nao incluido: nenhuma expressao dos temas foi encontrada."

    return {
        **paper,
        "score": score,
        "selected": selected,
        "justification": justification,
        "evidence": {
            "software_engineering": se,
            "intelligent_systems": ai,
        },
        "classifier_version": "concepts-v2",
    }


def main():
    source = ROOT / "data" / "candidates.json"
    papers = json.loads(source.read_text(encoding="utf-8"))
    evaluated = [classify(paper) for paper in papers]
    selected = [paper for paper in evaluated if paper["selected"]]

    (ROOT / "data" / "evaluated.json").write_text(
        json.dumps(evaluated, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Artigos avaliados: {len(evaluated)}")
    print(f"Artigos selecionados: {len(selected)}")
    for paper in selected:
        print(f"Nota {paper['score']}/5: {paper['title']}")


if __name__ == "__main__":
    main()

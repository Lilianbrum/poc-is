"""Consulta inicial ao arXiv usando apenas a biblioteca padrao."""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {"atom": "http://www.w3.org/2005/Atom"}

# Busca ampla de candidatos. A classificacao de relevancia sera uma
# etapa separada: pertencer a uma categoria nao garante inclusao.
QUERY = '(cat:cs.SE OR all:"software engineering" OR all:"program repair" OR all:"code generation")'


def clean(value):
    return " ".join((value or "").split())


def fetch_papers():
    params = urllib.parse.urlencode({
        "search_query": QUERY,
        "start": 0,
        "max_results": 100,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    request = urllib.request.Request(
        "https://export.arxiv.org/api/query?" + params,
        headers={
            "User-Agent": (
                "Lilianbrum-ArxivMonitor/0.1 "
                "(https://github.com/Lilianbrum/poc-is)"
            )
        },
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        root = ET.fromstring(response.read())

    papers = []
    for entry in root.findall("atom:entry", NS):
        url = clean(entry.findtext("atom:id", default="", namespaces=NS))

        if "/api/errors" in url:
            message = clean(
                entry.findtext("atom:summary", default="", namespaces=NS)
            )
            raise ValueError("O arXiv retornou um erro: " + message)

        if "/abs/" not in url:
            raise ValueError("Resposta com identificador de artigo inesperado.")

        papers.append({
            "arxiv_id": url.split("/abs/", 1)[1],
            "title": clean(
                entry.findtext("atom:title", default="", namespaces=NS)
            ),
            "authors": [
                clean(author.findtext("atom:name", default="", namespaces=NS))
                for author in entry.findall("atom:author", NS)
            ],
            "summary": clean(
                entry.findtext("atom:summary", default="", namespaces=NS)
            ),
            "published": entry.findtext(
                "atom:published", default="", namespaces=NS
            ),
            "updated": entry.findtext(
                "atom:updated", default="", namespaces=NS
            ),
            "categories": [
                category.get("term", "")
                for category in entry.findall("atom:category", NS)
            ],
            "url": url,
        })

    return papers


def main():
    print("Consultando o arXiv. Aguarde...")
    try:
        papers = fetch_papers()
        destination = ROOT / "data" / "candidates.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(papers, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except (urllib.error.URLError, OSError, ET.ParseError, ValueError) as error:
        print(f"Falha na consulta ou no salvamento: {error}", file=sys.stderr)
        return 1

    print(f"Consulta concluida: {len(papers)} artigos candidatos.")
    print(f"Metadados salvos em: {destination}")
    for paper in papers[:5]:
        print(f"- {paper['arxiv_id']}: {paper['title']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


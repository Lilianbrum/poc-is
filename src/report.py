"""Armazena as avaliacoes e gera o relatorio HTML."""

import html
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def escape(value):
    return html.escape(str(value), quote=True)


def main():
    source = ROOT / "data" / "evaluated.json"
    papers = json.loads(source.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()
    database = ROOT / "state" / "papers.db"

    new_selected = 0
    with sqlite3.connect(database) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                arxiv_id TEXT PRIMARY KEY,
                metadata_json TEXT NOT NULL,
                selected INTEGER NOT NULL,
                score INTEGER NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)

        for paper in papers:
            # Identifica o mesmo artigo mesmo quando sua versao muda.
            paper_id = re.sub(r"v\d+$", "", paper["arxiv_id"])
            exists = connection.execute(
                "SELECT 1 FROM papers WHERE arxiv_id = ?",
                (paper_id,),
            ).fetchone()

            if exists is None and paper["selected"]:
                new_selected += 1

            connection.execute("""
                INSERT INTO papers (
                    arxiv_id, metadata_json, selected, score,
                    first_seen, last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(arxiv_id) DO UPDATE SET
                    metadata_json = excluded.metadata_json,
                    selected = excluded.selected,
                    score = excluded.score,
                    last_seen = excluded.last_seen
            """, (
                paper_id,
                json.dumps(paper, ensure_ascii=False),
                int(paper["selected"]),
                paper["score"],
                now,
                now,
            ))

        total = connection.execute(
            "SELECT COUNT(*) FROM papers"
        ).fetchone()[0]

    selected = sorted(
        (paper for paper in papers if paper["selected"]),
        key=lambda paper: (paper["score"], paper["published"]),
        reverse=True,
    )

    cards = []
    for paper in selected:
        paper_id = paper["arxiv_id"]
        link = "https://arxiv.org/abs/" + paper_id
        cards.append(f"""
        <article>
          <div class="score">Nota {paper['score']}/5</div>
          <h2><a href="{escape(link)}">{escape(paper['title'])}</a></h2>
          <p><strong>arXiv ID:</strong> {escape(paper_id)}</p>
          <p><strong>Autores:</strong>
             {escape(', '.join(paper['authors']))}</p>
          <p><strong>Publicado em:</strong> {escape(paper['published'])}</p>
          <p><strong>Atualizado em:</strong> {escape(paper['updated'])}</p>
          <p><strong>Categorias:</strong>
             {escape(', '.join(paper['categories']))}</p>
          <h3>Resumo original</h3>
          <p>{escape(paper['summary'])}</p>
          <div class="reason">
            <strong>Justificativa:</strong>
            {escape(paper['justification'])}
          </div>
        </article>
        """)

    content = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Monitor arXiv — Relatorio</title>
<style>
body {font-family:Segoe UI,Arial,sans-serif;background:#f1f5f9;
      color:#172033;margin:0;line-height:1.65}
main {max-width:1000px;margin:auto;padding:32px 20px}
header {background:#102a43;color:white;padding:28px;border-radius:14px}
h1 {margin-top:0}
h2 {font-size:1.3rem}
a {color:#14548c}
article {background:white;padding:24px;margin:22px 0;border-radius:12px;
         border:1px solid #dbe3ec;overflow-wrap:anywhere}
.score {display:inline-block;background:#dbeafe;color:#173c72;
        padding:4px 12px;border-radius:20px;font-weight:bold}
.reason {background:#edf7f0;padding:16px;border-left:4px solid #29824b}
.notice {color:#475569}
@media print {
  body {background:white}
  article {break-inside:avoid}
}
</style>
</head>
<body><main>
"""
    content += f"""
<header>
<h1>Monitor de papers no arXiv</h1>
<p>Engenharia de Software e Sistemas Inteligentes</p>
<p>Gerado em UTC: {escape(now)}</p>
</header>
<p><strong>{len(papers)}</strong> candidatos avaliados nesta consulta;
<strong>{len(selected)}</strong> selecionados;
<strong>{new_selected}</strong> selecionados vistos pela primeira vez.</p>
<p class="notice">Este relatorio apresenta os selecionados da consulta atual.
Na primeira execucao, os registros formam a base inicial; isso nao significa
que tenham sido publicados hoje. A nota mede evidencias lexicais e requer
revisao humana. A consulta atual e limitada a 100 candidatos.</p>
"""
    content += "".join(cards) or "<p>Nenhum artigo selecionado nesta consulta.</p>"
    content += "</main></body></html>"

    destination = ROOT / "reports" / "latest.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")

    print(f"Registros no banco: {total}")
    print(f"Selecionados na consulta: {len(selected)}")
    print(f"Selecionados vistos pela primeira vez: {new_selected}")
    print(f"Relatorio salvo em: {destination}")


if __name__ == "__main__":
    main()


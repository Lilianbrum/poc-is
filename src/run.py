"""Executa a consulta, a classificacao e o relatorio em sequencia."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    stages = (
        ("Consulta ao arXiv", "monitor.py"),
        ("Classificacao dos artigos", "classifier.py"),
        ("Banco de dados e relatorio", "report.py"),
    )

    for name, filename in stages:
        print(f"\n=== {name} ===", flush=True)

        result = subprocess.run(
            [sys.executable, str(ROOT / "src" / filename)],
            cwd=ROOT,
            check=False,
        )

        if result.returncode != 0:
            print(
                f"\nExecucao interrompida na etapa: {name}. "
                "Um eventual relatorio anterior nao foi atualizado.",
                file=sys.stderr,
            )
            return result.returncode

    print("\nMonitoramento concluido.")
    print(f"Relatorio: {ROOT / 'reports' / 'latest.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

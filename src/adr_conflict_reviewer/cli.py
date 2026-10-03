import argparse
import sys
from typing import Sequence

from .renderer import render_report
from .repository import RepositoryError, load_repository
from .reviewer import AdrReviewer, ReviewError, create_openai_client


class CliError(ValueError):
    pass


class PortugueseParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError(
            "Argumentos inválidos. Informe o caminho da ADR proposta e o diretório de ADRs."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = PortugueseParser(description="Revisa conflitos entre uma ADR proposta e ADRs locais.")
    parser.add_argument("proposal", help="caminho do arquivo Markdown da ADR proposta")
    parser.add_argument("adr_directory", help="diretório que contém ADRs Markdown")
    return parser


def main(argv: Sequence[str] | None = None, reviewer: AdrReviewer | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        proposal, documents = load_repository(args.proposal, args.adr_directory)
        if reviewer is None:
            client, model = create_openai_client()
            reviewer = AdrReviewer(client, model)
        print(render_report(reviewer.review(proposal, documents)))
        return 0
    except (CliError, RepositoryError, ReviewError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 2

from pathlib import Path

from .models import AdrDocument

MAX_DOCUMENTS = 20
MAX_DOCUMENT_CHARS = 12_000
TRUNCATION_MARKER = "\n\n[Conteúdo truncado pelo limite do MVP.]"


class RepositoryError(ValueError):
    """Erro esperado ao ler documentos locais."""


def _validate_markdown_file(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise RepositoryError(f"O arquivo da {label} não foi encontrado: {path}.")
    if not resolved.is_file():
        raise RepositoryError(f"O caminho da {label} deve apontar para um arquivo: {path}.")
    if resolved.suffix.lower() != ".md":
        raise RepositoryError(f"O arquivo da {label} deve ter extensão .md: {path}.")
    return resolved


def _read_document(path: Path, label: str) -> AdrDocument:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        raise RepositoryError(f"Não foi possível ler a {label}: {path}.") from error
    if not content.strip():
        raise RepositoryError(f"A {label} está vazia. Adicione conteúdo Markdown antes de revisar.")
    if len(content) > MAX_DOCUMENT_CHARS:
        content = content[:MAX_DOCUMENT_CHARS] + TRUNCATION_MARKER
    return AdrDocument(path=str(path), content=content)


def load_repository(proposal_path: str, adr_directory: str) -> tuple[AdrDocument, list[AdrDocument]]:
    """Carrega a proposta e até vinte ADRs locais, em ordem determinística."""
    proposal_file = _validate_markdown_file(Path(proposal_path), "ADR proposta")
    directory = Path(adr_directory).expanduser().resolve()
    if not directory.exists():
        raise RepositoryError(f"O diretório de ADRs não foi encontrado: {adr_directory}.")
    if not directory.is_dir():
        raise RepositoryError(f"Informe um diretório de ADRs válido: {adr_directory}.")

    proposal = _read_document(proposal_file, "ADR proposta")
    candidates = sorted(
        (item.resolve() for item in directory.rglob("*") if item.is_file() and item.suffix.lower() == ".md"),
        key=lambda item: str(item),
    )
    documents = [
        _read_document(item, "ADR local")
        for item in candidates
        if item != proposal_file
    ]
    return proposal, documents[:MAX_DOCUMENTS]

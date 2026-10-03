from adr_conflict_reviewer.repository import (
    MAX_DOCUMENT_CHARS,
    TRUNCATION_MARKER,
    RepositoryError,
    load_repository,
)


def test_load_repository_orders_markdown_and_excludes_proposal(tmp_path):
    proposal = tmp_path / "adrs" / "proposal.md"
    proposal.parent.mkdir()
    proposal.write_text("# Proposed\nUse queues.", encoding="utf-8")
    (proposal.parent / "b.md").write_text("# B", encoding="utf-8")
    (proposal.parent / "a.md").write_text("# A", encoding="utf-8")
    (proposal.parent / "ignore.txt").write_text("ignored", encoding="utf-8")

    loaded_proposal, documents = load_repository(str(proposal), str(proposal.parent))

    assert loaded_proposal.path == str(proposal.resolve())
    assert [document.path for document in documents] == [
        str((proposal.parent / "a.md").resolve()),
        str((proposal.parent / "b.md").resolve()),
    ]


def test_load_repository_truncates_large_document(tmp_path):
    proposal = tmp_path / "proposal.md"
    directory = tmp_path / "adrs"
    directory.mkdir()
    proposal.write_text("proposal", encoding="utf-8")
    (directory / "large.md").write_text("x" * (MAX_DOCUMENT_CHARS + 10), encoding="utf-8")

    _, documents = load_repository(str(proposal), str(directory))

    assert documents[0].content.endswith(TRUNCATION_MARKER)
    assert len(documents[0].content) > MAX_DOCUMENT_CHARS


def test_load_repository_rejects_non_markdown_proposal(tmp_path):
    proposal = tmp_path / "proposal.txt"
    proposal.write_text("text", encoding="utf-8")
    directory = tmp_path / "adrs"
    directory.mkdir()

    try:
        load_repository(str(proposal), str(directory))
    except RepositoryError as error:
        assert "extensão .md" in str(error)
    else:
        raise AssertionError("Era esperado um erro para proposta sem extensão Markdown")

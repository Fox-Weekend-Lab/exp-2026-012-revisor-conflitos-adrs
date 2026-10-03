import os
from unittest.mock import patch

from adr_conflict_reviewer.cli import main
from adr_conflict_reviewer.models import ReviewReport


class StubReviewer:
    def review(self, proposal, documents):
        return ReviewReport(
            summary="Revisão concluída.",
            conflicts=[],
            review_questions=["A decisão foi aprovada?"],
        )


def test_cli_renders_report_with_injected_reviewer(tmp_path, capsys):
    proposal = tmp_path / "proposal.md"
    directory = tmp_path / "adrs"
    directory.mkdir()
    proposal.write_text("# Proposal", encoding="utf-8")
    (directory / "existing.md").write_text("# Existing", encoding="utf-8")

    result = main([str(proposal), str(directory)], reviewer=StubReviewer())

    captured = capsys.readouterr()
    assert result == 0
    assert "Nenhum conflito potencial" in captured.out
    assert "A decisão foi aprovada?" in captured.out


def test_cli_explains_missing_configuration(tmp_path, capsys):
    proposal = tmp_path / "proposal.md"
    directory = tmp_path / "adrs"
    directory.mkdir()
    proposal.write_text("# Proposal", encoding="utf-8")

    environment = {key: value for key, value in os.environ.items() if key not in {"OPENAI_API_KEY", "OPENAI_MODEL"}}
    with patch.dict(os.environ, environment, clear=True):
        result = main([str(proposal), str(directory)])

    assert result == 2
    assert "OPENAI_API_KEY" in capsys.readouterr().err


def test_cli_rejects_missing_arguments(capsys):
    result = main([])

    assert result == 2
    assert "Argumentos inválidos" in capsys.readouterr().err

from types import SimpleNamespace

from adr_conflict_reviewer.models import AdrDocument
from adr_conflict_reviewer.reviewer import AdrReviewer, ReviewError


class FakeResponses:
    def __init__(self, output=None, error=None):
        self.output = output
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(output_text=self.output)


class FakeClient:
    def __init__(self, output=None, error=None):
        self.responses = FakeResponses(output, error)


def test_reviewer_validates_conflict_and_sends_traceable_context():
    output = '''{"summary":"Há risco.","conflicts":[{"adr_path":"/adrs/001.md","quoted_excerpt":"Use REST","explanation":"A proposta usa eventos.","impact":"Integração."}],"review_questions":["Há migração?"]}'''
    client = FakeClient(output)
    reviewer = AdrReviewer(client, "configured-model")
    proposal = AdrDocument(path="/proposal.md", content="Use events")
    local = [AdrDocument(path="/adrs/001.md", content="Use REST")]

    report = reviewer.review(proposal, local)

    assert report.conflicts[0].adr_path == "/adrs/001.md"
    prompt = client.responses.calls[0]["input"]
    assert "/proposal.md" in prompt
    assert "/adrs/001.md" in prompt
    assert "cite literalmente" in prompt


def test_reviewer_accepts_report_without_conflicts():
    reviewer = AdrReviewer(FakeClient('{"summary":"Compatível.","conflicts":[],"review_questions":[]}'), "model")
    report = reviewer.review(AdrDocument(path="p.md", content="text"), [])

    assert report.conflicts == []


def test_reviewer_reports_invalid_json_without_network():
    reviewer = AdrReviewer(FakeClient("not json"), "model")

    try:
        reviewer.review(AdrDocument(path="p.md", content="text"), [])
    except ReviewError as error:
        assert "formato inválido" in str(error)
    else:
        raise AssertionError("Era esperado erro para JSON inválido")

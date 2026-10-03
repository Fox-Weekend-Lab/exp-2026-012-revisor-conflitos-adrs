import json
import os
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from .models import AdrDocument, ReviewReport


class ReviewError(RuntimeError):
    """Erro esperado durante a consulta ou validação do parecer."""


def create_openai_client() -> tuple[OpenAI, str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ReviewError("A variável OPENAI_API_KEY não está definida. Configure-a e tente novamente.")
    model = os.environ.get("OPENAI_MODEL")
    if not model:
        raise ReviewError("A variável OPENAI_MODEL não está definida. Informe o modelo a usar e tente novamente.")
    return OpenAI(api_key=api_key), model


def build_prompt(proposal: AdrDocument, documents: list[AdrDocument]) -> str:
    local_context = "\n\n".join(
        f"--- ADR LOCAL: {document.path} ---\n{document.content}\n--- FIM ADR LOCAL ---"
        for document in documents
    ) or "Nenhuma ADR local em Markdown foi encontrada."
    return f"""Você revisa decisões arquiteturais. Compare a ADR proposta com as ADRs locais.
Identifique apenas conflitos potenciais que possam ser justificados pelo contexto fornecido.
Para cada conflito, use o caminho exato de uma ADR local e cite literalmente um trecho dela.
Não invente arquivos, citações ou fatos. Mesmo sem conflitos, escreva um resumo útil.
Responda somente com JSON válido, sem cercas Markdown, neste formato:
{{"summary":"...","conflicts":[{{"adr_path":"...","quoted_excerpt":"...","explanation":"...","impact":"..."}}],"review_questions":["..."]}}

--- ADR PROPOSTA: {proposal.path} ---
{proposal.content}
--- FIM ADR PROPOSTA ---

{local_context}"""


class AdrReviewer:
    def __init__(self, client: Any, model: str):
        self.client = client
        self.model = model

    def review(self, proposal: AdrDocument, documents: list[AdrDocument]) -> ReviewReport:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=build_prompt(proposal, documents),
            )
        except Exception as error:
            raise ReviewError("Não foi possível consultar o modelo. Verifique a configuração e tente novamente.") from error

        output = getattr(response, "output_text", None)
        if not isinstance(output, str) or not output.strip():
            raise ReviewError("O modelo não retornou um parecer em texto. Tente novamente.")
        try:
            payload = json.loads(output)
            return ReviewReport.model_validate(payload)
        except (json.JSONDecodeError, ValidationError) as error:
            raise ReviewError("O modelo retornou um parecer em formato inválido. Tente novamente.") from error

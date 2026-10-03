from .models import ReviewReport


def render_report(report: ReviewReport) -> str:
    lines = ["PARECER DE REVISÃO DE ADRs", "", "Resumo", report.summary, ""]
    if report.conflicts:
        lines.append("Conflitos potenciais")
        for number, conflict in enumerate(report.conflicts, start=1):
            lines.extend(
                [
                    f"{number}. ADR relacionada: {conflict.adr_path}",
                    f"   Citação: {conflict.quoted_excerpt}",
                    f"   Explicação: {conflict.explanation}",
                    f"   Impacto: {conflict.impact}",
                ]
            )
    else:
        lines.append("Conflitos potenciais")
        lines.append("Nenhum conflito potencial foi identificado nas ADRs analisadas.")

    lines.extend(["", "Perguntas de revisão"])
    if report.review_questions:
        lines.extend(f"- {question}" for question in report.review_questions)
    else:
        lines.append("- Nenhuma pergunta de revisão foi sugerida.")
    return "\n".join(lines)

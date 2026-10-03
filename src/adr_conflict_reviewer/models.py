from pydantic import BaseModel, Field


class AdrDocument(BaseModel):
    path: str
    content: str


class ConflictFinding(BaseModel):
    adr_path: str = Field(min_length=1)
    quoted_excerpt: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    impact: str = Field(min_length=1)


class ReviewReport(BaseModel):
    summary: str = Field(min_length=1)
    conflicts: list[ConflictFinding]
    review_questions: list[str]

"""Prompt templates."""

from __future__ import annotations


def draft_answer_prompt(question: str, context: str) -> str:
    """Build draft answer prompt."""
    return f"DRAFT ANSWER\nQuestion: {question}\nContext:\n{context}\nAnswer using only context."


def missing_evidence_prompt(question: str, draft: str, context: str) -> str:
    """Build missing evidence prompt."""
    return f"MISSING EVIDENCE ANALYSIS\nQuestion: {question}\nDraft: {draft}\nContext:\n{context}"


def refinement_prompt(question: str, missing_reason: str) -> str:
    """Build refinement prompt."""
    return f"REFINE QUERY\nQuestion: {question}\nReason: {missing_reason}\nReturn refined query."


def final_answer_prompt(question: str, context: str) -> str:
    """Build final answer prompt."""
    return f"FINAL ANSWER WITH CITATIONS\nQuestion: {question}\nContext:\n{context}"

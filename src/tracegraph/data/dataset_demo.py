"""Synthetic demo corpus generation for offline tests."""

from __future__ import annotations

from tracegraph.data.models import Document, QAExample


def build_demo_documents() -> list[Document]:
    """Return deterministic multi-hop demo documents."""
    docs = [
        Document(doc_id="policy", title="Policy Manual", text="Retention Policy RP-17 states logs are kept 24 months. Clause C-12 requires compliance justification."),
        Document(doc_id="appendix", title="Policy Appendix", text="Exception E-9 allows shorter retention only if legal hold is absent and compliance clause C-12 is satisfied."),
        Document(doc_id="memo", title="Decision Memo", text="The committee decided to keep logs for 24 months, justified by clause C-12 in RP-17."),
        Document(doc_id="sop", title="Implementation SOP", text="Engineering enforces a 24 month retention job. Deviations must cite clause C-12."),
        Document(doc_id="glossary", title="Glossary", text="RP-17 means retention policy. C-12 is the compliance clause used for justification."),
        Document(doc_id="audit", title="Audit Note", text="Audit confirms decision memo references policy RP-17 and clause C-12."),
    ]
    return docs


def build_demo_qa() -> list[QAExample]:
    """Return deterministic QA set with support refs."""
    return [
        QAExample(
            example_id="q1",
            question="What decision did we make about data retention, and which compliance clause justified it?",
            answer="Logs were kept for 24 months, justified by clause C-12.",
            supporting_facts=[{"title": "Decision Memo"}, {"title": "Policy Manual"}],
        ),
        QAExample(
            example_id="q2",
            question="Which policy identifier is referenced by the decision memo?",
            answer="RP-17",
            supporting_facts=[{"title": "Decision Memo"}, {"title": "Glossary"}],
        ),
        QAExample(
            example_id="q3",
            question="Which clause is cited in both the implementation SOP and the policy manual?",
            answer="C-12",
            supporting_facts=[{"title": "Implementation SOP"}, {"title": "Policy Manual"}],
        ),
        QAExample(
            example_id="q4",
            question="What retention duration is enforced and where was that decision recorded?",
            answer="24 months in the Decision Memo.",
            supporting_facts=[{"title": "Implementation SOP"}, {"title": "Decision Memo"}],
        ),
        QAExample(
            example_id="q5",
            question="What exception is described and what condition must still be satisfied?",
            answer="Exception E-9 allows shorter retention only when clause C-12 is satisfied.",
            supporting_facts=[{"title": "Policy Appendix"}, {"title": "Policy Manual"}],
        ),
        QAExample(
            example_id="q6",
            question="Which audit source confirms the memo references both RP-17 and C-12?",
            answer="Audit Note.",
            supporting_facts=[{"title": "Audit Note"}, {"title": "Decision Memo"}],
        ),
        QAExample(
            example_id="q7",
            question="What does RP-17 refer to according to the glossary and policy text?",
            answer="RP-17 refers to the retention policy.",
            supporting_facts=[{"title": "Glossary"}, {"title": "Policy Manual"}],
        ),
        QAExample(
            example_id="q8",
            question="Why are deviations restricted in engineering enforcement?",
            answer="Because deviations must cite compliance clause C-12.",
            supporting_facts=[{"title": "Implementation SOP"}, {"title": "Policy Manual"}],
        ),
    ]

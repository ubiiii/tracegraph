"""Synthetic demo corpus generation for offline tests."""

from __future__ import annotations

from tracegraph.data.models import Document, QAExample


def build_demo_documents() -> list[Document]:
    """Return deterministic multi-hop demo documents."""
    docs = [
        Document(
            doc_id="policy",
            title="Policy Manual",
            text=(
                "RP-17 is the enterprise policy for operational log retention. The default retention period for operational logs is 24 months unless an approved exception applies.\n\n"
                "Compliance clause C-12 requires every deviation from the default retention period to include a written business or regulatory justification. The justification must be traceable in the policy record.\n\n"
                "Exception E-9 may extend or suspend deletion only when a legal hold is active and the request cites C-12. Without both conditions, RP-17 remains the controlling rule."
            ),
        ),
        Document(
            doc_id="appendix",
            title="Policy Appendix",
            text=(
                "The appendix to RP-17 defines how retention exceptions are recorded. Exception E-9 is available for operational logs when legal hold documentation exists and clause C-12 is cited as the justification basis.\n\n"
                "For normal operations, the 24 month retention default still applies. E-9 does not replace RP-17; it only pauses or extends deletion during an approved legal hold.\n\n"
                "The records office must attach the C-12 justification note to the retention register before engineering changes any deletion schedule."
            ),
        ),
        Document(
            doc_id="memo",
            title="Decision Memo",
            text=(
                "The retention decision for RP-17 confirmed that operational logs will be retained for 24 months by default. The approval relied on compliance clause C-12 because the committee required a documented justification for any deviation.\n\n"
                "The memo states that Exception E-9 can be used only when a legal hold exists and the request cites C-12. The committee rejected informal extensions that lack those two conditions.\n\n"
                "This memo is cross-referenced by the audit team whenever RP-17 retention handling is reviewed."
            ),
        ),
        Document(
            doc_id="sop",
            title="Implementation SOP",
            text=(
                "Engineering teams must configure operational log storage according to RP-17. The standard deletion timer is set to 24 months from log creation.\n\n"
                "Any deviation from the timer must cite compliance clause C-12 in the deployment ticket. If the deviation is based on Exception E-9, the ticket must also show an active legal hold.\n\n"
                "Operations engineers may not extend operational log retention without both the C-12 justification and the exception record required by the Policy Appendix."
            ),
        ),
        Document(
            doc_id="glossary",
            title="Glossary",
            text=(
                "RP-17 means the enterprise retention policy for operational logs. Its default retention period is 24 months.\n\n"
                "C-12 means the compliance clause requiring written justification for retention deviations. It is the clause cited by engineering when retention settings differ from RP-17.\n\n"
                "E-9 means the exception process that permits retention suspension or extension during legal hold, but only when C-12 is cited."
            ),
        ),
        Document(
            doc_id="audit",
            title="Audit Note",
            text=(
                "The audit review confirmed that RP-17, the Decision Memo, and compliance clause C-12 align on the 24 month operational log retention default.\n\n"
                "The audit team found that engineering SOP tickets properly cite C-12 for deviations. It also confirmed that Exception E-9 was limited to cases with legal hold documentation.\n\n"
                "The filing date for the audit review was 2025-04-18, and it was logged in the compliance register under entry CR-552."
            ),
        ),
    ]
    return docs


def build_demo_qa() -> list[QAExample]:
    """Return deterministic QA set with support refs."""
    return [
        QAExample(
            example_id="q1",
            question="What retention decision was made for operational logs, and which compliance clause justified deviations?",
            answer="Operational logs are retained for 24 months by default, and deviations are justified under C-12.",
            supporting_facts=[{"title": "Policy Manual"}, {"title": "Decision Memo"}],
        ),
        QAExample(
            example_id="q2",
            question="Which exception can extend or suspend deletion, and what two conditions are required?",
            answer="Exception E-9 can extend or suspend deletion when a legal hold is active and C-12 is cited.",
            supporting_facts=[{"title": "Policy Manual"}, {"title": "Policy Appendix"}],
        ),
        QAExample(
            example_id="q3",
            question="What must engineering cite when changing the deletion timer away from RP-17?",
            answer="Engineering must cite C-12 in the deployment ticket.",
            supporting_facts=[{"title": "Implementation SOP"}, {"title": "Glossary"}],
        ),
        QAExample(
            example_id="q4",
            question="Which documents show that E-9 does not replace the 24 month RP-17 default?",
            answer="The Policy Appendix says E-9 does not replace RP-17, and the Policy Manual keeps RP-17 as the controlling rule without both conditions.",
            supporting_facts=[{"title": "Policy Appendix"}, {"title": "Policy Manual"}],
        ),
        QAExample(
            example_id="q5",
            question="What did the audit confirm about RP-17 and C-12?",
            answer="The audit confirmed that RP-17, the Decision Memo, and C-12 align on the 24 month operational log retention default.",
            supporting_facts=[{"title": "Audit Note"}, {"title": "Decision Memo"}],
        ),
        QAExample(
            example_id="q6",
            question="When can operations engineers extend operational log retention?",
            answer="They can extend retention only with the C-12 justification and the exception record required by the Policy Appendix.",
            supporting_facts=[{"title": "Implementation SOP"}, {"title": "Policy Appendix"}],
        ),
        QAExample(
            example_id="q7",
            question="Which clause is cited by engineering for retention settings that differ from RP-17?",
            answer="C-12 is cited by engineering when retention settings differ from RP-17.",
            supporting_facts=[{"title": "Glossary"}, {"title": "Implementation SOP"}],
        ),
        QAExample(
            example_id="q8",
            question="What informal extension did the committee reject?",
            answer="The committee rejected informal extensions that lack legal hold and C-12.",
            supporting_facts=[{"title": "Decision Memo"}, {"title": "Policy Manual"}],
        ),
        QAExample(
            example_id="q9",
            question="What was the audit filing date and where was it logged?",
            answer="The audit filing date was 2025-04-18, and it was logged in the compliance register under entry CR-552.",
            supporting_facts=[{"title": "Audit Note"}],
        ),
    ]

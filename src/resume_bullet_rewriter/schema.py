from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class BulletFeedback:
    original: str
    verdict: str  # 'good' or 'needs_improvement'
    feedback: str
    clarifying_questions: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]

    def to_dict(self):
        return asdict(self)


def validate_feedback(obj: BulletFeedback, n_expected: int, keep_metrics: bool, original_has_numbers: bool) -> None:
    assert isinstance(obj.original, str)
    assert obj.verdict in ("good", "needs_improvement")
    assert isinstance(obj.feedback, str)
    assert isinstance(obj.clarifying_questions, list)
    assert isinstance(obj.suggestions, list)
    if obj.verdict == "needs_improvement":
        assert len(obj.suggestions) == n_expected, f"Expected {n_expected} suggestions, got {len(obj.suggestions)}"
    # If keep_metrics and original has numbers, ensure numbers preserved in at least one suggestion
    if keep_metrics and original_has_numbers:
        import re

        orig_nums = re.findall(r"\d[\d,\.]*", obj.original)
        all_text = " ".join(obj.suggestions)
        for num in orig_nums:
            assert num in all_text, f"Expected number {num} to be preserved"

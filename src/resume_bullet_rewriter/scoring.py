from typing import List
from resume_bullet_rewriter.utils import BANNED_WORDS, STRONG_VERBS


def score_variant(text: str) -> int:
    score = 0
    txt = text.lower()
    # prefer strong verbs
    for v in STRONG_VERBS:
        if v in txt:
            score += 5
    # penalize banned words
    for b in BANNED_WORDS:
        if b in txt:
            score -= 10
    # prefer brevity
    score += max(0, 3 - (len(text.split()) // 10))
    return score


def pick_top_two(variants: List[dict]) -> List[dict]:
    scored = [(score_variant(v["text"]), v) for v in variants]
    scored.sort(key=lambda x: x[0], reverse=True)
    top2 = [scored[i][1] for i in range(min(2, len(scored)))]
    return top2

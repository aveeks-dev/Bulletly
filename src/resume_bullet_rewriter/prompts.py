SYSTEM_PROMPT = """
You are a resume bullet rewriting expert. Do not invent metrics or claims. Preserve factuality and avoid buzzword-only phrasing. Keep tense consistent, start with strong verbs, include scope and technology when appropriate, and optimize for ATS clarity. Output a single JSON object matching the schema described in the user instruction.
"""


def build_user_prompt(bullet: str, role: str, seniority: str, style: str, tone: str, keep_metrics: bool, n: int):
    keep = "strictly preserve any numbers exactly" if keep_metrics else "do not invent numbers"
    return (
        f"Bullet: {bullet}\n"
        f"Role: {role}\n"
        f"Seniority: {seniority}\n"
        f"Style: {style}\n"
        f"Tone: {tone}\n"
        f"Rule: {keep}.\n"
        f"Constraints: Return JSON object with fields: original (string), critique (string), clarifying_questions (array),\n"
        f"variants (array of objects with text, style, tone), best_picks (array with 2 items containing text and reason),\n"
        f"Limit each variant to <= 2 lines; produce {n} variants.\n"
    )


def build_messages(bullet: str, role: str, seniority: str, style: str, tone: str, keep_metrics: bool, n: int):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(bullet, role, seniority, style, tone, keep_metrics, n)},
    ]

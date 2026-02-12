import argparse
import json
import os
import textwrap
from pathlib import Path
from typing import List

from resume_bullet_rewriter.prompts import build_messages
from resume_bullet_rewriter.schema import BulletFeedback, validate_feedback
from resume_bullet_rewriter.utils import (
    anonymize_sensitive,
    contains_banned_word,
    detect_tech_words,
    extract_numbers,
    has_numbers,
    needs_clarifying_questions,
    quick_critique,
    read_bullets_from_file,
    save_json,
)



DEFAULT_MODEL = "llama-3.3-70b-versatile"


def dry_run_suggestions(bullet: str, style: str, tone: str, n: int) -> List[str]:
    # Simpler, focused suggestion templates for quick local use
    templates = [
        "{verb} {what} by {how}",
        "{verb} {what}, improving {impact}",
        "{verb} {what} using {tech}" if detect_tech_words(bullet) else "{verb} {what}",
    ]
    verbs_map = {
        "ats": ["Improved", "Streamlined", "Managed"],
        "impact": ["Reduced", "Increased", "Accelerated"],
        "tech": ["Implemented", "Designed", "Built"],
        "leadership": ["Led", "Mentored", "Aligned"],
        "concise": ["Built", "Ran", "Scaled"],
    }
    verbs = verbs_map.get(style, verbs_map["ats"]) 
    techs = detect_tech_words(bullet)
    what = bullet
    how = "automation and query tuning"
    impact = "throughput or latency"
    suggestions = []
    for i in range(n):
        verb = verbs[i % len(verbs)]
        tpl = templates[i % len(templates)]
        tech = ", ".join(techs) if techs else ""
        s = tpl.format(verb=verb, what=what, how=how, impact=impact, tech=tech).strip()
        s = textwrap.shorten(s, width=140, placeholder="")
        suggestions.append(s)
    return suggestions


def call_groq_api(messages, model, temperature, max_tokens):
    try:
        from groq import Groq
    except Exception as e:
        raise RuntimeError("Groq SDK not installed; install with `pip install groq`") from e
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_tokens,
    )
    # Expect assistant response in resp.choices[0].message.content
    try:
        content = resp.choices[0].message.content
    except Exception as e:
        raise RuntimeError("Unexpected response from Groq API") from e
    return content




def rewrite_bullet(
    bullet: str,
    role: str = "",
    seniority: str = "",
    style: str = "ats",
    tone: str = "neutral",
    keep_metrics: bool = False,
    n: int = 2,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.4,
    max_tokens: int = 700,
    dry_run: bool = False,
) -> "BulletFeedback":
    orig = bullet.strip()
    original_has_numbers = has_numbers(orig)
    sanitized = anonymize_sensitive(orig)
    critique = quick_critique(sanitized)
    clarifying = []
    if needs_clarifying_questions(sanitized):
        clarifying = [
            "What was the measurable outcome (percent/time/dollars)?",
            "What scale or scope did this affect (team/customers/transactions)?",
        ]

    # Decide whether it's good or needs improvement
    banned = contains_banned_word(sanitized)
    verdict = "good" if critique == "concise and specific" and not clarifying and not banned else "needs_improvement"

    suggestions: List[str] = []
    if verdict == "needs_improvement":
        if dry_run:
            suggestions = dry_run_suggestions(sanitized, style, tone, n)
        else:
            # Ask Groq for concise suggestions; fall back to dry-run
            messages = build_messages(sanitized, role, seniority, style, tone, keep_metrics, n)
            try:
                content = call_groq_api(messages, model, temperature, max_tokens)
                # Expect a JSON array of suggestion strings or structured JSON we can parse
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict) and "suggestions" in parsed:
                        suggestions = parsed["suggestions"][:n]
                    elif isinstance(parsed, list):
                        suggestions = parsed[:n]
                except Exception:
                    # try to pull out lines
                    suggestions = [line.strip("\n \t\r- ") for line in content.splitlines() if line.strip()][:n]
                if not suggestions:
                    raise RuntimeError("empty suggestions from API")
            except Exception:
                suggestions = dry_run_suggestions(sanitized, style, tone, n)

    # Enforce keep-metrics / no-invention rules
    if keep_metrics and original_has_numbers:
        orig_nums = extract_numbers(sanitized)
        if not any(any(c.isdigit() for c in s) for s in suggestions):
            # append numbers to the first suggestion deterministically
            if suggestions:
                suggestions[0] = f"{suggestions[0]} ({', '.join(orig_nums)})"
    elif not original_has_numbers:
        import re

        suggestions = [re.sub(r"\d[\d,\.]*", "", s).strip() for s in suggestions]

    # Build feedback object
    from resume_bullet_rewriter.schema import BulletFeedback, validate_feedback

    feedback = (
        "concise and specific"
        if verdict == "good"
        else f"{critique}{'; contains banned words' if banned else ''}"
    )
    fb = BulletFeedback(
        original=sanitized,
        verdict=verdict,
        feedback=feedback,
        clarifying_questions=clarifying,
        suggestions=suggestions,
        metadata={
            "role": role,
            "seniority": seniority,
            "style": style,
            "tone": tone,
            "model": model if not dry_run else "dry-run",
        },
    )
    validate_feedback(fb, n, keep_metrics, original_has_numbers)
    return fb


def format_output(result: "BulletFeedback", fmt: str = "text") -> str:
    # Format the simplified feedback objects for different output modes
    if fmt == "json":
        return json.dumps(result.to_dict(), indent=2)
    elif fmt == "markdown":
        lines = [f"**Original:** {result.original}", "", f"**Verdict:** {result.verdict}", "", f"**Feedback:** {result.feedback}", ""]
        if result.clarifying_questions:
            lines.append("**Clarifying questions:**")
            for q in result.clarifying_questions:
                lines.append(f"- {q}")
            lines.append("")
        if result.suggestions:
            lines.append("**Suggestions:**")
            for s in result.suggestions:
                lines.append(f"- {s}  ")
        return "\n".join(lines)
    else:
        # simple text
        out = [f"Original: {result.original}", f"Verdict: {result.verdict}", f"Feedback: {result.feedback}", ""]
        if result.clarifying_questions:
            out.append("Clarifying questions:")
            for q in result.clarifying_questions:
                out.append(f" - {q}")
            out.append("")
        if result.suggestions:
            out.append("Suggestions:")
            for s in result.suggestions:
                out.append(f" - {s}")
        return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Assess and improve resume bullets; outputs verdict+feedback and suggested improvements")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("bullets", nargs="*", help="One or more bullets as positional arguments")
    group.add_argument("--file", "-f", type=Path, help="File with one bullet per line")

    parser.add_argument("--role", default="", help="Role (e.g., Data Engineer)")
    parser.add_argument("--seniority", default="", help="Seniority (Intern/Junior/Mid/Senior/Staff/Principal)")
    parser.add_argument("--style", choices=["ats", "impact", "tech", "leadership", "concise"], default="ats")
    parser.add_argument("--tone", choices=["neutral", "confident", "bold"], default="neutral")
    parser.add_argument("--keep-metrics", action="store_true", dest="keep_metrics", help="Preserve numbers from original bullets")
    parser.add_argument("--n", type=int, default=2, help="Number of suggested improvements when needed (default 2)")
    parser.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    parser.add_argument("--save", type=Path, default=None, help="optional path to save JSON output")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--max_tokens", type=int, default=700)
    parser.add_argument("--dry-run", action="store_true", help="Run local deterministic suggestions without calling API")

    args = parser.parse_args()

    bullets = []
    if args.file:
        bullets = read_bullets_from_file(args.file)
    elif args.bullet:
        bullets = [args.bullet]
    else:
        parser.error("Provide a bullet or --file")

    results = []
    for b in bullets:
        try:
            res = rewrite_bullet(
                b,
                role=args.role,
                seniority=args.seniority,
                style=args.style,
                tone=args.tone,
                keep_metrics=args.keep_metrics,
                n=args.n,
                model=args.model,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                dry_run=args.dry_run,
            )
        except AssertionError as e:
            print("Validation error:", e)
            continue
        results.append(res)
        out = format_output(res, args.format)
        print(out)

    if args.save:
        # Save list of dicts
        save_json(args.save, [r.to_dict() for r in results])


if __name__ == "__main__":
    main()

import json
import os
from typing import List

from .prompts import build_messages
from .schema import BulletFeedback, validate_feedback
from .utils import (
    anonymize_sensitive,
    contains_banned_word,
    quick_critique,
    has_numbers,
    needs_clarifying_questions,
    extract_numbers,
)


DEFAULT_MODEL = "llama-3.3-70b-versatile"


def dry_run_suggestions(bullet: str) -> List[str]:
    """Generate deterministic suggestions without API calls."""
    import re
    verbs = ["Improved", "Engineered", "Optimized", "Delivered"]
    # Only use numeric impacts if original has numbers (don't invent metrics)
    has_numbers = bool(re.search(r"\d", bullet))
    if has_numbers:
        impacts = ["by 30%", "resulting in better outcomes", "with measurable impact"]
    else:
        impacts = ["resulting in better outcomes", "with measurable impact", "increasing efficiency"]
    
    suggestions = [
        f"{verbs[0]} {bullet.lower()} {impacts[0]}",
        f"{verbs[1]} {bullet.lower()} {impacts[1]}",
        f"{verbs[2]} {bullet.lower()} {impacts[2]}",
    ]
    return suggestions[:2]


def call_groq_api(messages, model, temperature, max_tokens):
    """Call Groq API with messages."""
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
    
    try:
        content = resp.choices[0].message.content
    except Exception as e:
        raise RuntimeError("Unexpected response from Groq API") from e
    return content


def assess_bullet(bullet: str, role: str = "", dry_run: bool = False) -> BulletFeedback:
    """Assess a single bullet and return feedback."""
    orig = bullet.strip()
    sanitized = anonymize_sensitive(orig)
    critique = quick_critique(sanitized)
    
    clarifying = []
    if needs_clarifying_questions(sanitized):
        clarifying = [
            "What was the measurable outcome?",
            "What was the scope/impact?",
        ]
    
    banned = contains_banned_word(sanitized)
    verdict = "good" if critique == "concise and specific" and not clarifying and not banned else "needs_improvement"
    
    suggestions: List[str] = []
    
    if verdict == "needs_improvement":
        if dry_run:
            suggestions = dry_run_suggestions(sanitized)
        else:
            try:
                messages = build_messages(sanitized, role, "", "impact", "neutral", False, 2)
                content = call_groq_api(messages, DEFAULT_MODEL, 0.4, 700)
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict) and "suggestions" in parsed:
                        suggestions = parsed["suggestions"][:2]
                    elif isinstance(parsed, list):
                        suggestions = parsed[:2]
                except Exception:
                    suggestions = [line.strip("\n \t\r- ") for line in content.splitlines() if line.strip()][:2]
                
                if not suggestions:
                    suggestions = dry_run_suggestions(sanitized)
            except Exception:
                suggestions = dry_run_suggestions(sanitized)
    
    feedback = (
        "concise and specific"
        if verdict == "good"
        else critique
    )
    
    fb = BulletFeedback(
        original=sanitized,
        verdict=verdict,
        feedback=feedback,
        clarifying_questions=clarifying,
        suggestions=suggestions,
        metadata={
            "role": role,
            "model": "dry-run" if dry_run else DEFAULT_MODEL,
        },
    )
    
    validate_feedback(fb, 2, False, has_numbers(orig))
    return fb


def format_simple(result: BulletFeedback) -> str:
    """Format output in simple, ChatGPT-like style."""
    lines = []
    lines.append(f"[{result.verdict.upper()}]")
    lines.append(result.feedback)
    
    if result.suggestions:
        lines.append("")
        for i, s in enumerate(result.suggestions, 1):
            lines.append(f"{i}. {s}")
    
    if result.clarifying_questions:
        lines.append("")
        lines.append("Questions to strengthen:")
        for q in result.clarifying_questions:
            lines.append(f"  • {q}")
    
    return "\n".join(lines)


def interactive_mode(role: str = "", dry_run: bool = False):
    """Interactive conversation mode - just type bullets and get feedback."""
    print("\n✨ Bulletly - Resume Bullet Analyzer")
    print("=" * 50)
    if role:
        print(f"Role: {role}")
    if dry_run:
        print("Mode: Offline (--dry-run)")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            bullet = input("Enter a resume bullet: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if bullet.lower() == "quit":
            print("Goodbye!")
            break
        
        if not bullet:
            continue
        
        try:
            result = assess_bullet(bullet, role=role, dry_run=dry_run)
            output = format_simple(result)
            print(output)
            print()
        except Exception as e:
            print(f"Error: {e}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bulletly - Interactive resume bullet analyzer",
        epilog="Just start typing bullets when running in interactive mode!"
    )
    parser.add_argument("--role", default="", help="Your target role (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Run offline without Groq API")
    
    args = parser.parse_args()
    
    interactive_mode(role=args.role, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

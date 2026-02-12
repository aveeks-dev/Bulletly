# resume-bullet-rewriter

A small CLI tool that rewrites resume bullets into multiple strong variants while preserving truth and avoiding invention.

## Features

- Rewrite a single bullet or a file of bullets into multiple variants
- Optional dry-run (fully local) for testing without an API key
- Preserves metrics when requested; never invents numbers
- Adds quick critique, clarifying questions (if needed), and best-pick ranking

## Setup

1. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Set your API key (or use `--dry-run` for local testing):

```bash
export GROQ_API_KEY=your_key_here
# or copy .env.example to .env and edit
```

## Usage

Single bullet:

```bash
python -m resume_bullet_rewriter "Built data pipeline to ingest logs" \
  --role "Data Engineer" \
  --seniority "Senior" \
  --style "ats" \
  --tone "confident" \
  --keep-metrics \
  --n 6 \
  --format markdown
```

File mode (one bullet per line):

```bash
python -m resume_bullet_rewriter --file bullets.txt --role "Data Engineer" --dry-run
```

## Styles

- ats: clear, keyword-friendly; concise and scan-friendly
- impact: emphasizes outcomes and business impact
- tech: highlights technical approach and tools
- leadership: focuses on influence, mentorship, and strategy
- concise: short, punchy bullets

## Notes

- The tool aims to be truthful: it will not invent numbers or claims. Use `--keep-metrics` to preserve numbers exactly (if present); otherwise numbers will not be added.
- Use `--dry-run` to test locally without an API key. This uses deterministic templates.

## Quick usage (focused)

Now the CLI focuses on assessing bullets and offering improvements.

Examples:

```bash
# Assess one or more bullets (positional args) — default 2 suggestions when needed
python -m resume_bullet_rewriter "Built ETL pipeline to ingest logs" "Led migration of legacy ETL" --dry-run --style impact --tone confident --n 2 --format json

# File mode (one bullet per line):
python -m resume_bullet_rewriter --file bullets.txt --dry-run --n 2 --format json --save out.json
```

The output for each bullet includes:
- `verdict`: `good` or `needs_improvement`
- `feedback`: short notes on strengths/weaknesses
- `clarifying_questions`: when the bullet is too vague
- `suggestions`: suggested rewrites (when `needs_improvement`)

Note: The built-in demo was removed to simplify the repo; run the CLI with `--dry-run` for local deterministic suggestions.
---

(Implementation and tests are included in the `src/` and `tests/` folders.)

## Running tests

Install test requirements and run pytest:

```bash
pip install pytest
python -m pytest -q
```

Notes: The CLI supports `--dry-run` for offline testing; API usage requires `GROQ_API_KEY` to be set.

## Continuous Integration ✅

A GitHub Actions workflow is included at `.github/workflows/ci.yml` which runs the test suite on Python 3.10–3.12 for pushes and pull requests.

## Installing from source / pip

You can install locally with pip:

```bash
pip install -e .
# then run with script name
resume-bullet-rewriter "Built something" --dry-run
```

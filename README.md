# Bulletly

A CLI tool for analyzing and improving resume bullets. Bulletly evaluates your bullets for impact, clarity, and ATS optimization, then generates alternative versions tailored to different roles and writing styles.

## Features

- **Bullet Assessment**: Get immediate feedback on strength and areas for improvement
- **Multi-format Generation**: Generate variants optimized for ATS, impact, technical depth, or leadership focus
- **Metric Preservation**: Maintains existing metrics and never invents claims
- **Flexible I/O**: Process single bullets, files, or batch operations with JSON output support
- **Local Mode**: Run `--dry-run` for deterministic suggestions without API calls

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your API key:

```bash
export GROQ_API_KEY=<your-key>
# or copy .env.example to .env
```

## Quick Start

Single bullet:

```bash
python -m resume_bullet_rewriter "Built ETL pipeline to process 2M+ daily events" \
  --role "Data Engineer" \
  --style impact \
  --n 3 \
  --format json
```

Batch processing from file:

```bash
python -m resume_bullet_rewriter --file bullets.txt --role "Senior Engineer" --format json --save output.json
```

Local mode (no API key required):

```bash
python -m resume_bullet_rewriter "Led platform migration" --dry-run --style impact
```

## Output Format

Each bullet generates:

```json
{
  "verdict": "good|needs_improvement",
  "feedback": "strengths and areas for improvement",
  "clarifying_questions": ["optional questions if vague"],
  "suggestions": ["rewrite 1", "rewrite 2", "..."]
}
```

## Styles

- **ats**: ATS-friendly, keyword-optimized for scanning
- **impact**: Results-focused, emphasizes business outcomes
- **tech**: Technical depth, highlights tools and systems
- **leadership**: Influence and scope, mentorship and strategy
- **concise**: Short, punchy, executive summary style

## Development

Run tests:

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

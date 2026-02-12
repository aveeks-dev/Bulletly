# Bulletly

A CLI tool for analyzing and improving resume bullets. Bulletly evaluates your bullets for impact and clarity, then generates better alternatives. Powered by [Groq AI](https://groq.com/).

## Features

- **Instant Assessment**: Get immediate feedback on bullet strength
- **Smart Suggestions**: Groq-powered rewrites that preserve truth and metrics
- **Interactive Mode**: Simple conversation-style interface—just type bullets and get results
- **No Hallucinations**: Never invents metrics or false claims
- **Local Testing**: `--dry-run` mode for offline testing without an API key

## Quick Start

Just run the tool and start entering bullets:

```bash
python -m resume_bullet_rewriter
```

Then paste bullets one at a time and get instant feedback:

```
Enter a resume bullet (or 'quit' to exit): Built ETL pipeline to process 10M records
[Rating] needs_improvement
[Feedback] Lacks outcome impact
[Suggestions]
- Reduced data processing time by 40% with optimized ETL pipeline
- Architected scalable ETL system handling 10M+ daily records with 99.9% uptime

Enter a resume bullet (or 'quit' to exit): Led team of 5 engineers
[Rating] good
[Feedback] Clear scope and impact
[Done!]
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your Groq API key:

```bash
export GROQ_API_KEY=<your-key>
```

Get a free API key at [console.groq.com](https://console.groq.com)

## Options

```
--dry-run      Test locally without API key (deterministic suggestions)
--role         Optional: your target role (e.g., "Data Engineer")
```

## Examples

With a specific role:

```bash
python -m resume_bullet_rewriter --role "Senior Engineer"
```

Offline testing:

```bash
python -m resume_bullet_rewriter --dry-run
```

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
# Updated Wed Feb 11 23:11:17 EST 2026

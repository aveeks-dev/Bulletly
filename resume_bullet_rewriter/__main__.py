"""Module entrypoint when installed/used in-source.
Loads the implementation from `src/resume_bullet_rewriter/main.py` and runs `main()`.
"""
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMPL = ROOT / "src" / "resume_bullet_rewriter" / "main.py"

if not IMPL.exists():
    print("Could not find implementation at src/resume_bullet_rewriter/main.py")
    raise SystemExit(1)

# Ensure src/ is on sys.path so absolute imports inside the implementation work
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Import the implementation package from src (temporarily remove current wrapper to avoid circular import)
saved = sys.modules.pop("resume_bullet_rewriter", None)
try:
    impl = importlib.import_module("resume_bullet_rewriter")
    # Make sure the imported package is the implementation in src
    sys.modules["resume_bullet_rewriter"] = impl
    if hasattr(impl, "main"):
        impl.main()
    else:
        print("Implementation does not expose `main()`")
        raise SystemExit(1)
finally:
    # nothing to restore; we've replaced the package entry with the real implementation
    pass

"""Top-level wrapper package.
This wrapper ensures `python -m resume_bullet_rewriter` works by loading the real implementation from `src/` during development.
"""
import sys
import pathlib

# If src/resume_bullet_rewriter exists, add its parent (src) to sys.path so imports resolve to that implementation.
_root = pathlib.Path(__file__).resolve().parents[1]
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# Provide lazy, safe delegators to the real implementation in `src/`.
# This avoids import-time circularity and keeps `python -m resume_bullet_rewriter` working.
import importlib


def _get_impl():
    import sys as _sys
    import pathlib as _pathlib
    import importlib.util as _util

    _root = _pathlib.Path(__file__).resolve().parents[1]
    pkg_dir = _root / "src" / "resume_bullet_rewriter"
    init_py = pkg_dir / "__init__.py"
    if not init_py.exists():
        raise ImportError("Could not find implementation package in src/")
    # If already loaded return it
    if "_rbr_impl" in _sys.modules:
        return _sys.modules["_rbr_impl"]
    # Create a module spec for the package and set its search path so imports work
    spec = _util.spec_from_file_location("resume_bullet_rewriter", str(init_py))
    spec.submodule_search_locations = [str(pkg_dir)]
    module = _util.module_from_spec(spec)
    # Insert into sys.modules under the real package name so absolute imports resolve
    _sys.modules["resume_bullet_rewriter"] = module
    _sys.modules["_rbr_impl"] = module
    spec.loader.exec_module(module)
    return module


def rewrite_bullet(*args, **kwargs):
    impl = _get_impl()
    return impl.rewrite_bullet(*args, **kwargs)


def main(*args, **kwargs):
    impl = _get_impl()
    return impl.main(*args, **kwargs)

__all__ = ["rewrite_bullet", "main"]

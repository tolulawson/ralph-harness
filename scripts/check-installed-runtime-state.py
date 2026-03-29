#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from runtime_state_helpers import resolve_canonical_checkout_root, validate_installed_runtime


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an installed Ralph runtime for drift and mixed-version state.")
    parser.add_argument("--repo", default=".", help="Repository root to validate.")
    args = parser.parse_args()

    repo_root = resolve_canonical_checkout_root(Path(args.repo).resolve())
    issues = validate_installed_runtime(repo_root)
    if issues:
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("check-installed-runtime-state: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

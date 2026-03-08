#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from runtime_state_helpers import RuntimeStateError, migrate_repo_state, validate_installed_runtime


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate an installed Ralph runtime to the current interrupt-safe state shape.")
    parser.add_argument("--repo", default=".", help="Repository root to migrate.")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    try:
        migrate_repo_state(repo_root)
    except RuntimeStateError as exc:
        print(f"migrate-installed-runtime: {exc}")
        print("migrate-installed-runtime: stop and repair the ambiguous spec state before retrying.")
        return 1

    issues = validate_installed_runtime(repo_root)
    if issues:
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("migrate-installed-runtime: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

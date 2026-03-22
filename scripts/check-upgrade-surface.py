#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from runtime_state_helpers import validate_upgrade_preflight


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether the installed Ralph upgrade surface is safe to refresh before scaffold-owned files are overwritten."
    )
    parser.add_argument("--repo", default=".", help="Repository root to inspect.")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    issues = validate_upgrade_preflight(repo_root)
    if issues:
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("check-upgrade-surface: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

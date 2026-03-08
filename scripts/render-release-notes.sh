#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TAG_NAME="${1:-}"

if [[ -z "$TAG_NAME" ]]; then
  echo "render-release-notes: expected a tag argument like v0.4.0" >&2
  exit 1
fi

[[ -f CHANGELOG.md ]] || {
  echo "render-release-notes: missing CHANGELOG.md" >&2
  exit 1
}

python3 - "$TAG_NAME" <<'PY'
from pathlib import Path
import re
import sys

tag = sys.argv[1]
text = Path("CHANGELOG.md").read_text()

pattern = re.compile(rf"^## {re.escape(tag)}(?:\s+-\s+.*)?$", re.MULTILINE)
match = pattern.search(text)
if not match:
    raise SystemExit(f"render-release-notes: missing changelog section for {tag}")

start = match.end()
next_heading = re.search(r"^## ", text[start:], re.MULTILINE)
end = start + next_heading.start() if next_heading else len(text)
section = text[start:end].strip()

if not section:
    raise SystemExit(f"render-release-notes: changelog section for {tag} is empty")

print(section)
PY

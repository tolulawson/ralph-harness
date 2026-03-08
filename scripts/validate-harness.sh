#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 - <<'PY'
import json
import pathlib
import sys

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    from pip._vendor import tomli as tomllib  # type: ignore

root = pathlib.Path(".")

toml_paths = [
    root / ".codex/config.toml",
    *sorted((root / "agents").glob("*.toml")),
    root / "src/.codex/config.toml",
    *sorted((root / "src/agents").glob("*.toml")),
]

json_paths = [
    *sorted((root / ".ralph").rglob("*.json")),
    *sorted((root / "src/.ralph").rglob("*.json")),
]

jsonl_paths = [
    *sorted((root / ".ralph").rglob("*.jsonl")),
    *sorted((root / "src/.ralph").rglob("*.jsonl")),
]

for path in toml_paths:
    tomllib.loads(path.read_text())

for path in json_paths:
    json.loads(path.read_text())

for path in jsonl_paths:
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if line.strip():
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: {exc}") from exc

src_config = tomllib.loads((root / "src/.codex/config.toml").read_text())
if not src_config.get("features", {}).get("multi_agent"):
    raise SystemExit("src/.codex/config.toml must enable multi_agent")

current_version = (root / "VERSION").read_text().strip()
current_tag = f"v{current_version}"

changelog_path = root / "CHANGELOG.md"
if not changelog_path.exists():
    raise SystemExit("CHANGELOG.md must exist")

changelog_text = changelog_path.read_text()
if f"## {current_tag}" not in changelog_text:
    raise SystemExit(f"CHANGELOG.md must contain a section for {current_tag}")

for path in [root / "README.md", root / "INSTALLATION.md", root / "UPGRADING.md"]:
    if current_tag not in path.read_text():
        raise SystemExit(f"{path} must reference current tag {current_tag}")
PY

scripts/render-release-notes.sh "v$(tr -d '[:space:]' < VERSION)" >/dev/null
scripts/verify-installation-contract.sh
scripts/verify-interruption-contract.sh
scripts/verify-upgrade-contract.sh

if grep -Fq -- '--generate-notes' .github/workflows/release.yml; then
  echo "validate-harness: release workflow must not use --generate-notes" >&2
  exit 1
fi

if ! grep -Fq -- 'scripts/render-release-notes.sh' .github/workflows/release.yml; then
  echo "validate-harness: release workflow must render notes from CHANGELOG.md" >&2
  exit 1
fi

scripts/smoke-test-install-upgrade.sh

echo "validate-harness: ok"

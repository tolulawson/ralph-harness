#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import timedelta
from pathlib import Path

from runtime_state_helpers import (
    CLAIM_STATUSES,
    CURRENT_LEASE_SCHEMA_VERSION,
    CURRENT_WORKER_CLAIMS_SCHEMA_VERSION,
    DEFAULT_INTENTS_PATH,
    DEFAULT_LEASE_PATH,
    DEFAULT_WORKER_CLAIMS_PATH,
    INTENT_TYPES,
    LEASE_LOCK_SUFFIX,
    LEASE_TTL_SECONDS,
    ensure_intent_log,
    ensure_lease_file,
    ensure_spec_worktree,
    ensure_worker_claims_file,
    load_json,
    load_jsonl_records,
    parse_timestamp,
    worker_claim_is_healthy,
    utc_now,
    write_json,
    write_jsonl_records,
)


def load_workflow(repo_root: Path) -> dict:
    return load_json(repo_root / ".ralph/state/workflow-state.json")


def acquire_lock(lock_path: Path) -> int:
    return os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)


def release_lock(fd: int, lock_path: Path) -> None:
    os.close(fd)
    lock_path.unlink(missing_ok=True)


def lease_cmd(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    workflow = load_workflow(repo_root)
    lease = ensure_lease_file(repo_root, workflow)
    lease_path = repo_root / (workflow.get("orchestrator_lease_path") or DEFAULT_LEASE_PATH)
    lock_path = lease_path.with_name(lease_path.name + LEASE_LOCK_SUFFIX)

    if args.action == "status":
        print(json.dumps(lease, indent=2))
        return 0

    try:
        fd = acquire_lock(lock_path)
    except FileExistsError:
        print("orchestrator-coordination: lease lock is busy")
        return 1

    try:
        lease = load_json(lease_path)
        now = utc_now()
        expires_at = parse_timestamp(lease.get("expires_at"))
        is_expired = expires_at is None or expires_at <= now

        if args.action == "acquire":
            if lease.get("owner_token") and lease.get("owner_token") != args.owner_token and not is_expired:
                print("orchestrator-coordination: lease is already held by another owner")
                return 1
            lease.update(
                {
                    "schema_version": CURRENT_LEASE_SCHEMA_VERSION,
                    "owner_token": args.owner_token,
                    "holder_thread": args.holder_thread,
                    "run_id": args.run_id,
                    "acquired_at": now.isoformat(),
                    "heartbeat_at": now.isoformat(),
                    "expires_at": (now + timedelta(seconds=args.ttl_seconds)).isoformat(),
                    "status": "held",
                }
            )
        elif args.action == "heartbeat":
            if lease.get("owner_token") != args.owner_token:
                print("orchestrator-coordination: cannot heartbeat a lease you do not hold")
                return 1
            lease["heartbeat_at"] = now.isoformat()
            lease["expires_at"] = (now + timedelta(seconds=args.ttl_seconds)).isoformat()
            lease["status"] = "held"
        elif args.action == "release":
            if lease.get("owner_token") != args.owner_token:
                print("orchestrator-coordination: cannot release a lease you do not hold")
                return 1
            lease.update(
                {
                    "owner_token": None,
                    "holder_thread": None,
                    "run_id": None,
                    "acquired_at": None,
                    "heartbeat_at": None,
                    "expires_at": None,
                    "status": "idle",
                }
            )

        write_json(lease_path, lease)
        print(json.dumps(lease, indent=2))
        return 0
    finally:
        release_lock(fd, lock_path)


def intent_cmd(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    workflow = load_workflow(repo_root)
    intents_path = ensure_intent_log(repo_root, workflow)
    intents = load_jsonl_records(intents_path)

    if args.action == "list":
        print(json.dumps(intents, indent=2))
        return 0

    if args.intent_type not in INTENT_TYPES:
        print(f"orchestrator-coordination: unsupported intent type `{args.intent_type}`")
        return 1

    payload = None
    if args.spec_payload_json:
        payload = json.loads(args.spec_payload_json)

    record = {
        "schema_version": "1.0.0",
        "intent_id": args.intent_id,
        "created_at": utc_now().isoformat(),
        "requested_by": args.requested_by,
        "type": args.intent_type,
        "status": "pending",
        "target_spec_id": args.target_spec_id,
        "spec_payload": payload,
        "dependency_hints": args.dependency_hint or [],
        "priority_note": args.priority_note,
        "admission_note": args.admission_note,
    }
    intents.append(record)
    write_jsonl_records(intents_path, intents)
    print(json.dumps(record, indent=2))
    return 0


def worktree_cmd(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    queue = load_json(repo_root / ".ralph/state/spec-queue.json")
    spec = next((entry for entry in queue.get("specs", []) if entry.get("spec_id") == args.spec_id or entry.get("spec_key") == args.spec_id), None)
    if spec is None:
        print(f"orchestrator-coordination: spec `{args.spec_id}` not found")
        return 1
    worktree_path = ensure_spec_worktree(repo_root, spec)
    print(worktree_path)
    return 0


def claim_cmd(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo).resolve()
    workflow = load_workflow(repo_root)
    claims_path = ensure_worker_claims_file(repo_root, workflow)
    payload = load_json(claims_path)
    claims = list(payload.get("claims") or [])

    if args.action == "list":
        print(json.dumps(payload, indent=2))
        return 0

    now = utc_now()

    if args.action == "acquire":
        queue = load_json(repo_root / ".ralph/state/spec-queue.json")
        spec = next(
            (entry for entry in queue.get("specs", []) if entry.get("spec_id") == args.spec_id or entry.get("spec_key") == args.spec_id),
            None,
        )
        if spec is None:
            print(f"orchestrator-coordination: spec `{args.spec_id}` not found")
            return 1

        for claim in claims:
            if claim.get("spec_id") != spec.get("spec_id") or claim.get("role") != args.role:
                continue
            if claim.get("holder") == args.holder and claim.get("status") == "claimed":
                claim["heartbeat_at"] = now.isoformat()
                claim["expires_at"] = (now + timedelta(seconds=args.ttl_seconds)).isoformat()
                write_json(claims_path, {"schema_version": CURRENT_WORKER_CLAIMS_SCHEMA_VERSION, "claims": claims})
                print(json.dumps(claim, indent=2))
                return 0
            if worker_claim_is_healthy(claim, now):
                print("orchestrator-coordination: claim is already held by another runtime session")
                return 1

        claim_record = {
            "claim_id": args.claim_id or f"{spec['spec_id']}:{args.role}",
            "spec_id": spec["spec_id"],
            "spec_key": spec["spec_key"],
            "task_id": args.task_id,
            "role": args.role,
            "runtime": args.runtime,
            "session_id": args.session_id,
            "thread_id": args.thread_id,
            "holder": args.holder,
            "execution_mode": args.execution_mode,
            "worktree_path": spec.get("worktree_path"),
            "status": "claimed",
            "claimed_at": now.isoformat(),
            "heartbeat_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=args.ttl_seconds)).isoformat(),
        }
        claims.append(claim_record)
        write_json(claims_path, {"schema_version": CURRENT_WORKER_CLAIMS_SCHEMA_VERSION, "claims": claims})
        print(json.dumps(claim_record, indent=2))
        return 0

    target = next((claim for claim in claims if claim.get("claim_id") == args.claim_id), None)
    if target is None:
        print(f"orchestrator-coordination: claim `{args.claim_id}` not found")
        return 1

    if target.get("holder") != args.holder:
        print("orchestrator-coordination: cannot mutate a claim held by another runtime session")
        return 1

    if args.action == "heartbeat":
        target["heartbeat_at"] = now.isoformat()
        target["expires_at"] = (now + timedelta(seconds=args.ttl_seconds)).isoformat()
        target["status"] = "claimed"
    elif args.action == "release":
        target["heartbeat_at"] = now.isoformat()
        target["expires_at"] = now.isoformat()
        target["status"] = "released"
    else:
        print(f"orchestrator-coordination: unsupported claim action `{args.action}`")
        return 1

    write_json(claims_path, {"schema_version": CURRENT_WORKER_CLAIMS_SCHEMA_VERSION, "claims": claims})
    print(json.dumps(target, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Ralph orchestrator lease, durable intents, and per-spec worktrees.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lease = subparsers.add_parser("lease")
    lease.add_argument("action", choices=("acquire", "heartbeat", "release", "status"))
    lease.add_argument("--repo", default=".")
    lease.add_argument("--owner-token")
    lease.add_argument("--holder-thread")
    lease.add_argument("--run-id")
    lease.add_argument("--ttl-seconds", type=int, default=LEASE_TTL_SECONDS)
    lease.set_defaults(handler=lease_cmd)

    intent = subparsers.add_parser("intent")
    intent.add_argument("action", choices=("append", "list"))
    intent.add_argument("--repo", default=".")
    intent.add_argument("--intent-id")
    intent.add_argument("--requested-by")
    intent.add_argument("--intent-type")
    intent.add_argument("--target-spec-id")
    intent.add_argument("--spec-payload-json")
    intent.add_argument("--dependency-hint", action="append")
    intent.add_argument("--priority-note")
    intent.add_argument("--admission-note")
    intent.set_defaults(handler=intent_cmd)

    worktree = subparsers.add_parser("worktree")
    worktree.add_argument("spec_id")
    worktree.add_argument("--repo", default=".")
    worktree.set_defaults(handler=worktree_cmd)

    claim = subparsers.add_parser("claim")
    claim.add_argument("action", choices=("acquire", "heartbeat", "release", "list"))
    claim.add_argument("--repo", default=".")
    claim.add_argument("--claim-id")
    claim.add_argument("--spec-id")
    claim.add_argument("--task-id")
    claim.add_argument("--role")
    claim.add_argument("--runtime")
    claim.add_argument("--session-id")
    claim.add_argument("--thread-id")
    claim.add_argument("--holder")
    claim.add_argument("--execution-mode", default="interactive_session")
    claim.add_argument("--ttl-seconds", type=int, default=LEASE_TTL_SECONDS)
    claim.set_defaults(handler=claim_cmd)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

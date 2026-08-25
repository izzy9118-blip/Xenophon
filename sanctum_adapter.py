#!/usr/bin/env python3
"""Sanctum universal adapter boundary for the owner-certified Xenophon pin.

This overlay adds only the generic Sanctum transport to the previously certified
multi-work minister state. It preserves adapter.py and all source-line rules.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

import adapter

PROTOCOL = "sanctum.adapter.v1"
REPOSITORY = "izzy9118-blip/Xenophon"
MINISTER_ID = "xenophon"


class SanctumAdapterError(RuntimeError):
    pass


def _head() -> str:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=adapter.ROOT, capture_output=True, text=True, check=False)
    value = proc.stdout.strip()
    if proc.returncode != 0 or len(value) != 40:
        raise SanctumAdapterError("cannot resolve exact Xenophon repository commit")
    return value


def _read_stdin_object() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SanctumAdapterError(f"stdin must contain one JSON object: {exc}") from exc
    if not isinstance(value, dict):
        raise SanctumAdapterError("stdin must contain one JSON object")
    return value


def describe() -> dict[str, Any]:
    manifest = adapter.load_yaml(adapter.MANIFEST_PATH)
    return {
        "record_type": "sanctum_adapter_descriptor",
        "protocol": PROTOCOL,
        "minister_id": MINISTER_ID,
        "repository": REPOSITORY,
        "repository_commit": _head(),
        "manifest_path": "manifest.yaml",
        "manifest_version": str(manifest.get("version", "UNRECORDED")),
        "commands": ["describe", "validate-interface", "prepare-request", "validate-report"],
        "capabilities": ["reasoned", "outside_my_ground", "minister_local_context", "minister_local_report_validation"],
        "authority": "OWNER_AUTHORIZED_ADAPTER_OVERLAY_NO_DOCTRINAL_CHANGE",
    }


def validate_interface() -> dict[str, Any]:
    manifest = adapter.load_yaml(adapter.MANIFEST_PATH)
    mechanism = adapter.load_yaml(adapter.MECHANISM_PATH)
    errors = adapter.validate_manifest(manifest) + adapter.validate_mechanism(mechanism)
    if errors:
        raise SanctumAdapterError("; ".join(errors))
    return {
        "record_type": "sanctum_adapter_validation",
        "protocol": PROTOCOL,
        "minister_id": MINISTER_ID,
        "repository_commit": _head(),
        "status": "VALIDATED_INTERFACE_NOT_TRUTH_CERTIFIED",
    }


def prepare_request(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("record_type") != "sanctum_adapter_request":
        raise SanctumAdapterError("record_type must be sanctum_adapter_request")
    if request.get("protocol") != PROTOCOL:
        raise SanctumAdapterError(f"protocol must be {PROTOCOL}")
    if request.get("minister_id") != MINISTER_ID:
        raise SanctumAdapterError("minister_id mismatch")
    pin = request.get("repository_pin")
    if not isinstance(pin, dict) or pin.get("repository") != REPOSITORY:
        raise SanctumAdapterError("repository_pin.repository mismatch")
    head = _head()
    if pin.get("commit") != head:
        raise SanctumAdapterError("repository_pin.commit does not match this exact checkout")
    question = request.get("question")
    if not isinstance(question, str) or not question.strip():
        raise SanctumAdapterError("question must be a non-empty string")
    briefing = request.get("common_briefing")
    if not isinstance(briefing, dict) or not briefing.get("sha256"):
        raise SanctumAdapterError("common_briefing with sha256 is required")
    manifest = adapter.load_yaml(adapter.MANIFEST_PATH)
    mechanism = adapter.load_yaml(adapter.MECHANISM_PATH)
    source_lines = request.get("source_lines")
    available = list(manifest.get("source_policy", {}).get("operational_source_lines", {}).keys())
    if source_lines is None:
        source_lines = available
    if not isinstance(source_lines, list) or any(item not in available for item in source_lines):
        raise SanctumAdapterError("source_lines contains an unauthorized source line")
    context = {
        "manifest": manifest,
        "speech_mechanism": mechanism,
        "source_lines": source_lines,
        "corpus_index": adapter.load_yaml(adapter.CORPUS_INDEX_PATH),
    }
    return {
        "record_type": "sanctum_adapter_prepared_request",
        "protocol": PROTOCOL,
        "minister_id": MINISTER_ID,
        "repository": REPOSITORY,
        "repository_commit": head,
        "inquiry_id": request.get("inquiry_id"),
        "question": question,
        "common_briefing": briefing,
        "context": context,
        "output_rule": "SUBSTANTIVE_JUDGMENT_MUST_RETURN_THROUGH_MINISTER_LOCAL_VALIDATION",
        "certification": "NONE_SELF_CERTIFICATION_PROHIBITED",
    }


def validate_report(report: dict[str, Any]) -> dict[str, Any]:
    schema = adapter.load_json(adapter.SCHEMA_PATH)
    errors = sorted(adapter.Draft202012Validator(schema).iter_errors(report), key=lambda item: list(item.path))
    if errors:
        raise SanctumAdapterError("; ".join(error.message for error in errors))
    minister = report.get("minister", {})
    if minister.get("actor") != MINISTER_ID:
        raise SanctumAdapterError("report minister.actor mismatch")
    return {
        "record_type": "sanctum_adapter_report_validation",
        "protocol": PROTOCOL,
        "minister_id": MINISTER_ID,
        "repository_commit": _head(),
        "status": "MINISTER_LOCAL_STRUCTURE_VALIDATED_NOT_OWNER_CERTIFIED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["describe", "validate-interface", "prepare-request", "validate-report"])
    args = parser.parse_args(argv)
    try:
        if args.command == "describe":
            result = describe()
        elif args.command == "validate-interface":
            result = validate_interface()
        elif args.command == "prepare-request":
            result = prepare_request(_read_stdin_object())
        else:
            result = validate_report(_read_stdin_object())
    except (SanctumAdapterError, adapter.AdapterError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"SANCTUM ADAPTER ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extract 429 events and Retry-After hints from request logs.

Deterministic evidence collector for Loop 2 (Context Collection). Does not
diagnose — it only surfaces the raw 429 signal so the reasoning loops don't
have to guess.

Usage:
    parse_429_logs.py <logfile> [--json]
    cat access.log | parse_429_logs.py - --json

Accepts either JSON-lines logs (objects with status/timestamp/... fields) or
plain text lines. Emits a summary of 429 timing, Retry-After values, burstiness,
and per-region breakdown.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime

# Matches "429" as a status token and common Retry-After renderings.
STATUS_429 = re.compile(r"\b429\b")
RETRY_AFTER = re.compile(r"retry[-_ ]?after[\"'=:\s]+(\d+)", re.IGNORECASE)
TIMESTAMP = re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)")
REGION = re.compile(r"region[\"'=:\s]+([a-z]{2}-[a-z]+-?\d?)", re.IGNORECASE)


def parse_timestamp(text: str):
    m = TIMESTAMP.search(text)
    if not m:
        return None
    raw = m.group(1).replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def parse_line(line: str):
    """Return a normalized event dict for a 429 line, else None."""
    line = line.strip()
    if not line:
        return None

    status = None
    retry_after = None
    region = None
    ts = None

    # Prefer structured JSON lines when present.
    if line.startswith("{"):
        try:
            obj = json.loads(line)
            status = str(obj.get("status") or obj.get("status_code") or "")
            retry_after = obj.get("retry_after") or obj.get("Retry-After")
            region = obj.get("region") or obj.get("endpoint_region")
            ts = obj.get("timestamp") or obj.get("time") or obj.get("ts")
        except json.JSONDecodeError:
            pass

    if status != "429" and not STATUS_429.search(line):
        return None

    if retry_after is None:
        m = RETRY_AFTER.search(line)
        retry_after = int(m.group(1)) if m else None
    else:
        try:
            retry_after = int(retry_after)
        except (TypeError, ValueError):
            retry_after = None

    if region is None:
        m = REGION.search(line)
        region = m.group(1) if m else None

    dt = parse_timestamp(str(ts) if ts else line)

    return {"timestamp": dt, "retry_after": retry_after, "region": region}


def summarize(events):
    times = sorted(e["timestamp"] for e in events if e["timestamp"])
    retry_afters = [e["retry_after"] for e in events if e["retry_after"] is not None]
    regions = Counter(e["region"] for e in events if e["region"])

    span_seconds = None
    max_per_minute = None
    if times:
        span_seconds = (times[-1] - times[0]).total_seconds()
        per_minute = Counter(t.replace(second=0, microsecond=0) for t in times)
        max_per_minute = max(per_minute.values())

    return {
        "total_429": len(events),
        "first_seen": times[0].isoformat() if times else None,
        "last_seen": times[-1].isoformat() if times else None,
        "span_seconds": span_seconds,
        "peak_429_per_minute": max_per_minute,
        "retry_after": {
            "count": len(retry_afters),
            "min": min(retry_afters) if retry_afters else None,
            "max": max(retry_afters) if retry_afters else None,
            "avg": round(sum(retry_afters) / len(retry_afters), 2) if retry_afters else None,
        },
        "by_region": dict(regions),
        # Heuristic hint only — the diagnosis loop makes the actual call.
        "looks_bursty": bool(
            max_per_minute and span_seconds and span_seconds > 60
            and max_per_minute > 3 * (len(events) / (span_seconds / 60))
        ),
    }


def read_lines(path):
    if path == "-":
        yield from sys.stdin
    else:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            yield from fh


def main(argv=None):
    ap = argparse.ArgumentParser(description="Extract 429 events from logs.")
    ap.add_argument("logfile", help="Path to log file, or '-' for stdin.")
    ap.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = ap.parse_args(argv)

    events = [ev for line in read_lines(args.logfile) if (ev := parse_line(line))]
    summary = summarize(events)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"429 events:        {summary['total_429']}")
        print(f"window:            {summary['first_seen']} .. {summary['last_seen']}")
        print(f"peak 429/min:      {summary['peak_429_per_minute']}")
        ra = summary["retry_after"]
        print(f"Retry-After (s):   min={ra['min']} max={ra['max']} avg={ra['avg']}")
        print(f"by region:         {summary['by_region'] or '(none tagged)'}")
        print(f"looks bursty:      {summary['looks_bursty']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

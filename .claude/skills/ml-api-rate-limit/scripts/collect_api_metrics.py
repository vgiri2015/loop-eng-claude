#!/usr/bin/env python3
"""Collect rate/burst/token metrics for a 429 investigation.

Deterministic evidence collector for Loops 2 and 5. Reads a metrics export
(JSON or CSV of per-request samples) and derives the request-rate, burst-rate,
and token-usage signals the reasoning loops need. It reports what it can measure
and flags the rest as missing — it never invents values.

Usage:
    collect_api_metrics.py <samples.json|samples.csv> [--window 60] [--json]
    cat samples.json | collect_api_metrics.py - --json

Each sample is expected to carry at least a timestamp. Optional fields:
    input_tokens, output_tokens, region, status, retry, concurrency

Comparison mode for verification (Loop 5):
    collect_api_metrics.py after.json --baseline before.json --json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime

REQUIRED = ["request_rate_rpm", "peak_rpm", "tokens_per_minute"]


def parse_ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value)
        except (OverflowError, OSError, ValueError):
            return None
    raw = str(value).replace(" ", "T").replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def load_samples(path):
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    text = text.strip()
    if not text:
        return []
    if text[0] in "[{":
        data = json.loads(text)
        return data if isinstance(data, list) else data.get("samples", [])
    # Fallback: CSV with a header row.
    return list(csv.DictReader(text.splitlines()))


def _int(sample, key):
    try:
        return int(sample.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def compute(samples, window):
    """Derive metrics. Signals we can't measure are returned as None (missing)."""
    times = [t for s in samples if (t := parse_ts(s.get("timestamp") or s.get("ts")))]
    metrics: dict[str, float | None] = {k: None for k in REQUIRED}
    missing = []

    if times:
        times.sort()
        span_min = max((times[-1] - times[0]).total_seconds() / 60.0, 1e-9)
        metrics["request_rate_rpm"] = round(len(times) / span_min, 2)

        per_bucket = Counter(
            int(t.timestamp() // window) for t in times
        )
        # Peak requests in any window, normalized to per-minute.
        metrics["peak_rpm"] = round(max(per_bucket.values()) * (60.0 / window), 2)
    else:
        missing += ["request_rate_rpm", "peak_rpm"]

    token_samples = [
        s for s in samples if s.get("input_tokens") or s.get("output_tokens")
    ]
    if token_samples and times:
        total_tokens = sum(
            _int(s, "input_tokens") + _int(s, "output_tokens") for s in samples
        )
        span_min = max((times[-1] - times[0]).total_seconds() / 60.0, 1e-9)
        metrics["tokens_per_minute"] = round(total_tokens / span_min, 2)
    else:
        missing.append("tokens_per_minute")

    regions = Counter(s.get("region") for s in samples if s.get("region"))
    statuses = Counter(str(s.get("status")) for s in samples if s.get("status"))
    concurrencies = [_int(s, "concurrency") for s in samples if s.get("concurrency")]

    rate = metrics["request_rate_rpm"]
    peak = metrics["peak_rpm"]
    # burst = peak markedly above average sustained rate
    burst_ratio = round(peak / rate, 2) if rate and peak else None

    return {
        "sample_count": len(samples),
        "metrics": metrics,
        "by_region": dict(regions) or None,
        "status_breakdown": dict(statuses) or None,
        "max_concurrency": max(concurrencies) if concurrencies else None,
        "count_429": statuses.get("429", 0),
        "missing_evidence": missing,
        "burst_ratio": burst_ratio,
    }


def compare(before, after):
    def delta(key):
        b = before["metrics"].get(key)
        a = after["metrics"].get(key)
        if b is None or a is None:
            return None
        return round(a - b, 2)

    return {
        "429_delta": after["count_429"] - before["count_429"],
        "429_decreasing": after["count_429"] < before["count_429"],
        "request_rate_delta": delta("request_rate_rpm"),
        "tokens_per_minute_delta": delta("tokens_per_minute"),
        "peak_rpm_delta": delta("peak_rpm"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Collect API rate/token metrics.")
    ap.add_argument("samples", help="Samples file (JSON or CSV), or '-' for stdin.")
    ap.add_argument("--baseline", help="Baseline samples for verification compare.")
    ap.add_argument("--window", type=int, default=60, help="Burst window (seconds).")
    ap.add_argument("--json", action="store_true", help="Emit JSON.")
    args = ap.parse_args(argv)

    current = compute(load_samples(args.samples), args.window)
    result = {"current": current}
    if args.baseline:
        baseline = compute(load_samples(args.baseline), args.window)
        result["baseline"] = baseline
        result["comparison"] = compare(baseline, current)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        m = current["metrics"]
        print(f"samples:           {current['sample_count']}")
        print(f"request rate rpm:  {m['request_rate_rpm']}")
        print(f"peak rpm:          {m['peak_rpm']}  (burst ratio {current['burst_ratio']})")
        print(f"tokens/min:        {m['tokens_per_minute']}")
        print(f"429 count:         {current['count_429']}")
        print(f"by region:         {current['by_region'] or '(none tagged)'}")
        print(f"missing:           {current['missing_evidence'] or '(none)'}")
        if args.baseline:
            print(f"comparison:        {result['comparison']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

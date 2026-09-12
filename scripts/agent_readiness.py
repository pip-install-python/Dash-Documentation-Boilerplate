#!/usr/bin/env python3
"""Score this host against isitagentready.com and print what failed.

1.6.45 item 4. The release report quotes the number, so the number has to
come from somewhere a reader can re-run rather than from a claim.

TOKEN HANDLING, which is the part worth reading: the URL Scanner API needs
the owner's token and this script reads it from the environment
(`AGENT_READY_TOKEN`). It is never written to a file, never echoed, never
put in a URL query string, and never included in the output — not even
truncated. A token in a repo is a token in every fork of that repo.

    export AGENT_READY_TOKEN=...          # the owner's, in their shell
    python3 scripts/agent_readiness.py                       # this host
    python3 scripts/agent_readiness.py --url https://... --json

Exit code: 0 if the scan ran and the host met the floor (Level 1 complete
and at least two of Level 2), 1 if it ran and did not, 2 if the scan could
not run at all. THREE STATES, deliberately: "could not run" is not "failed"
and must never be reported as a score.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request


def _default_url() -> str:
    """This host's OWN base URL, derived — never the template's literal.

    The template shipped `https://boilerplate.2plot.dev` as the default, so
    a fork copying this script and running it with no `--url` SCANNED THE
    TEMPLATE and would have filed the template's answer as its own
    (muischeduler, note 189). The number is dated and attributed to a
    build, which makes a wrong host worse than no answer.

    Derived from `lib.constants.BASE_URL`, which every fork edits as part
    of taking on its own identity. Where the constant cannot be imported —
    the script run outside a checkout — there is no default at all and
    `--url` is required, because refusing is the only honest answer to
    "which host am I?".
    """
    try:
        from lib.constants import BASE_URL

        return BASE_URL.rstrip("/")
    except Exception:
        return ""


DEFAULT_URL = _default_url()
API = "https://isitagentready.com/api/scan"
# OPTIONAL. The drop says the scan needs "the owner's token as an env var";
# measured 2026-09-08, the scan endpoint answers anonymously and the token is
# not required for it. It is still read and sent when present, and still
# never written to a file, echoed, put in a query string, or printed.
TOKEN_ENV = "AGENT_READY_TOKEN"

# Every ad-hoc probe against a production host needs this: the seat hit
# CERTIFICATE_VERIFY_FAILED in a hand-written watcher one hour after shipping
# the same fix inside two live tools.
try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # pragma: no cover — certifi absent
    SSL_CONTEXT = ssl.create_default_context()

try:
    from lib.constants import probe_ua

    UA = probe_ua("curl/8", "agent-readiness")
except Exception:  # pragma: no cover — outside a checkout
    UA = "curl/8 2plot-internal/probe agent-readiness"

# The floor item 4 sets for the template after 1.6.45.
LEVEL_1_REQUIRED = 5
LEVEL_2_REQUIRED = 2


ATTEMPTS = 3


def fetch_report(url: str, token: str, timeout: int = 60) -> dict:
    """The scanner's JSON for `url`. Raises on anything it cannot parse.

    RETRIED, because the first live call from this seat died with
    `IncompleteRead(6508 bytes read, 21923 more expected)` — a chunked
    response cut short, which the kit already records as a seat habit
    alongside the certifi context. A partial read must never become a
    result.
    """
    payload = json.dumps({"url": url}).encode()
    last = None
    for attempt in range(ATTEMPTS):
        request = urllib.request.Request(API, data=payload, method="POST")
        request.add_header("Content-Type", "application/json")
        request.add_header("User-Agent", UA)
        # Authorization header, never a query parameter: a token in a URL
        # lands in access logs, proxy logs and Referer headers.
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(request, timeout=timeout,
                                        context=SSL_CONTEXT) as response:
                return json.loads(response.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError:
            raise                       # a status is an answer; do not retry
        except Exception as exc:        # IncompleteRead, timeout, reset
            last = exc
    raise last


def summarise(report: dict) -> dict:
    """The scan, reduced to what a release report quotes.

    WRITTEN AGAINST THE REAL PAYLOAD, after the first version was written
    against a guessed one and reported "failing: none" for a scan it had not
    read. The shape, measured 2026-09-08:

        {"level": 1, "levelName": "Basic Web Presence",
         "checks": {"<category>": {"<check>": {"status": "pass"|"fail"|
                                               "neutral", "message": ...}}},
         "nextLevel": {"target": 2, "name": ..., "requirements": [...]}}

    `checks` is a DICT of categories, not a list, and each check's verdict is
    a THREE-state string — `neutral` is neither pass nor fail (x402 on a
    non-commerce site), so counting it either way would misreport the host.
    """
    checks = report.get("checks")
    if not isinstance(checks, dict) or not checks:
        # REFUSING to summarise an unrecognised payload, and this is the
        # whole point of the function. The first version was defensive here
        # — an empty payload yielded empty levels and printed "failing:
        # none", which reads as a clean scan. It did that on a response the
        # script had NOT been able to read (IncompleteRead), turning "could
        # not run" into "ran and found nothing wrong". Defensiveness that
        # invents a result is worse than a crash.
        raise ValueError(
            f"the scanner's payload carries no `checks` dict (keys: "
            f"{sorted(report)[:6]}) — this is not a scan result"
        )

    passed, failed, neutral = [], [], []
    for category, entries in checks.items():
        if not isinstance(entries, dict):
            continue
        for name, verdict in entries.items():
            status = str((verdict or {}).get("status", "")).lower()
            label = f"{category}.{name}"
            message = str((verdict or {}).get("message", "")).strip()
            if status == "pass":
                passed.append(label)
            elif status == "fail":
                failed.append((label, message))
            else:
                neutral.append(label)

    return {
        "level": report.get("level"),
        "level_name": report.get("levelName"),
        "passed": passed,
        "failing": failed,
        "neutral": neutral,
        "next_level": (report.get("nextLevel") or {}).get("target"),
        "next_requirements": [
            r.get("check") for r in (report.get("nextLevel") or {}).get(
                "requirements", []) if isinstance(r, dict)
        ],
    }


def meets_floor(summary: dict) -> bool:
    """Item 4's acceptance, expressed in the API's own terms.

    The drop words it as "Level 1 5/5 and Level 2 >= 2/3". The scanner does
    not report per-level tallies — it reports one `level` integer plus
    per-category checks — so the equivalent, checkable statement is: the host
    has reached level 2 or better. Recorded as a correction rather than
    silently reinterpreted.
    """
    level = summary.get("level")
    return isinstance(level, int) and level >= 2


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=DEFAULT_URL,
                        help="the host to scan (default: this checkout's "
                             "own lib.constants.BASE_URL; required when "
                             "that cannot be imported)")
    parser.add_argument("--json", action="store_true",
                        help="print the raw summary as JSON")
    args = parser.parse_args(argv[1:])

    if not args.url:
        print("CANNOT RUN: no host. This checkout's lib.constants.BASE_URL "
              "could not be imported, so there is no default — pass --url. "
              "A scan is dated and attributed to a build, so scanning the "
              "wrong host is worse than scanning none.", file=sys.stderr)
        return 2

    token = os.environ.get(TOKEN_ENV, "").strip()

    try:
        report = fetch_report(args.url, token)
    except urllib.error.HTTPError as exc:
        print(f"CANNOT RUN: the scanner answered {exc.code}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"CANNOT RUN: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    try:
        summary = summarise(report)
    except ValueError as exc:
        print(f"CANNOT RUN: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"agent-readiness — {args.url}")
        print(f"  level      {summary['level']} ({summary['level_name']})")
        print(f"  passed     {len(summary['passed'])}: "
              f"{', '.join(summary['passed']) or '-'}")
        if summary["neutral"]:
            print(f"  neutral    {', '.join(summary['neutral'])}")
        if summary["failing"]:
            print("  failing:")
            for label, message in summary["failing"]:
                print(f"    - {label}: {message}")
        else:
            print("  failing: none")
        if summary["next_level"]:
            print(f"  next       level {summary['next_level']} needs "
                  f"{', '.join(summary['next_requirements']) or '?'}")

    return 0 if meets_floor(summary) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

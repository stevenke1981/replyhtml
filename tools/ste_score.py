"""Score a Markdown reply: percent of prose sentences with no STE linter finding.

Uses the local asd-ste100 skill (parser + agent-profile linter). The score is a
style gate only; it does not certify ASD-STE100 compliance.

Usage:
    python tools/ste_score.py reply.md [--min 90] [--mode description|procedure]
                              [--errors-only] [--json] [--skill DIR]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_SKILL = Path.home() / ".claude" / "skills" / "asd-ste100"
DEFAULT_MIN = 90.0
# The skill linter does not check contractions; STE does not permit them.
CONTRACTION = re.compile(
    r"\b\w+(?:n['’]t|['’](?:ve|re|ll|m|d))\b"
    r"|\b(?:it|that|there|what|here|let|who)['’]s\b", re.I)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", type=Path)
    parser.add_argument("--min", type=float, default=DEFAULT_MIN,
                        help="minimum passing percent (default 90)")
    parser.add_argument("--mode", choices=("description", "procedure"),
                        default="description")
    parser.add_argument("--errors-only", action="store_true",
                        help="count only ERROR findings; ignore CHECK findings")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skill", type=Path,
                        default=Path(os.environ.get("STE_SKILL_DIR", DEFAULT_SKILL)))
    return parser.parse_args(argv)


def sentence_spans(text, skill_dir):
    """Return [(start_pos, end_pos, sentence)] with (line, col) positions."""
    sys.path.insert(0, str(skill_dir / "scripts"))
    from ste_markdown import parse_markdown  # noqa: E402
    from ste_agent import _sentence_spans  # noqa: E402

    spans = []
    for block in parse_markdown(text):
        for start, end in _sentence_spans(block.masked):
            sentence = block.text[start:end]
            if any(ch.isalpha() for ch in sentence):
                spans.append((block.position(start), block.position(end), sentence))
    return spans


def lint_findings(path, mode, skill_dir):
    linter = skill_dir / "scripts" / "ste_lint.py"
    result = subprocess.run(
        [sys.executable, str(linter), str(path), "--profile", "agent",
         "--mode", mode, "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if not result.stdout.strip():
        raise RuntimeError(f"linter failed: {result.stderr.strip()}")
    return json.loads(result.stdout)["findings"]


def score(spans, findings, errors_only):
    relevant = [f for f in findings if not errors_only or f["level"] == "ERROR"]
    flagged = {}
    for finding in relevant:
        pos = (finding["line"], finding["col"])
        for index, (start, end, _) in enumerate(spans):
            if start <= pos <= end:
                flagged.setdefault(index, []).append(finding)
                break
    for index, (_, _, sentence) in enumerate(spans):
        if CONTRACTION.search(sentence):
            flagged.setdefault(index, []).append(
                {"rule": "contraction", "level": "ERROR"})
    total = len(spans)
    passed = total - len(flagged)
    percent = 100.0 if total == 0 else round(100.0 * passed / total, 1)
    return total, passed, percent, flagged


def main(argv=None):
    args = parse_args(argv)
    if not args.file.is_file():
        print(f"File not found: {args.file}", file=sys.stderr)
        return 2
    if not (args.skill / "scripts" / "ste_lint.py").is_file():
        print(f"asd-ste100 skill not found at {args.skill}. Set STE_SKILL_DIR.",
              file=sys.stderr)
        return 2

    text = args.file.read_text(encoding="utf-8")
    spans = sentence_spans(text, args.skill)
    findings = lint_findings(args.file, args.mode, args.skill)
    total, passed, percent, flagged = score(spans, findings, args.errors_only)
    ok = percent >= args.min

    if args.json:
        print(json.dumps({
            "file": str(args.file), "sentences": total, "passed": passed,
            "percent": percent, "min": args.min, "pass": ok,
            "flagged": [{"sentence": spans[i][2],
                         "rules": sorted({f["rule"] for f in fs})}
                        for i, fs in sorted(flagged.items())],
            "compliance_not_verified": True,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"STE score: {percent}% ({passed}/{total} sentences) "
              f"- minimum {args.min}% - {'PASS' if ok else 'FAIL'}")
        for index, items in sorted(flagged.items()):
            rules = ", ".join(sorted({f["rule"] for f in items}))
            print(f"  L{spans[index][0][0]}: [{rules}] {spans[index][2]}")
        print("Note: heuristic style gate. Full ASD-STE100 compliance is not verified.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

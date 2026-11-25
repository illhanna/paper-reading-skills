"""Check paper-reading evidence links and PDF page bounds in a Markdown note."""

import argparse
from pathlib import Path
import re


CATEGORIES = {"原文事实", "作者观点", "AI 推断", "外部资料"}
COVERAGE = {"全文已查阅", "部分全文", "仅摘要", "仅元数据", "不可读"}
HEADER = ["结论 ID", "结论", "来源类别", "证据与定位", "支撑与边界"]
SOURCE = r"[PSE][1-9]\d*"
CLAIM = r"C[1-9]\d*"
PDF_POSITION = re.compile(
    rf"\b({SOURCE})\s+PDF\s+p\.\s*(\d+)(?:\s*[-–—]\s*(\d+))?"
)


def body_lines(note):
    """Ignore YAML, HTML comments, and code examples before inspecting Markdown."""
    front_matter = re.match(r"\A---\s*\n.*?\n---\s*(?:\n|$)", note, re.DOTALL)
    if front_matter:
        note = note[front_matter.end():]
    note = re.sub(r"<!--.*?-->", "", note, flags=re.DOTALL)

    fence = None
    for line in note.splitlines():
        marker = re.match(r"\s*([~]{3,}|[\x60]{3,})", line)
        if marker:
            delimiter = marker.group(1)
            if fence is None:
                fence = delimiter
                continue
            if delimiter.startswith(fence) and not line.strip().strip(fence[0]):
                fence = None
                continue
        if fence is None:
            yield line


def section(lines, heading):
    marker = f"## {heading}"
    for index, line in enumerate(lines):
        if line.strip() == marker:
            content = []
            for following in lines[index + 1:]:
                if re.match(r"^#{1,2}\s", following.strip()):
                    break
                content.append(following)
            return content
    return []


def table_row(line):
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip()[1:-1])]


def check(note, page_counts):
    lines = list(body_lines(note))
    coverage = "\n".join(section(lines, "来源与覆盖"))
    evidence = section(lines, "核心结论与证据")
    source_ids = set(re.findall(rf"\b{SOURCE}\b", coverage))
    errors = []
    claim_ids = set()

    if not source_ids or not any(label in coverage for label in COVERAGE):
        errors.append("Expected source IDs and a coverage status under 来源与覆盖.")

    rows = [
        table_row(line)
        for line in evidence
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if rows:
        if rows[0] != HEADER:
            errors.append("Unexpected evidence table header.")
        if len(rows) < 3:
            errors.append("The evidence table needs at least one conclusion.")
        if len(rows) < 2 or len(rows[1]) != len(HEADER) or not all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]
        ):
            errors.append("Expected a Markdown table separator after the header.")

        for index, row in enumerate(rows[2:], start=1):
            if len(row) != len(HEADER) or not all(row):
                errors.append(f"Evidence row {index} needs five nonempty cells.")
                continue

            claim_id, _, category, locator, _ = row
            if not re.fullmatch(CLAIM, claim_id):
                errors.append(f"Invalid conclusion ID: {claim_id}")
            if claim_id in claim_ids:
                errors.append(f"Duplicate conclusion ID: {claim_id}")
            claim_ids.add(claim_id)
            if category not in CATEGORIES:
                errors.append(f"{claim_id}: unrecognized evidence category: {category}")

            cited = set(re.findall(rf"\b{SOURCE}\b", locator))
            if not cited:
                errors.append(f"{claim_id}: missing source ID in the locator.")
            for source in sorted(cited - source_ids):
                errors.append(f"{claim_id}: undeclared source ID: {source}")
            for source, first, last in PDF_POSITION.findall(locator):
                start, end = int(first), int(last or first)
                if start < 1 or end < start or (source in page_counts and end > page_counts[source]):
                    errors.append(f"{claim_id}: invalid {source} PDF page range {start}–{end}.")
            for match in re.finditer(rf"\b{SOURCE}\s+PDF\b", locator):
                if not PDF_POSITION.match(locator, match.start()):
                    errors.append(f"{claim_id}: use a 1-based locator such as P1 PDF p. 4.")
    elif "无可核对结论" not in "\n".join(evidence):
        errors.append("Expected an evidence table or 无可核对结论 under 核心结论与证据.")

    for target in sorted(set(re.findall(rf"〔({CLAIM})〕", "\n".join(lines))) - claim_ids):
        errors.append(f"Unknown conclusion reference: {target}")
    return errors, len(claim_ids)


def page_count(value):
    match = re.fullmatch(rf"({SOURCE})=([1-9]\d*)", value)
    if not match:
        raise argparse.ArgumentTypeError("expected a source ID and page count, e.g. P1=11")
    return match[1], int(match[2])


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note", type=Path)
    parser.add_argument("--pages", action="append", type=page_count, default=[])
    args = parser.parse_args()
    if len(dict(args.pages)) != len(args.pages):
        parser.error("each PDF source needs at most one --pages argument")
    try:
        errors, count = check(args.note.read_text(encoding="utf-8-sig"), dict(args.pages))
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f"Cannot read note: {exc}\n")
    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"Evidence structure OK ({count} conclusion IDs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

"""Extract local PDF text with 1-based page positions and extraction status."""

import argparse
import json
from pathlib import Path
import sys


def page_entry(number, extract, label=None):
    try:
        content = extract()
    except Exception as exc:
        return {
            "page": number,
            "page_label": label,
            "status": "error",
            "text": "",
            "detail": str(exc) or type(exc).__name__,
        }
    return {
        "page": number,
        "page_label": label,
        "status": "ok" if content.strip() else "no_text",
        "text": content,
    }


def read_with_pymupdf(path):
    import pymupdf

    with pymupdf.open(path, filetype="pdf") as document:
        if document.needs_pass:
            raise ValueError("PDF is password-protected; provide a readable copy.")
        pages = []
        for number, page in enumerate(document, start=1):
            pages.append(page_entry(number, lambda: page.get_text("text"), page.get_label() or None))
        return pages


def read_with_pypdf(path):
    from pypdf import PdfReader

    with path.open("rb") as stream:
        document = PdfReader(stream)
        if document.is_encrypted and not document.decrypt(""):
            raise ValueError("PDF is password-protected; provide a readable copy.")
        return [
            page_entry(number, lambda: page.extract_text() or "")
            for number, page in enumerate(document.pages, start=1)
        ]


def read_pages(path):
    if not path.is_file():
        raise ValueError(f"Local PDF not found: {path}")
    with path.open("rb") as stream:
        if b"%PDF-" not in stream.read(1024):
            raise ValueError("Input does not have a PDF header.")

    failures = []
    for name, read in (("pymupdf", read_with_pymupdf), ("pypdf", read_with_pypdf)):
        try:
            pages = read(path)
            if pages:
                return name, pages, failures
            failures.append(f"{name}: PDF has no pages.")
        except ImportError:
            failures.append(f"{name}: package is unavailable.")
        except Exception as exc:
            failures.append(f"{name}: {exc}")
    raise ValueError(" ".join(failures))


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Local PDF path")
    parser.add_argument("--output", type=Path, help="New UTF-8 JSON file (default: stdout)")
    args = parser.parse_args()
    try:
        backend, pages, fallback = read_pages(args.pdf)
        record = {
            "file": str(args.pdf.resolve()),
            "backend": backend,
            "backend_diagnostics": fallback,
            "page_count": len(pages),
            "pages_needing_review": [
                page["page"] for page in pages if page["status"] != "ok"
            ],
            "pages": pages,
        }
        data = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(data)
        else:
            sys.stdout.buffer.write(data.encode("utf-8"))
    except (OSError, ValueError) as exc:
        print(f"PDF extraction failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

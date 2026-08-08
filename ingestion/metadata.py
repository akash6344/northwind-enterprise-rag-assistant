from pathlib import Path
import re


DATE_RE = re.compile(r"(Effective|Plan Year|Last Updated):\s*([^|\n]+)", re.I)
VERSION_RE = re.compile(r"(Version|Template Version):\s*([0-9.]+)", re.I)
SUPERSEDES_RE = re.compile(r"Supersedes:\s*([^|\n]+)", re.I)


def infer_department(path: Path) -> str:
    try:
        return path.parent.name
    except IndexError:
        return "Unknown"


def infer_document_id(path: Path) -> str:
    return path.stem.lower().replace(" ", "_").replace("-", "_")


def extract_common_metadata(path: Path, text: str) -> dict:
    effective_match = DATE_RE.search(text)
    version_match = VERSION_RE.search(text)
    supersedes_match = SUPERSEDES_RE.search(text)
    title = next((line.strip() for line in text.splitlines() if line.strip()), path.stem)
    is_current = not ("2025" in path.stem and "Pricing" in path.stem)
    return {
        "document_id": infer_document_id(path),
        "source_file": str(path),
        "department": infer_department(path),
        "title": title,
        "document_type": path.suffix.lower().lstrip("."),
        "version": version_match.group(2).strip() if version_match else None,
        "effective_date": effective_match.group(2).strip() if effective_match else None,
        "supersedes": supersedes_match.group(1).strip() if supersedes_match else None,
        "is_current": is_current,
        "access_groups": [infer_department(path)],
    }

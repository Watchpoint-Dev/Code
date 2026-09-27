"""Script bac-à-sable pour explorer une source. Copier avec le dossier.

Usage:
    source ../shared/.venv/bin/activate
    python explore.py
"""
import sys
import pathlib

# rend `shared/` importable
from watchpoint.commun.utils import get, samples_dir, save_text  # noqa: E402

URL = "https://example.com"  # <-- a remplacer


def main() -> None:
    print(f"GET {URL}")
    resp = get(URL)
    print(f"  statut HTTP: {resp.status_code}  ·  {len(resp.text):,} caracteres")

    out = samples_dir(__file__) / "page.html"
    save_text(out, resp.text)
    print("Fait. Ouvre le fichier dans samples/ pour regarder la structure.")


if __name__ == "__main__":
    main()

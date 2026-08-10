"""Utilitaires communs pour le labo data-sourcing.

Import depuis un script de source :

    import sys, pathlib
    sys.path.append(str(next(p for p in pathlib.Path(__file__).resolve().parents if (p/"shared"/"utils.py").exists())/"shared"))
    from utils import get, save_html, save_json, SAMPLES
"""
from __future__ import annotations

import json
import time
import pathlib
import requests

# En-tete de navigateur "poli" pour ne pas etre bloque betement.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
}


def get(url: str, *, params: dict | None = None, pause: float = 1.0, **kwargs) -> requests.Response:
    """GET simple et poli : en-tetes navigateur + petite pause anti-surcharge."""
    resp = requests.get(url, headers={**HEADERS, **kwargs.pop("headers", {})},
                        params=params, timeout=30, **kwargs)
    time.sleep(pause)  # on reste gentil avec le site
    return resp


def samples_dir(script_file: str) -> pathlib.Path:
    """Dossier samples/ a cote du script appelant."""
    d = pathlib.Path(script_file).resolve().parent / "samples"
    d.mkdir(exist_ok=True)
    return d


def save_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print(f"  -> sauvegarde {path.name} ({len(text):,} caracteres)")


def save_json(path: pathlib.Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> sauvegarde {path.name} ({len(data) if hasattr(data,'__len__') else '?'} elements)")

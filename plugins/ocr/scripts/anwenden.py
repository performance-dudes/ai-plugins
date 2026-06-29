#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf"]
# ///
"""
anwenden.py — phase 4 of the OCR flow: apply the reviewed proposal.

Deterministic, traceable, with an undo log. Reads _vorschlag.json (after human
review) and renames/moves the ORIGINAL scans to
<target-root>/<zielordner>/<sprechender_name>.

DEFAULT = dry-run (shows only what would happen). Real moves only with --apply.

Document image scans (JPG/PNG with enough recognized text) are combined into one
searchable PDF — proportions 1:1, invisible auge text layer (see searchbar.py).
Photo scans / keepsakes (little or no recognized text, below MIN_DOC_CHARS) stay
as images (no PDF). Existing PDFs: image-only PDFs get an auge text layer; PDFs
that already have text stay unchanged.

Generic: ships no personal data. The trash folder for ist_muell items defaults to
"_Aussortiert" and is set with --muell-ordner.

Usage:
  uv run anwenden.py <ocr-dir> --src <scan-dir> --ziel-root <target> [--apply] [--copy] [--skip-fotos]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import searchbar

MIN_DOC_CHARS = 20  # less recognized text -> photo/keepsake, stays an image (no PDF)


def _norm(stem: str) -> str:
    """How ocr.py forms the session key: spaces/slashes -> underscore."""
    return re.sub(r"[ /]", "_", stem)


def src_files_for(session: str, src_dir: Path) -> list[Path]:
    """Find the original files of a session (scanner prefix or speaking name).
    Named files carry underscores in the session key instead of spaces -> match
    back through the same normalization (else files with spaces are skipped)."""
    if session.isdigit() and len(session) == 14:
        return sorted(src_dir.glob(f"{session}_*.*"))
    return sorted(p for p in src_dir.iterdir()
                  if p.is_file() and _norm(p.stem) == session)


def meaningful_chars(ocr_dir: Path, session: str) -> int:
    """Real text amount from the already-produced OCR text (skipping page markers /
    placeholders). Basis for the photo-vs-document decision — no re-OCR needed.
    Marker strings match ocr.py's output."""
    p = ocr_dir / f"{session}.txt"
    if not p.exists():
        return 0
    txt = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("--- page") or s == "[auge: no text detected]":
            continue
        txt.append(s)
    return len(" ".join(txt))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ocr_dir", type=Path)
    ap.add_argument("--src", type=Path, required=True, help="folder of the original scans")
    ap.add_argument("--ziel-root", type=Path, required=True, help="target documents root")
    ap.add_argument("--apply", action="store_true", help="execute for real (otherwise dry-run)")
    ap.add_argument("--copy", action="store_true",
                    help="keep originals (copy instead of move) — for staging/review")
    ap.add_argument("--skip-fotos", action="store_true",
                    help="skip pure photo sessions (process documents only)")
    ap.add_argument("--muell-ordner", default="_Aussortiert",
                    help="target folder for ist_muell=true items")
    args = ap.parse_args()

    items = json.loads((args.ocr_dir / "_vorschlag.json").read_text(encoding="utf-8"))
    undo: list[dict] = []
    plan_only = not args.apply
    print(f"{'DRY-RUN' if plan_only else 'APPLY'} · {len(items)} entries\n")

    for r in items:
        session = r["session"]
        srcs = src_files_for(session, args.src)
        if not srcs:
            print(f"  !  {session}: no source files found — skipped")
            continue

        if r.get("ist_muell"):
            ziel = args.ziel_root / args.muell_ordner
            name = session
        else:
            ziel = args.ziel_root / r.get("zielordner", "").strip("/")
            name = r.get("sprechender_name") or session

        all_images = all(s.suffix.lower() in searchbar.IMG_EXTS for s in srcs)
        single_pdf = len(srcs) == 1 and srcs[0].suffix.lower() == ".pdf"
        is_photo = all_images and meaningful_chars(args.ocr_dir, session) < MIN_DOC_CHARS

        if is_photo and args.skip_fotos:
            continue

        if all_images and is_photo:
            # pure photo / keepsake -> stays an image (no PDF)
            if len(srcs) == 1:
                dest = ziel / f"{name}{srcs[0].suffix.lower()}"
                action = f"photo -> {dest}  (stays image)"
            else:
                dest = ziel / name  # subfolder, keep original filenames
                action = f"{len(srcs)} photos -> {dest}/  (stay images)"
        elif all_images:
            dest = ziel / f"{name}.pdf"
            action = f"{len(srcs)} page(s) -> {dest}  (searchable PDF)"
        elif single_pdf:
            dest = ziel / f"{name}.pdf"
            img_only = searchbar.pdf_is_image_only(srcs[0])
            action = f"{srcs[0].name} -> {dest}" + ("  (+ auge text layer)" if img_only else "")
        else:
            dest = ziel / name
            action = f"{len(srcs)} file(s) -> {dest}/"

        print(f"  {'.' if not r.get('ist_muell') else 'x'} {action}")
        if plan_only:
            continue

        ziel.mkdir(parents=True, exist_ok=True)
        mv = shutil.copy2 if args.copy else shutil.move
        if all_images and is_photo:
            if len(srcs) == 1:
                if dest.exists():
                    dest = dest.with_stem(dest.stem + "_2")
                mv(str(srcs[0]), str(dest))
                undo.append({"from": str(srcs[0]), "to": str(dest), "copied": args.copy})
            else:
                dest.mkdir(parents=True, exist_ok=True)
                for s in srcs:
                    d = dest / s.name
                    mv(str(s), str(d))
                    undo.append({"from": str(s), "to": str(d), "copied": args.copy})
        elif all_images:
            if dest.exists():
                dest = dest.with_stem(dest.stem + "_2")
            searchbar.images_to_pdf(srcs, dest)          # builds a new PDF (originals untouched)
            if not args.copy:
                for s in srcs:
                    s.unlink()
            undo.append({"created": str(dest), "from": [str(s) for s in srcs],
                         "kept_originals": args.copy})
        elif single_pdf:
            if dest.exists():
                dest = dest.with_stem(dest.stem + "_2")
            mv(str(srcs[0]), str(dest))
            if img_only:
                searchbar.add_textlayer(dest)
            undo.append({"from": str(srcs[0]), "to": str(dest), "copied": args.copy})
        else:
            dest.mkdir(parents=True, exist_ok=True)
            for s in srcs:
                d = dest / s.name
                mv(str(s), str(d))
                undo.append({"from": str(s), "to": str(d), "copied": args.copy})

    if not plan_only:
        log = args.ocr_dir / "_undo.json"
        log.write_text(json.dumps(undo, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n{len(undo)} operations · undo log: {log}")
    else:
        print("\n(dry-run — nothing changed. Use --apply to execute for real.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

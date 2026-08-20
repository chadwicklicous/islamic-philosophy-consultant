#!/usr/bin/env python3
"""Section-aware splitter for Avicenna's al-Najat (imported by ip_extract.py).

The wikisource text has a TOC + preface, then the body. The body is mostly
giant lines (2000+ chars) with 'فصل' (chapter) markers embedded MID-LINE, and
section markers (القسم الأول/الثاني/الثالث, في المنطق/الطبيعيات/الإلهيات)
that may also appear mid-line.

This module exposes:
  find_body_start(text) -> int   (char index where the real body begins)
  split_body_into_segments(body) -> [(citation, text), ...]
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, 'raw', 'avicenna', 'al_najat.txt')

# Section keyword -> canonical label (checked as substrings in flowing text)
SECTION_KEYWORDS = [
    ('القسم الأول', 'المنطق'),
    ('القسم الثاني', 'الطبيعيات'),
    ('القسم الثالث', 'الإلهيات'),
    ('في المنطق', 'المنطق'),
    ('في الطبيعيات', 'الطبيعيات'),
    ('في الإلهيات', 'الإلهيات'),
]


def find_body_start(text):
    """Find the char index where the real body begins (after TOC + preface)."""
    idxs = [m.start() for m in re.finditer('القسم الأول', text)]
    for i in reversed(idxs):
        if 'في المنطق' in text[i:i+80]:
            return i
    return 0


def split_body_into_segments(body):
    """Split the body into (citation, text) segments at every 'فصل' marker.

    Each segment = a فصل heading + its following body. Section label is derived
    from the running section state (updated as keywords appear in the text).
    """
    # Strip page-break artifacts
    body = re.sub(r'الصفحة\s*:\s*\d+', '', body)
    body = re.sub(r'^\s*\d+\s*$', '', body, flags=re.MULTILINE)

    # Split at each 'فصل' marker, keeping the marker with the following text
    parts = re.split(r'(فصل\s+[^\n]{0,100})', body)

    segments = []
    current_section = 'المنطق'
    current_treatise = None
    current_heading = None
    current_text = []

    def flush():
        nonlocal current_text
        txt = ''.join(current_text).strip()
        if txt and len(txt) > 40:
            cit = f"al-Najat | {current_section}"
            if current_treatise:
                cit += f" | {current_treatise}"
            if current_heading:
                cit += f" | {current_heading}"
            segments.append((cit, txt))
        current_text = []

    for piece in parts:
        if not piece:
            continue
        for kw, label in SECTION_KEYWORDS:
            if kw in piece:
                current_section = label
                break
        tm = re.search(r'المقالة\s+\S+', piece)
        if tm:
            current_treatise = tm.group(0).strip()
        if piece.startswith('فصل') and len(piece) < 120:
            flush()
            current_heading = piece.strip()
            current_text.append(piece)
        else:
            current_text.append(piece)
    flush()
    return segments

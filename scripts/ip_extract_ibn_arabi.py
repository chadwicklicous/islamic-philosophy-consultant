#!/usr/bin/env python3
"""Extract Ibn Arabi's Tarjuman al-Ashwaq (English translation) into segments.

Source: Nicholson's public-domain English translation (archive.org). The Arabic
is OCR-garbled, so we keep the CLEAN ENGLISH BODY and label every segment as a
translation.

The ode markers are page headers that repeat and the poems/commentaries are
interleaved, so robust ode-splitting is fragile. Instead we split the clean
English into paragraph-sized segments, each labeled as the translation.

Citation:  Ibn Arabi | Tarjuman al-Ashwaq (tr. Nicholson) | <section>
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'raw', 'ibn_arabi', 'tarjuman_ashwaq.txt')
TEXT = os.path.join(BASE, 'text', 'ibn_arabi.tsv')

WORK = "Ibn Arabi | Tarjuman al-Ashwaq (tr. Nicholson)"

def clean_english(text):
    """Keep readable English, drop OCR garbage lines and garbled Arabic."""
    lines = text.split('\n')
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        words = re.findall(r'[A-Za-z]{3,}', line)
        # Keep lines with real English content
        if len(words) >= 1 and not re.search(r'[\u0600-\u06FF]{3,}', line):
            out.append(line)
        elif len(words) >= 2:
            out.append(line)
    return '\n'.join(out)

def split_paragraphs(text, max_len=2500):
    """Split clean English into citation-sized segments."""
    # Split on sentence terminators
    parts = re.split(r'(?<=[.?!])\s+', text)
    segments = []
    buf = []
    buf_len = 0
    for p in parts:
        # hard-split oversized parts
        while len(p) > max_len:
            chunk = p[:max_len]
            sp = chunk.rfind(' ')
            if sp > max_len * 0.6:
                chunk = chunk[:sp]
            segments.append(chunk.strip())
            p = p[len(chunk):]
        buf.append(p)
        buf_len += len(p)
        if buf_len >= max_len:
            body = ' '.join(buf).strip()
            if len(body) > 100:
                segments.append(body)
            buf = []
            buf_len = 0
    if buf:
        body = ' '.join(buf).strip()
        if len(body) > 100:
            segments.append(body)
    return segments


def is_clean_english(body):
    """Return True if the segment is mostly readable English (not OCR garbage)."""
    # Count English words vs total words
    words = re.findall(r'[A-Za-z]{2,}', body)
    total = len(re.findall(r'\S+', body))
    if total == 0:
        return False
    # A segment is usable if at least 40% is English words
    return len(words) / total >= 0.4

def main():
    with open(SRC, encoding='utf-8') as f:
        text = f.read()
    # Skip front matter: the real content (odes) begins at the first ode marker
    m = re.search(r'THE\s+TARJUMAN\s+AL-ASHWAQ\s*\(', text)
    if m:
        text = text[m.start():]
    clean = clean_english(text)
    segments = split_paragraphs(clean)
    os.makedirs(os.path.dirname(TEXT), exist_ok=True)
    count = 0
    with open(TEXT, 'w', encoding='utf-8') as f:
        for i, body in enumerate(segments):
            if not is_clean_english(body):
                continue
            cit = f"{WORK} | section {i+1}"
            f.write(f"{cit}\t{body}\n")
            count += 1
    print(f"Extracted {count} clean segments -> {TEXT}")

if __name__ == '__main__':
    main()

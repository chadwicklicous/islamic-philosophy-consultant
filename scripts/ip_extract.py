#!/usr/bin/env python3
"""Extract all Islamic Philosophy raw texts into citation-tagged segments.

Each thinker's raw files are split into CITATION\\tTEXT rows. The citation
identifies the thinker, work, and (where possible) section/chapter.

Output: text/<thinker>.tsv for each thinker.
"""
import os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, 'raw')
TEXT = os.path.join(BASE, 'text')
os.makedirs(TEXT, exist_ok=True)

# ---- Helpers ----

def clean(text):
    """Strip wikisource artifacts and collapse whitespace."""
    text = re.sub(r'<[^>]+>', '', text)
    # Remove template blocks {{...}} (including nested) — replace with space
    while '{{' in text:
        text = re.sub(r'\{\{[^{}]*\}\}', ' ', text)
    # Remove links [[a|b]] -> b, [[a]] -> a
    text = re.sub(r'\[\[[^\]]*?\|([^\]]*?)\]\]', r'\1', text)
    text = re.sub(r'\[\[([^\]]*?)\]\]', r'\1', text)
    # Remove remaining brackets and template markers
    text = text.replace('{{', ' ').replace('}}', ' ')
    text = re.sub(r'\[\[|\]\]', ' ', text)
    # Remove external links [https://... text] -> text
    text = re.sub(r'\[https?://[^\s\]]+\s+([^\]]*?)\]', r'\1', text)
    text = re.sub(r'\[https?://[^\]]*\]', ' ', text)
    # Remove stray angle-bracket link artifacts like '<[[...]]'
    text = re.sub(r'<\[\[[^\]]*\]\]', ' ', text)
    text = re.sub(r'<\[\[', ' ', text)
    # Remove wiki heading markers and bold/italic
    text = re.sub(r'={2,}\s*', ' ', text)   # ==heading==
    text = re.sub(r"'''", '', text)          # bold
    text = re.sub(r"''", '', text)           # italic
    # Remove page artifacts
    text = re.sub(r'الصفحة\s*:\s*\d+', '', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove any remaining stray angle brackets
    text = text.replace('<', ' ').replace('>', ' ')
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_fasl(text, work, max_len=2500):
    """Split Arabic text into segments at 'فصل' markers (mid-line too).

    Splits on 'فصل' as a substring anywhere in the text, then enforces a hard
    max length so no single citation is unwieldy.
    """
    # Split at every 'فصل' occurrence, keeping the marker with the following text
    parts = re.split(r'(فصل\s+[^\s][^\n]{0,100})', text)
    segments = []
    current_heading = None
    current = []
    def flush():
        nonlocal current
        body = ''.join(current).strip()
        if body and len(body) > 40:
            cit = work
            if current_heading:
                cit += f" | {current_heading}"
            segments.append((cit, body))
        current = []
    for piece in parts:
        if not piece:
            continue
        if piece.startswith('فصل') and len(piece) < 120:
            flush()
            current_heading = piece.strip()
            current.append(piece)
        else:
            current.append(piece)
    flush()
    # If segments are too large, re-split them by paragraph
    final = []
    for cit, body in segments:
        if len(body) > max_len:
            final.extend(split_paragraphs(body, cit, max_len=max_len))
        else:
            final.append((cit, body))
    return final


def split_paragraphs(text, work, min_len=80, max_len=2500):
    """Split text into citation-sized segments (max ~2500 chars each).

    Splits on Arabic sentence terminators (، . ؛ ؟ !) and enforces a hard
    max length so no single citation is unwieldy. Keeps segments large enough
    to be meaningful but small enough to be a precise citation.
    """
    # Split on sentence terminators followed by whitespace
    parts = re.split(r'(?<=[،.؛؟!])\s+', text)
    segments = []
    buf = []
    buf_len = 0
    for p in parts:
        # If a single part is huge (no terminators), hard-split it
        while len(p) > max_len:
            # take a chunk up to max_len at a sentence-ish boundary
            chunk = p[:max_len]
            # try to break at a space near the end
            sp = chunk.rfind(' ')
            if sp > max_len * 0.6:
                chunk = chunk[:sp]
            segments.append((work, chunk.strip()))
            p = p[len(chunk):]
        buf.append(p)
        buf_len += len(p)
        if buf_len >= max_len:
            body = ' '.join(buf).strip()
            if len(body) > min_len:
                segments.append((work, body))
            buf = []
            buf_len = 0
    if buf:
        body = ' '.join(buf).strip()
        if len(body) > min_len:
            segments.append((work, body))
    return segments


# ---- Per-thinker extractors ----

def extract_kindi():
    out = []
    files = {
        'first_philosophy': 'في الفلسفة الأولى',
        'de_intellectu': 'رسالة في العقل',
        'on_soul': 'رسالة في النفس',
        'incorporeal_substances': 'رسالة في أنه جواهر لا أجسام',
        'definitions': 'رسالة في حدود الأشياء',
        'on_infinite': 'رسالة في مائية ما لا يمكن أن يكون لا نهاية',
        'on_oneness': 'رسالة في وحدانية الله',
    }
    for slug, work in files.items():
        path = os.path.join(RAW, 'kindi', f"{slug}.txt")
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            text = clean(f.read())
        segs = split_fasl(text, f"al-Kindi | {work}")
        if not segs:
            segs = split_paragraphs(text, f"al-Kindi | {work}")
        out.extend(segs)
    return out


def extract_farabi():
    out = []
    files = {
        'al_jam': 'الجمع بين رأيي الحكيمين',
        'fusus_al_hikam': 'فصوص الحكم',
        'uyun_al_masail': 'عيون المسائل',
        'maani_al_aql': 'معاني العقل',
        'before_philosophy': 'ما ينبغي أن يقدم قبل تعلم الفلسفة',
        'philosophical_questions': 'المسائل الفلسفية',
        'exposition_metaphysics': 'الإبانة عن غرض أرسطو في ما بعد الطبيعة',
        'on_astrology': 'النكت في أحكام النجوم',
    }
    for slug, work in files.items():
        path = os.path.join(RAW, 'farabi', f"{slug}.txt")
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            text = clean(f.read())
        segs = split_fasl(text, f"al-Farabi | {work}")
        if not segs:
            segs = split_paragraphs(text, f"al-Farabi | {work}")
        out.extend(segs)
    return out


def extract_ghazali():
    out = []
    files = {
        'munqidh': 'المنقذ من الضلال',
        'iqtisad': 'الاقتصاد في الاعتقاد',
    }
    for slug, work in files.items():
        path = os.path.join(RAW, 'ghazali', f"{slug}.txt")
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            text = clean(f.read())
        segs = split_fasl(text, f"al-Ghazali | {work}")
        if not segs:
            segs = split_paragraphs(text, f"al-Ghazali | {work}")
        out.extend(segs)
    return out


def extract_averroes():
    out = []
    # Fasl al-Maqal
    path = os.path.join(RAW, 'averroes', 'fasl_al_maqal.txt')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            text = clean(f.read())
        segs = split_fasl(text, "Averroes | فصل المقال")
        if not segs:
            segs = split_paragraphs(text, "Averroes | فصل المقال")
        out.extend(segs)
    # Bidayat al-Mujtahid (full, with book markers)
    path = os.path.join(RAW, 'averroes', 'bidayat_full.txt')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            text = f.read()
        # Split by book markers
        books = re.split(r'=== (بداية المجتهد - كتاب [^=]+) ===', text)
        # books: [pre, book1, text1, book2, text2, ...]
        for i in range(1, len(books), 2):
            book = books[i].strip()
            body = clean(books[i+1]) if i+1 < len(books) else ''
            if body:
                segs = split_fasl(body, f"Averroes | {book}")
                if not segs:
                    segs = split_paragraphs(body, f"Averroes | {book}")
                out.extend(segs)
    return out


def extract_avicenna():
    """Avicenna al-Najat — reuse the dedicated extractor logic."""
    path = os.path.join(RAW, 'avicenna', 'al_najat.txt')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # Reuse the section-aware splitter from ip_extract_avicenna
    import importlib.util
    spec = importlib.util.spec_from_file_location('ip_extract_avicenna',
        os.path.join(BASE, 'ip_extract_avicenna.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    start = mod.find_body_start(text)
    body = text[start:]
    return mod.split_body_into_segments(body)


def main():
    extractors = {
        'kindi': extract_kindi,
        'farabi': extract_farabi,
        'ghazali': extract_ghazali,
        'averroes': extract_averroes,
        'avicenna': extract_avicenna,
    }
    total = 0
    for thinker, fn in extractors.items():
        segs = fn()
        out = os.path.join(TEXT, f"{thinker}.tsv")
        with open(out, 'w', encoding='utf-8') as f:
            for cit, body in segs:
                f.write(f"{cit}\t{body}\n")
        print(f"{thinker}: {len(segs)} segments -> {out}")
        total += len(segs)
    print(f"\nTotal: {total} segments")


if __name__ == '__main__':
    main()

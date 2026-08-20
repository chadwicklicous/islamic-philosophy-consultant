---
name: islamic-philosophy-consultant
description: "Answer questions about the Islamic philosophers (falasifa) from the original Arabic."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [islamic-philosophy, falasifa, avicenna, kindi, farabi, ghazali, averroes, arabic, vector-search]
    category: research
---

# Islamic Philosophy Consultant

Answer questions about the **Islamic philosophers (falāsifa)** — al-Kindi, al-Farabi,
Avicenna (Ibn Sina), al-Ghazali, Averroes (Ibn Rushd), and Ibn Arabi — **from the
original Arabic** (and, for Ibn Arabi, from a clearly-labeled English translation),
with exact citations (thinker + work + section), not from a translation or the model's
recollection.

## When to Use

- User asks about a concept, argument, or doctrine in Islamic philosophy
- User wants a passage located, an Arabic term examined, or a citation verified
- User is studying the falāsifa, the history of philosophy, or the transmission of
  Greek thought into Islam

## The Corpus (already built)

- **Text corpus:** `C:\Users\philo\islamic-philosophy-consultant\scripts\text\` — 5 TSV files, 1,223 entries, each `CITATION\tTEXT`
- **Vector index:** `C:\Users\philo\islamic-philosophy-consultant\scripts\chroma\` — ChromaDB collection `islamic_philosophy_corpus`, bge-m3 (1024-dim, multilingual)
- **Raw sources:** `scripts/raw/` — the clean Arabic texts fetched from ar.wikisource

The corpus covers six thinkers:

| Thinker | Works | Segments |
|---------|-------|----------|
| **al-Kindi** | 7 philosophical epistles (On First Philosophy, De Intellectu, On the Soul, etc.) | 53 |
| **al-Farabi** | Dieterici collection (Al-Jam', Fusus al-Hikam, 'Uyun al-Masa'il, Ma'ani al-'Aql, etc.) | 71 |
| **Avicenna (Ibn Sina)** | *al-Najat* (The Deliverance) — logic, physics, metaphysics | 264 |
| **al-Ghazali** | *al-Munqidh min al-Dalal*, *al-Iqtisad fi al-I'tiqad* | 120 |
| **Averroes (Ibn Rushd)** | *Fasl al-Maqal*, *Bidayat al-Mujtahid* (17 books) | 715 |
| **Ibn Arabi** | *Tarjuman al-Ashwaq* (tr. Nicholson) — **English translation** | 85 |

Each entry carries the thinker + work in its citation, e.g.
`al-Kindi | في الفلسفة الأولى | فصل في ...` or `Averroes | بداية المجتهد - كتاب الطهارة`.

**Note on Ibn Arabi:** the *Tarjuman al-Ashwaq* is included as Nicholson's **English
translation** (the Arabic original is not freely available as clean text). It is
clearly labeled as a translation in every citation (`tr. Nicholson`), so answers
from it are quoted in English, not Arabic.

### Not yet included (deferred)

The **Illuminationist / later thinkers** — Suhrawardi and Mulla Sadra — are
**not** in the corpus because no clean, machine-readable text (Arabic or English)
is freely available (only imperfect OCR of scans or paid editions). Ibn Arabi is
partially covered via the English *Tarjuman al-Ashwaq*; his major works (*Futuhat
al-Makkiyya*, *Fusus al-Hikam*) remain out pending clean editions. These gaps are
flagged so the consultant is honest about coverage rather than silently omitting
them. If clean editions are sourced, they can be added following the same pattern.

## Query Workflow

### 1. Semantic retrieval

```bash
cd /c/Users/philo/islamic-philosophy-consultant/scripts
python ip_index.py --query "<question, in Arabic or English>" --k 5
```

bge-m3 is multilingual, so English queries match Arabic text. Returns the top-k
entries with exact citations. For a broader sweep, use `--k 10`.

### 2. Read the actual text

The query returns the passage text. Read it carefully. If you need the full text,
grep the TSV:

```bash
grep -F "al-Kindi | في الفلسفة الأولى" /c/Users/philo/islamic-philosophy-consultant/scripts/text/kindi.tsv
```

### 3. Answer from the source

- Quote the **original Arabic** passage.
- Give the **exact citation** (e.g. `al-Kindi | في الفلسفة الأولى`, `Averroes | فصل المقال`).
- Explain the passage in the user's language, but anchor every claim in the quoted text.
- Note the original Arabic term where relevant (e.g. *wajib al-wujud* "the Necessary Being",
  *'aql* "intellect", *nafs* "soul").

## Citation format

| Form | Meaning |
|------|---------|
| `al-Kindi \| في الفلسفة الأولى` | al-Kindi, On First Philosophy |
| `al-Farabi \| الجمع بين رأيي الحكيمين` | al-Farabi, The Harmonization of the Two Sages |
| `Avicenna \| al-Najat \| الإلهيات` | Avicenna, The Deliverance, Metaphysics |
| `al-Ghazali \| المنقذ من الضلال` | al-Ghazali, The Deliverance from Error |
| `Averroes \| فصل المقال` | Averroes, The Decisive Treatise |

## Pitfalls

- **Don't answer from memory or from a translation.** Always retrieve and quote the original Arabic. The whole point is citation-grounded answers in the original language.
- **The index build is resumable.** If `ip_index.py` dies partway, re-run it — it resumes from the last indexed count.
- **Ollama must be running** for embeddings (`ollama serve`). Model: `bge-m3` (multilingual — required for Arabic).
- **Long entries** are truncated to 6000 chars before embedding.
- **The Illuminationist thinkers (Suhrawardi, Ibn Arabi, Mulla Sadra) are NOT in the corpus** — do not answer about them as if from the source; say they are not yet covered.

## Verification

1. Run a query and confirm it returns entries with valid citations.
2. Grep the TSV to confirm the full text matches the citation.
3. Answer a test question and confirm every claim is anchored in a quoted Arabic passage.

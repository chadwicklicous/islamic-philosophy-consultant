# Islamic Philosophy Consultant

A citation-grounded research consultant for the **Islamic philosophers (falāsifa)** —
al-Kindi, al-Farabi, Avicenna (Ibn Sina), al-Ghazali, Averroes (Ibn Rushd), and Ibn Arabi.
It answers questions **from the original Arabic** (and, for Ibn Arabi, from a clearly-labeled
English translation) with exact citations — not from a model's recollection.

---

## What it is

A suite of retrieval tools that turns the primary texts of six Islamic philosophers
into a **searchable, citation-grounded corpus**. When you ask a question, the consultant
finds the actual passages that answer it, in the original language, and hands you the
exact citation so you can verify it against the critical edition.

**It does not paraphrase from memory. It retrieves from the text and shows you the source.**

| Thinker | Works | Segments | Language |
|---------|-------|----------|----------|
| **al-Kindi** | 7 philosophical epistles (On First Philosophy, De Intellectu, On the Soul, etc.) | 53 | Arabic |
| **al-Farabi** | the Dieterici collection (Al-Jam', Fusus al-Hikam, 'Uyun al-Masa'il, Ma'ani al-'Aql, etc.) | 71 | Arabic |
| **Avicenna (Ibn Sina)** | *al-Najat* (The Deliverance): logic, physics, metaphysics | 264 | Arabic |
| **al-Ghazali** | *al-Munqidh min al-Dalal*, *al-Iqtisad fi al-I'tiqad* | 120 | Arabic |
| **Averroes (Ibn Rushd)** | *Fasl al-Maqal*, *Bidayat al-Mujtahid* (17 books) | 715 | Arabic |
| **Ibn Arabi** | *Tarjuman al-Ashwaq* (tr. Nicholson) | 85 | **English** |

**Total: 1,308 citation-grounded segments.**

---

## Why this is different from asking ChatGPT / Claude / Perplexity

A generative AI (ChatGPT, Claude, Perplexity) produces an answer by extrapolating from
patterns in its training data. When you ask it about Avicenna, it **generates** a
plausible answer — which can include **quotes and citations that do not exist**. You
cannot open "the book" it is quoting and confirm the words are really there.

This consultant **retrieves** the answer from a real, local corpus. Every answer is
produced by:
1. Searching a vector index built over the **actual primary texts** (the Arabic of
   *al-Najat*, *Ma'ani al-'Aql*, etc.).
2. Returning the **verbatim original-language passage**.
3. Citing its **exact scholarly reference** (e.g. `al-Farabi | معاني العقل`), so you
   can open the critical edition and verify it.

Because the answer is retrieved — not generated — **it cannot fabricate a citation.**
If the passage is not in the corpus, the tool says nothing rather than invent.

### The honest difference, in one line
> A chat AI *guesses* at what Avicenna said and gives you no way to check.
> This shows you the actual Arabic passage he wrote, with the citation to verify it.

### When you should STILL use a chat AI
- For **synthesis, translation, and broad explanation** — a general AI is far better
  at this.
- For **brainstorming and open-ended analysis**.
- For **anything far beyond this corpus**.

**The best workflow uses both:** a generative AI for breadth and drafting, this tool
for **grounding and verification** — the moment a quote has to be real and checkable.

---

## The limits (honestly stated)

1. **Coverage is not complete.** The corpus covers six thinkers, but not every work
   of every thinker. The **Illuminationist / later thinkers — Suhrawardi and Mulla
   Sadra — are NOT included**, because no clean, machine-readable text (Arabic or
   English) is freely available; only imperfect OCR of scans or paid editions.
   Indexing garbled OCR would defeat the whole purpose.

2. **Ibn Arabi is a translation.** His *Tarjuman al-Ashwaq* is included as Nicholson's
   English translation (the Arabic original is not freely available as clean text).
   It is clearly labeled `tr. Nicholson` in every citation — answers from it are quoted
   in English, not Arabic.

3. **The corpus is not a whole library.** It is a focused set of primary works. If a
   passage you need is not in the corpus, the tool is silent — it does not fill gaps
   with invented text.

4. **Translation quality.** For the five Arabic thinkers, the text is the original
   Arabic (proofread ar.wikisource). For Ibn Arabi, the English translation is clean,
   but it is still a translation — treat it as such.

5. **Semantic search is approximate.** bge-m3 is multilingual, so English queries match
   Arabic text — but retrieval is by meaning, not exact words. For precise work, query
   in Arabic or include the thinker's name.

---

## How to use it

### For non-technical users (recommended): let your AI agent do the work

If you use **Hermes Agent** (or a similar AI agent), you don't need to run any commands.

1. Install the skill:
   ```bash
   hermes skills install https://raw.githubusercontent.com/chadwicklicous/islamic-philosophy-consultant/main/SKILL.md
   ```
2. Say: *"Set up the Islamic Philosophy consultant."*

Your agent reads the skill, installs the dependencies, downloads the corpus, builds
the index, and verifies it — all autonomously. Then you ask questions in plain English
and it answers from the original Arabic with exact citations.

### For technical users: run it directly

The pipeline is standalone Python (stdlib only for downloading/extracting; `chromadb`
for the index).

```bash
# 1. Install dependencies
pip install "chromadb==1.5.9"

# 2. Pull the embedding model (multilingual — required for Arabic)
ollama pull bge-m3

# 3. Build the corpus (downloads the clean texts, extracts segments)
cd scripts
python ip_download.py      # fetches all raw texts from ar.wikisource + archive.org
python ip_extract.py      # splits into citation-tagged segments (text/*.tsv)

# 4. Build the vector index (embeds ~1,308 segments; resumable)
python ip_index.py

# 5. Query — in Arabic (original)
python ip_index.py --query "فصل في إثبات واجب الوجود" --k 5
# or in English (bge-m3 is multilingual)
python ip_index.py --query "the Necessary Being and proof of God" --k 5
```

### The scripts

| Script | Purpose |
|--------|---------|
| `ip_download.py` | Fetches the clean primary texts from ar.wikisource + archive.org (resumes) |
| `ip_extract.py` | Splits each raw text into citation-tagged segments → `text/*.tsv` |
| `ip_extract_avicenna.py` | Section-aware splitter for Avicenna's *al-Najat* |
| `ip_extract_ibn_arabi.py` | Extracts Ibn Arabi's English translation (labels it) |
| `ip_index.py` | Builds/updates the ChromaDB vector index; runs `--query` |

---

## Citation format

| Form | Meaning |
|------|---------|
| `al-Kindi \| في الفلسفة الأولى` | al-Kindi, On First Philosophy |
| `al-Farabi \| الجمع بين رأيي الحكيمين` | al-Farabi, The Harmonization of the Two Sages |
| `Avicenna \| al-Najat \| الإلهيات` | Avicenna, The Deliverance, Metaphysics |
| `al-Ghazali \| المنقذ من الضلال` | al-Ghazali, The Deliverance from Error |
| `Averroes \| فصل المقال` | Averroes, The Decisive Treatise |
| `Ibn Arabi \| Tarjuman al-Ashwaq (tr. Nicholson)` | Ibn Arabi, English translation |

---

## Requirements

- **Python 3.9+** (stdlib only for download/extract; `chromadb` for the index)
- **ChromaDB** — `pip install "chromadb==1.5.9"`. Runs embedded (no server).
- **Ollama** — the embedding provider (free, local, no API key). `ollama pull bge-m3`.
- **Hermes Agent** (optional) — to use the bundled `islamic-philosophy-consultant` skill.

---

## License

MIT. The Arabic texts are from ar.wikisource (public/open); the English translation of
Ibn Arabi is from the public-domain Nicholson edition on archive.org. This repository
does not distribute the large corpus — the scripts build it from the public sources.

---

*The Islamic Philosophy Consultant is a research aid. It retrieves and cites the texts;
the interpretation and judgment remain with the reader.*

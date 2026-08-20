# Islamic Philosophy Consultant

A citation-grounded consultant for the **Islamic philosophers (falāsifa)** — al-Kindi,
al-Farabi, Avicenna (Ibn Sina), al-Ghazali, Averroes (Ibn Rushd), and Ibn Arabi —
answering **from the original Arabic** (and, for Ibn Arabi, from a clearly-labeled
English translation) with exact citations (thinker + work + section), not from a
translation or a model's recollection.

## What it does

1. Downloads the clean Arabic texts of the falāsifa from ar.wikisource:
   - **al-Kindi** — 7 philosophical epistles (On First Philosophy, De Intellectu, On the Soul, etc.)
   - **al-Farabi** — the Dieterici collection (Al-Jam', Fusus al-Hikam, 'Uyun al-Masa'il, Ma'ani al-'Aql, etc.)
   - **Avicenna (Ibn Sina)** — *al-Najat* (The Deliverance): logic, physics, metaphysics
   - **al-Ghazali** — *al-Munqidh min al-Dalal*, *al-Iqtisad fi al-I'tiqad*
   - **Averroes (Ibn Rushd)** — *Fasl al-Maqal*, *Bidayat al-Mujtahid* (17 books)
   - **Ibn Arabi** — *Tarjuman al-Ashwaq* (Nicholson's English translation)
2. Extracts 1,308 citation-tagged segments, each `CITATION\tTEXT`.
3. Builds a ChromaDB vector index (bge-m3, 1024-dim, multilingual) for semantic search.
4. Answers questions by retrieving the relevant passages with exact citations.

## Two ways to use it

### For non-technical users (recommended): let your AI agent do the work

If you use **Hermes Agent** (or a similar AI agent), you don't need to run any commands. Just:

1. Install the skill:
   ```bash
   hermes skills install https://raw.githubusercontent.com/chadwicklicous/islamic-philosophy-consultant/main/SKILL.md
   ```
2. Say: *"Set up the Islamic Philosophy consultant."*

Your agent reads the skill, installs the dependencies, downloads the corpus, builds the
index, and verifies it — all autonomously. Then you ask questions in plain English and it
answers from the original Arabic with exact citations.

### For technical users: run it directly

The pipeline is standalone Python. See the Quick start below.

## Requirements

- **Python 3.9+** (stdlib only for the pipeline; `chromadb` for the index)
- **ChromaDB** — `pip install "chromadb==1.5.9"` (in `requirements.txt`). Runs embedded.
- **Ollama** — the embedding provider (free, local, no API key). Pull the `bge-m3` model with `ollama pull bge-m3` (multilingual — required for Arabic).
- **Hermes Agent** (optional) — to use the bundled `islamic-philosophy-consultant` skill.

## Quick start

```bash
# 1. Install dependencies
pip install "chromadb==1.5.9"

# 2. Pull the embedding model
ollama pull bge-m3

# 3. Build the corpus (downloads the clean Arabic texts)
cd scripts
python ip_download.py            # Kindi, Farabi, Ghazali, Averroes (direct pages)
python ip_download_farabi.py     # Farabi (resolves transclusion stubs)
python ip_download_resolve.py    # Averroes Bidayat sub-pages + Kindi on_infinite

# 4. Extract citation-tagged segments
python ip_extract.py

# 5. Build the vector index (embeds 1,223 segments; resumable)
python ip_index.py

# 6. Query — original Arabic
python ip_index.py --query "فصل في اثبات واجب الوجود" --k 5
# or in English (bge-m3 is multilingual)
python ip_index.py --query "the Necessary Being and proof of God" --k 5
```

## Coverage

| Thinker | Works | Segments |
|---------|-------|----------|
| **al-Kindi** | 7 philosophical epistles | 53 |
| **al-Farabi** | Dieterici collection (8 treatises) | 71 |
| **Avicenna (Ibn Sina)** | *al-Najat* (logic, physics, metaphysics) | 264 |
| **al-Ghazali** | *al-Munqidh*, *al-Iqtisad* | 120 |
| **Averroes (Ibn Rushd)** | *Fasl al-Maqal*, *Bidayat al-Mujtahid* (17 books) | 715 |
| **Ibn Arabi** | *Tarjuman al-Ashwaq* (tr. Nicholson) — **English translation** | 85 |

### Not yet included (deferred)

The **Illuminationist / later thinkers** — Suhrawardi and Mulla Sadra — are
**not** in the corpus because no clean, machine-readable text (Arabic or English)
is freely available (only imperfect OCR of scans or paid editions). Ibn Arabi is
partially covered via the English *Tarjuman al-Ashwaq*; his major works (*Futuhat
al-Makkiyya*, *Fusus al-Hikam*) remain out pending clean editions. These gaps are
flagged so the consultant is honest about coverage rather than silently omitting
them. If clean editions are sourced, they can be added following the same pattern.

## Citation format

| Form | Meaning |
|------|---------|
| `al-Kindi \| في الفلسفة الأولى` | al-Kindi, On First Philosophy |
| `al-Farabi \| الجمع بين رأيي الحكيمين` | al-Farabi, The Harmonization of the Two Sages |
| `Avicenna \| al-Najat \| الإلهيات` | Avicenna, The Deliverance, Metaphysics |
| `al-Ghazali \| المنقذ من الضلال` | al-Ghazali, The Deliverance from Error |
| `Averroes \| فصل المقال` | Averroes, The Decisive Treatise |

## Research note

- **The Active Intellect and the Soul** (`docs/`) — a two-chapter comparative essay on the
  metaphysics of the soul and the active intellect in the Islamic philosophers vs. St. Thomas
  Aquinas, grounded in the corpus (Avicenna's *al-Najat*, al-Farabi's *Ma'ani al-'Aql*,
  al-Kindi's *On First Philosophy*, and the *Summa Theologiae* / *Contra Gentiles*).

## License

MIT. The Arabic texts are from ar.wikisource (public/open); this repository does not
distribute the large corpus — the scripts build it from the public source.

---

*The Islamic Philosophy Consultant is a research aid. It retrieves and cites the texts;
the interpretation and judgment remain with the reader.*

#!/usr/bin/env python3
"""Build a ChromaDB vector index of the Islamic Philosophy corpus (Avicenna et al.).

Each segment (citation + Arabic text) becomes a document. Embeddings come from
Ollama's bge-m3 (1024-dim, multilingual — handles Arabic, so English queries match
Arabic text). The index lives in chroma/ and supports citation-grounded retrieval.

Usage:
  python ip_index.py            # build/refresh the index
  python ip_index.py --query "the Necessary Being" --k 5
"""
import os, sys, json, time, urllib.request, urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(BASE, 'text')
CHROMA_DIR = os.path.join(BASE, 'chroma')
COLLECTION = 'islamic_philosophy_corpus'
OLLAMA_URL = 'http://localhost:11434'
EMBED_MODEL = 'bge-m3'


def embed(texts):
    texts = [t[:6000] for t in texts]
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                f'{OLLAMA_URL}/api/embed',
                data=json.dumps({'model': EMBED_MODEL, 'input': texts}).encode(),
                headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())['embeddings']
        except urllib.error.HTTPError as e:
            if e.code == 400 and len(texts) > 1:
                mid = len(texts) // 2
                return embed(texts[:mid]) + embed(texts[mid:])
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def load_entries():
    entries = []
    for fname in sorted(os.listdir(TXT)):
        if not fname.endswith('.tsv'):
            continue
        with open(os.path.join(TXT, fname), encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if '\t' not in line:
                    continue
                cit, text = line.split('\t', 1)
                if text.strip():
                    entries.append((cit.strip(), text.strip()))
    return entries


def main():
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection(
        name=COLLECTION, metadata={'hnsw:space': 'cosine'})
    entries = load_entries()
    print(f"Loaded {len(entries)} entries (model={EMBED_MODEL})")
    existing = col.count()
    print(f"Already indexed: {existing}")
    BATCH = 32
    start = existing
    for i in range(start, len(entries), BATCH):
        batch = entries[i:i+BATCH]
        ids = [f"p{i+j}" for j in range(len(batch))]
        texts = [t for _, t in batch]
        cits = [c for c, _ in batch]
        vecs = embed(texts)
        col.add(ids=ids, embeddings=vecs, documents=texts,
                metadatas=[{'citation': c} for c in cits])
        if (i // BATCH) % 5 == 0:
            print(f"  indexed {i+len(batch)}/{len(entries)}")
    print(f"Index complete: {col.count()} vectors")


def query(q, k=5):
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_collection(COLLECTION)
    vec = embed([q])[0]
    res = col.query(query_embeddings=[vec], n_results=k)
    return list(zip(res['metadatas'][0], res['documents'][0]))


if __name__ == '__main__':
    if '--query' in sys.argv:
        q = sys.argv[sys.argv.index('--query') + 1]
        k = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 5
        for meta, doc in query(q, k):
            print(f"\n[{meta['citation']}]\n  {doc[:300]}")
    else:
        main()

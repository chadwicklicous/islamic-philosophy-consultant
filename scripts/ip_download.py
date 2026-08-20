#!/usr/bin/env python3
"""Download the clean Arabic texts for the Islamic Philosophy consultant.

Fetches the verified ar.wikisource pages for:
  - Al-Kindi (7 philosophical epistles)
  - Al-Farabi (Dieterici collection, 8 treatises — resolves transclusion stubs)
  - Al-Ghazali (al-Munqidh min al-Dalal, al-Iqtisad fi al-I'tiqad)
  - Averroes (Fasl al-Maqal, Bidayat al-Mujtahid + its sub-pages)
  - Avicenna (al-Najat)

Each page's text is saved to raw/<thinker>/<slug>.txt. Uses the MediaWiki API
with proper UTF-8 handling (avoids MSYS shell Arabic mangling). Resumable:
skips files already downloaded.
"""
import os, json, time, re, urllib.request, urllib.error, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, 'raw')
WIKI = 'https://ar.wikisource.org/w/api.php'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

# thinker -> list of (slug, page_title)
PAGES = {
    'kindi': [
        ('first_philosophy', 'الكندي - الفلسفة الأولى'),
        ('de_intellectu', 'رسالة في العقل'),
        ('on_soul', 'رسالة في القول في النفس، المختصر من كتاب أرسطو وأفلاطون'),
        ('incorporeal_substances', 'رسالة في أنه جواهر لا أجسام'),
        ('definitions', 'رسالة في حدود الأشياء ورسومها'),
        ('on_infinite', 'رسالة في مائية ما لا يمكن أن يكون لا نهاية , و ما الذي يقال لا نهاية له'),
        ('on_oneness', 'رسالة في وحدانية الله وتناهي جرم العالم'),
    ],
    'farabi': [
        ('al_jam', 'مجموعة فلسفة أبي نصر الفارابي/كتاب الجمع بين رأيي الحكيمين أفلاطون وأرسطو طاليس'),
        ('fusus_al_hikam', 'مجموعة فلسفة أبي نصر الفارابي/كتاب فصوص الحكم مع شرحه نصوص الكلم'),
        ('uyun_al_masail', 'مجموعة فلسفة أبي نصر الفارابي/كتاب عيون المسائل'),
        ('maani_al_aql', 'مجموعة فلسفة أبي نصر الفارابي/كتاب معاني العقل'),
        ('before_philosophy', 'مجموعة فلسفة أبي نصر الفارابي/كتاب ما ينبغي أن يقدم قبل تعلم الفلسفة'),
        ('philosophical_questions', 'مجموعة فلسفة أبي نصر الفارابي/كتاب المسائل الفلسفية والأجوبة عنها'),
        ('exposition_metaphysics', 'مجموعة فلسفة أبي نصر الفارابي/كتاب الإبانة عن غرض أرسطو طاليس في كتاب ما بعد الطبيعة'),
        ('on_astrology', 'مجموعة فلسفة أبي نصر الفارابي/كتاب النكت فيما يصح وما لا يصح في أحكام النجوم'),
    ],
    'ghazali': [
        ('munqidh', 'المنقذ من الضلال'),
        ('iqtisad', 'الاقتصاد في الاعتقاد'),
    ],
    'averroes': [
        ('fasl_al_maqal', 'فصل المقال فيما بين الحكمة والشريعة من الاتصال'),
    ],
    'avicenna': [
        ('al_najat', 'ابن سينا – النجاة'),
    ],
}


def api_get(params, retries=5):
    params = dict(params)
    params['format'] = 'json'
    url = WIKI + '?' + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 * (attempt + 1))
                continue
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def get_wikitext(title):
    """Get raw wikitext (works for direct pages)."""
    d = api_get({'action': 'query', 'prop': 'revisions', 'rvprop': 'content',
                 'rvslots': 'main', 'titles': title})
    pages = d.get('query', {}).get('pages', {})
    for p in pages.values():
        if 'revisions' in p:
            return p['revisions'][0]['slots']['main']['*']
    return None


def get_rendered_text(title):
    """Get rendered HTML (templates expanded) and strip to plain text.

    Needed for Farabi's Dieterici pages, which transclude from the Page:
    namespace via the {{صفحات}} template (raw wikitext returns only the stub).
    """
    d = api_get({'action': 'parse', 'page': title, 'prop': 'text',
                 'formatversion': '2'})
    try:
        html = d['parse']['text']
    except Exception:
        return None
    text = re.sub(r'<[^>]+>', '', html)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_subpages(prefix):
    """Find all pages under a prefix (for Bidayat's index of sub-pages)."""
    pages = []
    apcontinue = None
    while True:
        params = {'action': 'query', 'list': 'allpages', 'apprefix': prefix,
                  'aplimit': '500'}
        if apcontinue:
            params['apcontinue'] = apcontinue
        d = api_get(params)
        for p in d.get('query', {}).get('allpages', []):
            pages.append(p['title'])
        apcontinue = d.get('continue', {}).get('apcontinue')
        if not apcontinue:
            break
    return pages


def save(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def main():
    total_ok = 0
    total_fail = 0

    # 1. Direct pages (Kindi, Ghazali, Avicenna, Averroes Fasl)
    for thinker, pages in PAGES.items():
        thinker_dir = os.path.join(RAW, thinker)
        os.makedirs(thinker_dir, exist_ok=True)
        print(f"=== {thinker} ===")
        for slug, title in pages:
            out = os.path.join(thinker_dir, f"{slug}.txt")
            if os.path.exists(out) and os.path.getsize(out) > 100:
                print(f"  [skip] {slug}")
                total_ok += 1
                continue
            try:
                text = get_wikitext(title)
                if text and len(text) > 100:
                    save(out, text)
                    print(f"  [ok]   {slug} ({len(text)} chars)")
                    total_ok += 1
                else:
                    print(f"  [FAIL] {slug} — empty or missing")
                    total_fail += 1
            except Exception as e:
                print(f"  [FAIL] {slug} — {e}")
                total_fail += 1
            time.sleep(0.5)

    # 2. Farabi: resolve transclusion stubs via rendered HTML
    farabi_dir = os.path.join(RAW, 'farabi')
    os.makedirs(farabi_dir, exist_ok=True)
    print("=== farabi (resolve transclusions) ===")
    for slug, title in PAGES['farabi']:
        out = os.path.join(farabi_dir, f"{slug}.txt")
        if os.path.exists(out) and os.path.getsize(out) > 500:
            print(f"  [skip] {slug}")
            total_ok += 1
            continue
        text = get_rendered_text(title)
        if text and len(text) > 500:
            save(out, text)
            print(f"  [ok]   {slug} ({len(text)} chars)")
            total_ok += 1
        else:
            print(f"  [FAIL] {slug}")
            total_fail += 1
        time.sleep(0.5)

    # 3. Averroes Bidayat: fetch all sub-pages
    averroes_dir = os.path.join(RAW, 'averroes')
    os.makedirs(averroes_dir, exist_ok=True)
    print("=== averroes (Bidayat sub-pages) ===")
    subs = get_subpages('بداية المجتهد - كتاب')
    print(f"  found {len(subs)} sub-pages")
    combined = []
    for sub in subs:
        text = get_rendered_text(sub)
        if text and len(text) > 200:
            combined.append(f"\n\n=== {sub} ===\n\n{text}")
        time.sleep(0.3)
    if combined:
        out = os.path.join(averroes_dir, 'bidayat_full.txt')
        save(out, '\n'.join(combined))
        print(f"  [ok] bidayat_full.txt ({len(''.join(combined))} chars, {len(combined)} books)")
        total_ok += 1
    else:
        print("  [FAIL] no Bidayat sub-pages retrieved")
        total_fail += 1

    print(f"\nDone: {total_ok} ok, {total_fail} fail")


if __name__ == '__main__':
    main()

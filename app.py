"""
Bible App - Flask backend

English (default): World English Bible (WEB) via bible-api.com
Chinese / Swahili / Hindi: via the getBible API (api.getbible.net)

Browse by book/chapter, view verses, and search. The user's language is
stored in a cookie; a link can also force one with ?lang=zh|sw|hi|en.
"""
import os
import re
import time
from urllib.parse import urlencode

import requests
from flask import (
    Flask, render_template, request, jsonify, abort, g, redirect,
)

from i18n import DEFAULT_LANG, LANGUAGES, STRINGS, build_book_labels

app = Flask(__name__)

BIBLE_API_BASE = "https://bible-api.com"
GETBIBLE_API = "https://api.getbible.net/v2"

LANG_COOKIE = "lang"
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # one year

BOOKS = [
    ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
    ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
    ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
    ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
    ("Esther", 10), ("Job", 42), ("Psalms", 150), ("Proverbs", 31),
    ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66), ("Jeremiah", 52),
    ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12), ("Hosea", 14),
    ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
    ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3),
    ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4),
    ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21),
    ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13),
    ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4),
    ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4),
    ("Titus", 3), ("Philemon", 1), ("Hebrews", 13), ("James", 5),
    ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1),
    ("3 John", 1), ("Jude", 1), ("Revelation", 22),
]

BOOK_NAMES = [b[0] for b in BOOKS]
CHAPTER_COUNTS = {b[0]: b[1] for b in BOOKS}
BOOK_LABELS = build_book_labels(BOOK_NAMES)  # {lang: {english_name: label}}


# ---------------------------------------------------------------------------
# Translation helpers
# ---------------------------------------------------------------------------

def translate(lang, key, **kwargs):
    """Look up a UI string, falling back to English."""
    text = STRINGS.get(lang, {}).get(key) or STRINGS[DEFAULT_LANG][key]
    return text.format(**kwargs) if kwargs else text


def book_label(lang, english_name):
    return BOOK_LABELS.get(lang, BOOK_LABELS[DEFAULT_LANG]).get(english_name, english_name)


# ---------------------------------------------------------------------------
# Tiny in-memory cache (successful lookups only, so outages are not "sticky")
# ---------------------------------------------------------------------------

_CACHE = {}
_CACHE_MAX_ENTRIES = 1000


def cache_get(key):
    entry = _CACHE.get(key)
    if entry and entry[0] > time.time():
        return entry[1]
    return None


def cache_set(key, value, ttl=6 * 3600):
    if len(_CACHE) >= _CACHE_MAX_ENTRIES:
        _CACHE.clear()
    _CACHE[key] = (time.time() + ttl, value)


# ---------------------------------------------------------------------------
# Data sources
# ---------------------------------------------------------------------------

def fetch_passage(reference):
    """English: fetch a passage from bible-api.com. Returns parsed JSON or None."""
    try:
        resp = requests.get(
            f"{BIBLE_API_BASE}/{reference}",
            params={"translation": LANGUAGES[DEFAULT_LANG]["translation"]},
            timeout=8,
        )
        if resp.status_code != 200:
            return None
        return resp.json()
    except (requests.RequestException, ValueError):
        return None


def resolve_translation(lang):
    """Return the getBible translation abbreviation to use for `lang`, or None."""
    cfg = LANGUAGES[lang]

    override = os.environ.get(f"BIBLE_TRANSLATION_{lang.upper()}")
    if override:
        return override
    if cfg.get("translation"):
        return cfg["translation"]

    # No fixed code configured (Hindi): find one in getBible's translation list.
    cache_key = ("resolve", lang)
    cached = cache_get(cache_key)
    if cached:
        return cached
    if cache_get(("resolve-failed", lang)):
        return None

    wanted = cfg.get("lookup_language", "").lower()
    try:
        resp = requests.get(f"{GETBIBLE_API}/translations.json", timeout=8)
        resp.raise_for_status()
        data = resp.json()
        entries = data.values() if isinstance(data, dict) else data
        matches = sorted(
            e["abbreviation"]
            for e in entries
            if isinstance(e, dict)
            and str(e.get("language", "")).lower() == wanted
            and e.get("abbreviation")
        )
        if matches:
            cache_set(cache_key, matches[0], ttl=24 * 3600)
            return matches[0]
    except (requests.RequestException, ValueError):
        pass

    cache_set(("resolve-failed", lang), True, ttl=300)  # retry in 5 minutes
    return None


def fetch_chapter_getbible(lang, book_name, chapter):
    """Return a list of {'verse': int, 'text': str} for one chapter, or None."""
    code = resolve_translation(lang)
    if not code:
        return None

    key = ("chapter", code, book_name, chapter)
    cached = cache_get(key)
    if cached is not None:
        return cached

    book_number = BOOK_NAMES.index(book_name) + 1  # canonical order 1..66
    try:
        resp = requests.get(
            f"{GETBIBLE_API}/{code}/{book_number}/{chapter}.json", timeout=8
        )
        if resp.status_code != 200:
            return None
        raw = resp.json().get("verses", [])
    except (requests.RequestException, ValueError, AttributeError):
        return None

    verses = [
        {"verse": v["verse"], "text": (v.get("text") or "").strip()}
        for v in raw
        if "verse" in v
    ]
    if not verses:
        return None
    cache_set(key, verses)
    return verses


def get_passage(lang, book_name, chapter, start=None, end=None):
    """
    Unified passage lookup. Returns
    {"reference": str, "text": str, "verses": [{"verse", "text"}, ...]} or None.
    `book_name` is always the English name.
    """
    suffix = ""
    if start is not None:
        suffix = f":{start}" + (f"-{end}" if end and end != start else "")

    if lang == DEFAULT_LANG:
        data = fetch_passage(f"{book_name} {chapter}{suffix}")
        if not data or not data.get("verses"):
            return None
        return data

    verses = fetch_chapter_getbible(lang, book_name, chapter)
    if not verses:
        return None
    if start is not None:
        last = end if end else start
        verses = [v for v in verses if start <= v["verse"] <= last]
        if not verses:
            return None

    return {
        "reference": f"{book_label(lang, book_name)} {chapter}{suffix}",
        "text": " ".join(v["text"] for v in verses),
        "verses": verses,
    }


# ---------------------------------------------------------------------------
# Reference parsing for non-English search ("约翰福音 3:16", "Yohana 3:16", ...)
# ---------------------------------------------------------------------------

_REF_RE = re.compile(
    r"""^\s*(?P<book>.+?)\s*(?P<ch>\d+)\s*章?
        (?:\s*(?:[:：.]|章)\s*(?P<v1>\d+)\s*(?:[-–—~]\s*(?P<v2>\d+))?)?
        \s*节?\s*$""",
    re.VERBOSE,
)


def _norm(text):
    return re.sub(r"[\s.\-·]", "", text).lower()


_ALIAS_CACHE = {}


def _aliases(lang):
    """normalized name -> English book name, for the language plus English."""
    if lang not in _ALIAS_CACHE:
        table = {_norm(n): n for n in BOOK_NAMES}
        for english, label in BOOK_LABELS.get(lang, {}).items():
            table[_norm(label)] = english
        _ALIAS_CACHE[lang] = table
    return _ALIAS_CACHE[lang]


def parse_reference(query, lang):
    """Return (english_book, chapter, verse_start, verse_end) or None."""
    m = _REF_RE.match(query)
    if not m:
        return None

    table = _aliases(lang)
    key = _norm(m.group("book"))
    book = table.get(key)
    if book is None and len(key) >= 2:  # unique prefix, e.g. "gen", "psalm"
        candidates = {b for alias, b in table.items() if alias.startswith(key)}
        if len(candidates) == 1:
            book = candidates.pop()
    if book is None:
        return None

    chapter = int(m.group("ch"))
    if not 1 <= chapter <= CHAPTER_COUNTS[book]:
        return None

    v1 = int(m.group("v1")) if m.group("v1") else None
    v2 = int(m.group("v2")) if m.group("v2") else None
    if v1 is not None and v2 is not None and v2 < v1:
        v1, v2 = v2, v1
    return book, chapter, v1, v2


def lookup_reference(query, lang):
    """Free-text reference lookup used by search and the JSON API."""
    if lang == DEFAULT_LANG:
        return fetch_passage(query)  # bible-api.com understands English refs
    parsed = parse_reference(query, lang)
    if not parsed:
        return None
    return get_passage(lang, *parsed)


# ---------------------------------------------------------------------------
# Language selection (cookie, or ?lang=xx on any URL)
# ---------------------------------------------------------------------------

def _is_safe_next(path):
    return bool(path) and path.startswith("/") and not path.startswith("//") and "\\" not in path


@app.before_request
def detect_language():
    requested = request.args.get("lang")
    if requested in LANGUAGES:
        g.lang, g.persist_lang = requested, True
    else:
        cookie = request.cookies.get(LANG_COOKIE)
        g.lang = cookie if cookie in LANGUAGES else DEFAULT_LANG
        g.persist_lang = False


@app.after_request
def persist_language(resp):
    if getattr(g, "persist_lang", False):
        resp.set_cookie(
            LANG_COOKIE, g.lang, max_age=LANG_COOKIE_MAX_AGE, samesite="Lax"
        )
    resp.vary.add("Cookie")  # pages differ by language cookie
    return resp


@app.context_processor
def inject_i18n():
    lang = getattr(g, "lang", DEFAULT_LANG)

    # Current URL without ?lang=, so the language links can return here.
    args = [(k, v) for k, v in request.args.items(multi=True) if k != "lang"]
    current_url = request.path + (("?" + urlencode(args)) if args else "")

    return {
        "lang": lang,
        "lang_cfg": LANGUAGES[lang],
        "languages": LANGUAGES,
        "t": lambda key, **kw: translate(lang, key, **kw),
        "book_label": lambda name: book_label(lang, name),
        "current_url": current_url,
    }


@app.route("/set-language/<code>")
def set_language(code):
    if code not in LANGUAGES:
        abort(404)
    destination = request.args.get("next", "/")
    if not _is_safe_next(destination):
        destination = "/"
    resp = redirect(destination)
    resp.set_cookie(LANG_COOKIE, code, max_age=LANG_COOKIE_MAX_AGE, samesite="Lax")
    return resp


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html", books=BOOKS)


@app.route("/book/<book_name>")
def book_view(book_name):
    if book_name not in CHAPTER_COUNTS:
        abort(404)
    chapter_count = CHAPTER_COUNTS[book_name]
    return render_template(
        "book.html", book_name=book_name, chapter_count=chapter_count
    )


@app.route("/book/<book_name>/<int:chapter>")
def chapter_view(book_name, chapter):
    if book_name not in CHAPTER_COUNTS:
        abort(404)
    if chapter < 1 or chapter > CHAPTER_COUNTS[book_name]:
        abort(404)

    data = get_passage(g.lang, book_name, chapter)
    if data is None:
        return render_template(
            "error.html", message=translate(g.lang, "err_chapter")
        ), 502

    total_chapters = CHAPTER_COUNTS[book_name]
    return render_template(
        "chapter.html",
        book_name=book_name,
        chapter=chapter,
        verses=data["verses"],
        total_chapters=total_chapters,
        prev_chapter=chapter - 1 if chapter > 1 else None,
        next_chapter=chapter + 1 if chapter < total_chapters else None,
    )


@app.route("/verse/<book_name>/<int:chapter>/<int:verse>")
def verse_view(book_name, chapter, verse):
    if book_name not in CHAPTER_COUNTS:
        abort(404)
    data = get_passage(g.lang, book_name, chapter, verse)
    if data is None:
        return render_template(
            "error.html", message=translate(g.lang, "err_verse")
        ), 404
    return render_template(
        "verse.html", book_name=book_name, chapter=chapter, verse=verse, data=data
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("search.html", query="", result=None, error=None)

    data = lookup_reference(query, g.lang)
    if not data or not data.get("verses"):
        return render_template(
            "search.html",
            query=query,
            result=None,
            error=translate(g.lang, "err_not_found"),
        )

    return render_template("search.html", query=query, result=data, error=None)


@app.route("/api/passage")
def api_passage():
    reference = request.args.get("ref", "").strip()
    if not reference:
        return jsonify({"error": "Missing 'ref' parameter"}), 400
    data = lookup_reference(reference, g.lang)
    if data is None:
        return jsonify({"error": "Passage not found"}), 404
    return jsonify(data)


@app.errorhandler(404)
def not_found(e):
    lang = getattr(g, "lang", DEFAULT_LANG)
    return render_template("error.html", message=translate(lang, "err_page")), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

"""
Bible App - Flask backend
Serves the World English Bible (WEB) translation via bible-api.com
Browse by book/chapter, view verses, and search.
"""
import os
import requests
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)

BIBLE_API_BASE = "https://bible-api.com"
TRANSLATION = "web"  # World English Bible - public domain

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


def fetch_passage(reference):
    """Fetch a passage from bible-api.com. Returns parsed JSON or None on failure."""
    try:
        resp = requests.get(
            f"{BIBLE_API_BASE}/{reference}",
            params={"translation": TRANSLATION},
            timeout=8,
        )
        if resp.status_code != 200:
            return None
        return resp.json()
    except requests.RequestException:
        return None


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

    reference = f"{book_name} {chapter}"
    data = fetch_passage(reference)
    if data is None or "verses" not in data:
        return render_template(
            "error.html",
            message="Could not load this chapter right now. Please try again shortly.",
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
    reference = f"{book_name} {chapter}:{verse}"
    data = fetch_passage(reference)
    if data is None or "verses" not in data or not data["verses"]:
        return render_template(
            "error.html", message="That verse could not be found."
        ), 404
    return render_template(
        "verse.html", book_name=book_name, chapter=chapter, verse=verse, data=data
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("search.html", query="", result=None, error=None)

    data = fetch_passage(query)
    if data is None or "verses" not in data or not data["verses"]:
        return render_template(
            "search.html",
            query=query,
            result=None,
            error="No passage found for that reference. Try formats like 'John 3:16', 'Genesis 1', or 'Psalm 23:1-3'.",
        )

    return render_template("search.html", query=query, result=data, error=None)


@app.route("/api/passage")
def api_passage():
    reference = request.args.get("ref", "").strip()
    if not reference:
        return jsonify({"error": "Missing 'ref' parameter"}), 400
    data = fetch_passage(reference)
    if data is None:
        return jsonify({"error": "Passage not found"}), 404
    
return jsonify(data)


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found."), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)


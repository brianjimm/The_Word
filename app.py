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

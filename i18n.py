"""
Language support for the Bible app: language registry, UI strings and
localized book names.

Book names in URLs always stay English (e.g. /book/John/3) so links keep
working across languages; only the *displayed* label is localized.
"""

DEFAULT_LANG = "en"

# provider "bible-api" -> bible-api.com   (English WEB, the original source)
# provider "getbible"  -> api.getbible.net (Chinese, Swahili, Hindi)
#
# "translation" is the getBible abbreviation. For Hindi it is None on purpose:
# the app looks up a Hindi translation in getBible's translation list at
# runtime (see resolve_translation in app.py). You can pin any language to a
# specific translation with an environment variable, e.g.
#     BIBLE_TRANSLATION_HI=<abbreviation>
LANGUAGES = {
    "en": {
        "native": "English",
        "html_lang": "en",
        "provider": "bible-api",
        "translation": "web",
        "examples": ["John 3:16", "Genesis 1", "Psalm 23"],
    },
    "zh": {
        "native": "中文",
        "html_lang": "zh-Hans",
        "provider": "getbible",
        "translation": "cus",  # Chinese Union Version (Simplified)
        "examples": ["约翰福音 3:16", "创世记 1", "诗篇 23"],
    },
    "sw": {
        "native": "Kiswahili",
        "html_lang": "sw",
        "provider": "getbible",
        "translation": "swahili",
        "examples": ["Yohana 3:16", "Mwanzo 1", "Zaburi 23"],
    },
    "hi": {
        "native": "हिन्दी",
        "html_lang": "hi",
        "provider": "getbible",
        "translation": None,
        "lookup_language": "Hindi",
        "examples": ["यूहन्ना 3:16", "उत्पत्ति 1", "भजन संहिता 23"],
    },
}

STRINGS = {
    "en": {
        "tagline": "World English Bible",
        "search_placeholder": "Search a reference — e.g. John 3:16, Psalm 23",
        "find": "Find",
        "books": "Books",
        "search": "Search",
        "choose_book": "Choose a book to browse, or search a reference above.",
        "ot": "Old Testament",
        "nt": "New Testament",
        "chapter_n": "Chapter {n}",
        "results_for": "Results for \u201c{q}\u201d",
        "empty_search": "Enter a reference above to find a passage.",
        "try": "Try:",
        "err_not_found": "No passage found for that reference. Try formats like 'John 3:16', 'Genesis 1', or 'Psalm 23:1-3'.",
        "err_chapter": "Could not load this chapter right now. Please try again shortly.",
        "err_verse": "That verse could not be found.",
        "err_page": "Page not found.",
        "language": "Language",
        "footer": "World English Bible \u2014 public domain, freely shared \u00b7 text via bible-api.com",
        "title_suffix": "Scripture",
    },
    "zh": {
        "tagline": "圣经 · 和合本",
        "search_placeholder": "查找经文 — 例如 约翰福音 3:16、诗篇 23",
        "find": "查找",
        "books": "书卷",
        "search": "搜索",
        "choose_book": "请选择一卷书浏览，或在上方查找经文。",
        "ot": "旧约",
        "nt": "新约",
        "chapter_n": "第 {n} 章",
        "results_for": "\u201c{q}\u201d 的搜索结果",
        "empty_search": "请在上方输入经文出处以查找经文。",
        "try": "试试：",
        "err_not_found": "找不到该经文。请尝试如“约翰福音 3:16”、“创世记 1”或“诗篇 23:1-3”的格式。",
        "err_chapter": "暂时无法加载本章，请稍后再试。",
        "err_verse": "找不到该节经文。",
        "err_page": "找不到该页面。",
        "language": "语言",
        "footer": "和合本（简体）\u00b7 经文来源：getbible.net",
        "title_suffix": "圣经",
    },
    "sw": {
        "tagline": "Biblia Takatifu",
        "search_placeholder": "Tafuta andiko — mfano Yohana 3:16, Zaburi 23",
        "find": "Tafuta",
        "books": "Vitabu",
        "search": "Tafuta",
        "choose_book": "Chagua kitabu cha kusoma, au tafuta andiko hapo juu.",
        "ot": "Agano la Kale",
        "nt": "Agano Jipya",
        "chapter_n": "Sura ya {n}",
        "results_for": "Matokeo ya \u201c{q}\u201d",
        "empty_search": "Andika rejea hapo juu ili kupata andiko.",
        "try": "Jaribu:",
        "err_not_found": "Hakuna andiko lililopatikana kwa rejea hiyo. Jaribu mifano kama 'Yohana 3:16', 'Mwanzo 1', au 'Zaburi 23:1-3'.",
        "err_chapter": "Imeshindikana kupakia sura hii kwa sasa. Tafadhali jaribu tena baadaye.",
        "err_verse": "Mstari huo haukupatikana.",
        "err_page": "Ukurasa haukupatikana.",
        "language": "Lugha",
        "footer": "Biblia Takatifu (Kiswahili) \u00b7 maandiko kupitia getbible.net",
        "title_suffix": "Biblia",
    },
    "hi": {
        "tagline": "पवित्र बाइबल",
        "search_placeholder": "पद खोजें — जैसे यूहन्ना 3:16, भजन संहिता 23",
        "find": "खोजें",
        "books": "पुस्तकें",
        "search": "खोज",
        "choose_book": "पढ़ने के लिए कोई पुस्तक चुनें, या ऊपर कोई संदर्भ खोजें।",
        "ot": "पुराना नियम",
        "nt": "नया नियम",
        "chapter_n": "अध्याय {n}",
        "results_for": "\u201c{q}\u201d के परिणाम",
        "empty_search": "पद खोजने के लिए ऊपर संदर्भ लिखें।",
        "try": "आज़माएँ:",
        "err_not_found": "इस संदर्भ के लिए कोई पद नहीं मिला। 'यूहन्ना 3:16', 'उत्पत्ति 1' या 'भजन संहिता 23:1-3' जैसे रूप आज़माएँ।",
        "err_chapter": "यह अध्याय अभी लोड नहीं हो सका। कृपया थोड़ी देर बाद पुनः प्रयास करें।",
        "err_verse": "वह पद नहीं मिला।",
        "err_page": "पृष्ठ नहीं मिला।",
        "language": "भाषा",
        "footer": "पवित्र बाइबल (हिन्दी) \u00b7 पाठ स्रोत: getbible.net",
        "title_suffix": "बाइबल",
    },
}

# Same order as BOOKS in app.py (Genesis ... Revelation, 66 books).
_BOOK_LABELS_LIST = {
    "zh": [
        "创世记", "出埃及记", "利未记", "民数记", "申命记", "约书亚记", "士师记", "路得记",
        "撒母耳记上", "撒母耳记下", "列王纪上", "列王纪下", "历代志上", "历代志下",
        "以斯拉记", "尼希米记", "以斯帖记", "约伯记", "诗篇", "箴言", "传道书", "雅歌",
        "以赛亚书", "耶利米书", "耶利米哀歌", "以西结书", "但以理书", "何西阿书", "约珥书",
        "阿摩司书", "俄巴底亚书", "约拿书", "弥迦书", "那鸿书", "哈巴谷书", "西番雅书",
        "哈该书", "撒迦利亚书", "玛拉基书",
        "马太福音", "马可福音", "路加福音", "约翰福音", "使徒行传", "罗马书",
        "哥林多前书", "哥林多后书", "加拉太书", "以弗所书", "腓立比书", "歌罗西书",
        "帖撒罗尼迦前书", "帖撒罗尼迦后书", "提摩太前书", "提摩太后书", "提多书", "腓利门书",
        "希伯来书", "雅各书", "彼得前书", "彼得后书", "约翰一书", "约翰二书", "约翰三书",
        "犹大书", "启示录",
    ],
    "sw": [
        "Mwanzo", "Kutoka", "Walawi", "Hesabu", "Kumbukumbu la Torati", "Yoshua", "Waamuzi", "Ruthu",
        "1 Samweli", "2 Samweli", "1 Wafalme", "2 Wafalme", "1 Mambo ya Nyakati", "2 Mambo ya Nyakati",
        "Ezra", "Nehemia", "Esta", "Ayubu", "Zaburi", "Methali", "Mhubiri", "Wimbo Ulio Bora",
        "Isaya", "Yeremia", "Maombolezo", "Ezekieli", "Danieli", "Hosea", "Yoeli",
        "Amosi", "Obadia", "Yona", "Mika", "Nahumu", "Habakuki", "Sefania",
        "Hagai", "Zekaria", "Malaki",
        "Mathayo", "Marko", "Luka", "Yohana", "Matendo ya Mitume", "Warumi",
        "1 Wakorintho", "2 Wakorintho", "Wagalatia", "Waefeso", "Wafilipi", "Wakolosai",
        "1 Wathesalonike", "2 Wathesalonike", "1 Timotheo", "2 Timotheo", "Tito", "Filemoni",
        "Waebrania", "Yakobo", "1 Petro", "2 Petro", "1 Yohana", "2 Yohana", "3 Yohana",
        "Yuda", "Ufunuo wa Yohana",
    ],
    "hi": [
        "उत्पत्ति", "निर्गमन", "लैव्यव्यवस्था", "गिनती", "व्यवस्थाविवरण", "यहोशू", "न्यायियों", "रूत",
        "1 शमूएल", "2 शमूएल", "1 राजा", "2 राजा", "1 इतिहास", "2 इतिहास",
        "एज्रा", "नहेमायाह", "एस्तेर", "अय्यूब", "भजन संहिता", "नीतिवचन", "सभोपदेशक", "श्रेष्ठगीत",
        "यशायाह", "यिर्मयाह", "विलापगीत", "यहेजकेल", "दानिय्येल", "होशे", "योएल",
        "आमोस", "ओबद्याह", "योना", "मीका", "नहूम", "हबक्कूक", "सपन्याह",
        "हाग्गै", "जकर्याह", "मलाकी",
        "मत्ती", "मरकुस", "लूका", "यूहन्ना", "प्रेरितों के काम", "रोमियों",
        "1 कुरिन्थियों", "2 कुरिन्थियों", "गलातियों", "इफिसियों", "फिलिप्पियों", "कुलुस्सियों",
        "1 थिस्सलुनीकियों", "2 थिस्सलुनीकियों", "1 तीमुथियुस", "2 तीमुथियुस", "तीतुस", "फिलेमोन",
        "इब्रानियों", "याकूब", "1 पतरस", "2 पतरस", "1 यूहन्ना", "2 यूहन्ना", "3 यूहन्ना",
        "यहूदा", "प्रकाशित वाक्य",
    ],
}


def build_book_labels(english_names):
    """Map English book name -> displayed label, per language."""
    labels = {"en": {n: n for n in english_names}}
    for lang, names in _BOOK_LABELS_LIST.items():
        assert len(names) == len(english_names), f"{lang}: expected {len(english_names)} book names"
        labels[lang] = dict(zip(english_names, names))
    return labels

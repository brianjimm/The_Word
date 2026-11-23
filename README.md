# The_Word
Holy Bible App
Created using Flask Framework

## Languages
Readers pick a language from the switcher in the header. English is the default; the choice is remembered in a cookie.

| Language | Translation | Source |
|---|---|---|
| English (default) | World English Bible (`web`) | bible-api.com |
| 中文 (Chinese, Simplified) | Chinese Union Version (`cus`) | api.getbible.net |
| Kiswahili | Swahili (`swahili`) | api.getbible.net |
| हिन्दी (Hindi) | First Hindi translation listed by getBible (looked up at runtime) | api.getbible.net |

- Any link can force a language with `?lang=en|zh|sw|hi`.
- Search in non-English languages accepts localized or English book names: `约翰福音 3:16`, `Yohana 3:16-18`, `यूहन्ना 3`, `John 3:16`.
- To pin a language to a specific getBible translation, set an environment variable, e.g. `BIBLE_TRANSLATION_HI=<abbreviation>` (also `_ZH`, `_SW`). Abbreviations are listed at https://api.getbible.net/v2/translations.json
- Check each translation's copyright/licence before deploying publicly.

## Files
- `i18n.py` — language registry, UI strings, localized book names. Add a language here.
- `app.py` — routes, data sources, reference parsing.

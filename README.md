# Ronaldo captions

A personal research project: collect the captions of [@cristiano](https://www.instagram.com/cristiano/)'s Instagram
posts into a searchable local database, to study his writing style and, later, to build search / RAG tooling on top.

This is a fan project. It is not affiliated with or endorsed by Cristiano Ronaldo or Meta.

## Status

| | |
|---|---|
| Posts collected | 2,412 of the 4,145 shown on the profile (at collection time, October 2026) |
| Date range | March 2017 – October 2026 |
| Missing | About 1,730 older posts (roughly 2012 – early 2017), see [Limitations](#limitations) |
| Filtering | None. Every collected post is stored, including emoji-only, non-English and collab posts |

## How the data was collected

Honest summary: this is **scraping, done gently, from a logged-in browser session**.

1. Open the profile in Chrome while logged in.
2. `capture.js` hooks the page's own `fetch`/`XMLHttpRequest` and **only records the JSON responses the page already
   loads** (its `/api/graphql` pagination calls and the embedded initial data). It makes no API requests of its own.
3. It scrolls to the bottom every 6–11 seconds with random jitter, like a person would, and stops immediately on any
   non-200 response.
4. The captured posts are saved to `raw/*.jsonl` and loaded into SQLite by `ronaldo_db.py`.

Things that went wrong, for the record:
- My first attempt called Instagram's internal profile endpoint directly from the page. It was rate-limited (HTTP 429)
  on the first request, so I abandoned direct API calls and switched to passively recording the page's own traffic.
- A cursor-based feed endpoint I tried afterwards returned the HTML app shell instead of JSON, so it was not used.

## Limitations

- **Incomplete history.** The web grid stopped paginating at about March 2017: the page sent no further requests, and
  waiting did not help. Older posts were not reachable this way.
- **Snapshot numbers.** Likes and comment counts are as of capture time and will drift.
- **No labels yet.** Language, topic and sentiment are not tagged. `ronaldo_db.py` contains an optional rule-based
  English detector (`is_meaningful_english`), which is approximate and is **not** applied on ingest.
- **Collab posts.** Posts on his grid owned by other accounts (brands, clubs) are stored with their `owner` so they can
  be excluded; their captions are not Ronaldo's own voice.
- Captions only. No images, video, comments or follower data.

## Usage

Requires Python 3.9+ with SQLite FTS5 (standard in CPython). No third-party packages.

```
python ronaldo_db.py ingest raw/run2.jsonl     # idempotent: re-ingesting updates rows by shortcode
python ronaldo_db.py stats
python ronaldo_db.py search "legacy" -n 5      # full-text search, stemmed
```

Schema (`posts`): `code` (shortcode, primary key), `ts` (unix seconds), `likes`, `comments`,
`type` (`image` | `video` | `carousel`), `caption`, `owner`.

To reproduce a capture: log in, open a profile, paste `capture.js` into the DevTools console, and leave the tab open.
Progress is in `window.__ig2` and mirrored to `localStorage`. `receiver.py` is a small local helper used to move the
data from the browser to `raw/` (the page serves it a URL hash; it POSTs to `127.0.0.1` only), and is not needed if
you copy the data out another way.

## Legal and ethical notes

- The captions are Ronaldo's (or his team's) copyrighted text. Collecting them goes against
  [Instagram's Terms of Use](https://help.instagram.com/581066165581870), which prohibit automated collection without
  permission. This project is for personal research; you are responsible for how you use any data you collect.
- For that reason **the collected dataset is not included in this repository** (`raw/` and `ronaldo.db` are in
  `.gitignore`). The code and method are what is shared; run the capture yourself if you want the data.
- Please be gentle if you reproduce this: keep the delays, do not parallelise, and stop on errors. Use a throwaway
  account if you are worried about your own.
- If you are a rights holder and want something removed, open an issue.

## License

Code: choose a license before publishing (MIT is a common choice). No license is granted for the captions themselves.

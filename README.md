# 🐐 Ronaldo Captions

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Cristiano_Ronaldo_0876.jpg/960px-Cristiano_Ronaldo_0876.jpg" alt="Cristiano Ronaldo celebrating a goal" width="600">
  <br>
  <sub>Photo: <a href="https://commons.wikimedia.org/wiki/File:Cristiano_Ronaldo_0876.jpg">YantsImages / Aram Nersesyan</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></sub>
</p>

> 4,145 posts. 2,412 captions. 1 dataset. Zero chill.

Every caption from [@cristiano](https://www.instagram.com/cristiano/)'s Instagram, in one searchable SQLite file,
so you can study the master's writing without scrolling for 4,000 posts. Because we have lives. Mostly.

**Why?** To learn how Ronaldo writes, and to build search / RAG / style tools on top. Pure fan project. Not affiliated with Ronaldo or Meta.

## How we did it

1. 🕵️ Opened his profile in a logged-in browser and scrolled slowly, like a human who is *definitely* not a robot.
2. 📝 A tiny script quietly wrote down the posts Instagram was already sending to the page. No hammering, no tricks.
3. 📦 Dropped everything into SQLite with full-text search. Nothing filtered, nothing judged.

## What you get

- **2,412 of 4,145 posts**, March 2017 → October 2026. Instagram stops loading older ones, so the 2012–2017 era is missing. We tried. Even legends have limits.
- Caption, date, likes, comments, post type and who posted it.
- Emoji-only posts, Portuguese, Arabic and collab posts are all in there. Filter them yourself. 🇵🇹

## Try it

```
python src/ronaldo_db.py stats
python src/ronaldo_db.py search "legacy" -n 5
```

```
.
├── data/   the loot (ronaldo.db + raw JSONL)
└── src/    capture.js (scout), receiver.py (ball boy), ronaldo_db.py (vault), test_filter.py (VAR)
```

## Fair warning 🟨

The captions belong to Ronaldo and his team, and Instagram's Terms of Use don't allow automated collection.
This is shared for research and fun. If you are a rights holder and want something removed, open an issue and it's gone.
If you copy the scraper, be gentle: slow scrolling, no parallel runs, stop on errors.

*Siuuuu.*

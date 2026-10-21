"""The vault. Stores EVERY post unfiltered, like a goalkeeper who lets everything in so the striker can sort it out later.

Usage (run from the repo root):
  python src/ronaldo_db.py ingest data/raw/run2.jsonl   # idempotent: re-ingesting updates rows by shortcode
  python src/ronaldo_db.py stats
  python src/ronaldo_db.py search "champion mindset" -n 10

Each JSONL line: {"code","ts","likes","comments","type","caption","owner"}
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "ronaldo.db"

# --- optional helper for later labelling; NOT used by ingest -------------------------------------
STOPWORDS = {
    "the", "and", "to", "of", "in", "for", "is", "with", "on", "that", "this", "it", "you",
    "my", "we", "our", "be", "are", "was", "as", "at", "by", "from", "all", "have", "not",
    "so", "but", "your", "will", "thank", "thanks", "just", "never", "always", "team",
}
# Portuguese / Spanish function words that are not English words; English must clearly outnumber them.
FOREIGN = {
    "de", "da", "do", "das", "dos", "com", "para", "uma", "um", "os", "as", "em", "que", "não", "nao",
    "por", "pelo", "pela", "obrigado", "obrigada", "muito", "nós", "nos", "está", "esta", "são", "foi",
    "mais", "vamos", "vitória", "orgulho", "el", "los", "las", "con", "una", "gracias", "feliz",
    "equipo", "equipa", "juntos", "juntas", "grande", "hoje", "amanhã", "ao", "aos", "meu", "minha",
}
URL_RE = re.compile(r"https?://\S+|www\.\S+")
TAG_RE = re.compile(r"[#@][\w.]+")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’]*")


def is_meaningful_english(caption: str) -> bool:
    text = TAG_RE.sub(" ", URL_RE.sub(" ", caption or ""))
    words = WORD_RE.findall(text)
    if len(words) < 3:
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters or sum(c.isascii() for c in letters) / len(letters) < 0.85:
        return False
    hits = sum(w.lower() in STOPWORDS for w in words)
    foreign = sum(w.lower() in FOREIGN for w in words)
    return hits >= 2 and hits / len(words) >= 0.15 and hits > foreign


# --- storage -------------------------------------------------------------------------------------
def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS posts (
            code TEXT PRIMARY KEY, ts INTEGER, likes INTEGER, comments INTEGER,
            type TEXT, caption TEXT NOT NULL DEFAULT '', owner TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
            caption, content='posts', content_rowid='rowid', tokenize='porter unicode61');
        CREATE TRIGGER IF NOT EXISTS posts_ai AFTER INSERT ON posts BEGIN
            INSERT INTO posts_fts(rowid, caption) VALUES (new.rowid, new.caption); END;
        CREATE TRIGGER IF NOT EXISTS posts_ad AFTER DELETE ON posts BEGIN
            INSERT INTO posts_fts(posts_fts, rowid, caption) VALUES ('delete', old.rowid, old.caption); END;
        """
    )
    return con


def ingest(path: str) -> None:
    con = connect()
    new = updated = 0
    for line in Path(path).read_text(encoding="utf-8").split("\n"):  # not splitlines(): captions may hold U+2028
        if not line.strip():
            continue
        p = json.loads(line)
        row = (p["code"], p.get("ts"), p.get("likes"), p.get("comments"), p.get("type"),
               (p.get("caption") or "").strip(), p.get("owner"))
        exists = con.execute("SELECT 1 FROM posts WHERE code=?", (p["code"],)).fetchone()
        if exists:
            con.execute("DELETE FROM posts WHERE code=?", (p["code"],))  # fires FTS delete trigger
            updated += 1
        else:
            new += 1
        con.execute("INSERT INTO posts VALUES (?,?,?,?,?,?,?)", row)
    con.commit()
    print(f"new {new}, updated {updated}. Goal!")


def stats() -> None:
    con = connect()
    n, empty, oldest, newest = con.execute(
        "SELECT COUNT(*), SUM(caption=''), MIN(ts), MAX(ts) FROM posts").fetchone()
    owners = con.execute("SELECT owner, COUNT(*) FROM posts GROUP BY owner ORDER BY 2 DESC LIMIT 5").fetchall()
    print(f"posts {n}, empty captions {empty}, ts range {oldest}..{newest}, owners {owners}")
    print("SIUUUUUUU")


def search(q: str, n: int = 10) -> None:
    con = connect()
    rows = con.execute(
        "SELECT p.code, p.likes, substr(p.caption,1,200) FROM posts_fts f JOIN posts p ON p.rowid=f.rowid "
        "WHERE posts_fts MATCH ? ORDER BY rank LIMIT ?", (q, n)).fetchall()
    for code, likes, cap in rows:
        print(f"[{code}] {likes} likes: {cap!r}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "ingest":
        ingest(sys.argv[2])
    elif cmd == "stats":
        stats()
    elif cmd == "search":
        search(sys.argv[2], int(sys.argv[4]) if len(sys.argv) > 4 else 10)

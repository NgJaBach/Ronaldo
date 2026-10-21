"""The ball boy. Fetches posts from the browser and delivers them to disk, then sprints back to the touchline.

GET / serves a page that reads posts from the URL hash and POSTs them back to this server (127.0.0.1 only);
posts are appended to data/raw/run2.jsonl (one JSON per line)."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT.mkdir(exist_ok=True)

PAGE = b"""<!doctype html><meta charset=utf-8><title>rx</title><body id=b>waiting
<script>
(async()=>{
 try{
  const posts=JSON.parse(decodeURIComponent(escape(atob(location.hash.slice(1)))));
  const r=await fetch('/ingest',{method:'POST',body:JSON.stringify(posts)});
  document.getElementById('b').textContent='received '+await r.text();
 }catch(e){document.getElementById('b').textContent='error '+e}
})();
</script>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(PAGE)

    def do_POST(self):
        posts = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))))
        with open(OUT / "run2.jsonl", "a", encoding="utf-8") as f:
            for p in posts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str(len(posts)).encode())

    def log_message(self, *a):
        pass


HTTPServer(("127.0.0.1", 8765), H).serve_forever()

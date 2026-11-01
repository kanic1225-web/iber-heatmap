# Build a standalone Cloudflare Pages copy of heatmap/index.html (the artifact file stays untouched).
# Usage: python3 -I make_dist.py <heatmap/index.html> <heatmap/dist>
import os, re, sys
src, out = sys.argv[1], sys.argv[2]
h = open(src, encoding="utf-8").read()
title = re.search(r"<title>.*?</title>", h, re.S).group(0)
link = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', h).group(0)
style = re.search(r"<style>.*?</style>", h, re.S).group(0)
body = h
for piece in (title, link, style):
    body = body.replace(piece, "", 1)
body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', "", body).strip()
assert "<title>" not in body and "<style>" not in body
reset = ("<style>html{color-scheme:light}"
         ":root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
         "body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>")
doc = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
       "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
       + title + "\n" + link + "\n" + reset + "\n" + style + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(doc)
open(os.path.join(out, "_headers"), "w").write("/*\n  Cache-Control: public, max-age=300\n  X-Content-Type-Options: nosniff\n")
print("dist", os.path.getsize(os.path.join(out, "index.html")), "bytes")

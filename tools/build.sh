#!/usr/bin/env bash
# Rebuild index.artifact.html and dist/ from geo/, data/ and tools/.
# Usage (from anywhere): bash tools/build.sh [extra <html> attributes for the screenshot wrapper]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/index.artifact.html"
mkdir -p "$BUILD"

# 1. Generate the artifact page (geometry in geo/, real data in data/).
python3 -I "$ROOT/tools/gen.py" "$ROOT/geo" "$ROOT/tools/template.html" "$OUT" "$ROOT/data" > "$BUILD/gen.log" \
  || { cat "$BUILD/gen.log"; echo GEN_FAILED; exit 1; }
head -3 "$BUILD/gen.log"

# 2. Syntax-check the inline script.
python3 -I -c "
import re,sys
h=open(sys.argv[1],encoding='utf-8').read(); s=re.findall(r'<script>(.*?)</script>',h,re.S); open(sys.argv[2],'w',encoding='utf-8').write(s[-1])" "$OUT" "$BUILD/inline.js"
if command -v node >/dev/null 2>&1; then
  node --check "$BUILD/inline.js" && echo SYNTAX_OK
else
  echo "node not found; skipping syntax check"
fi

# 3. Standalone Cloudflare Pages copy in dist/ (index.html + _headers).
python3 -I "$ROOT/tools/make_dist.py" "$OUT" "$ROOT/dist"

# 4. Optional screenshots (only if Google Chrome is installed).
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ -x "$C" ]; then
  H="${1:-}"
  { echo '<!doctype html><html'"$H"'><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'; cat "$OUT"; echo '</body></html>'; } > "$BUILD/wrap.html"
  "$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=1440,1500 --screenshot="$BUILD/wide.png" "file://$BUILD/wrap.html" 2>/dev/null || echo "wide screenshot failed"
  "$C" --headless=new --disable-gpu --virtual-time-budget=6000 --window-size=400,2000 --screenshot="$BUILD/narrow.png" "file://$BUILD/wrap.html" 2>/dev/null || echo "narrow screenshot failed"
else
  echo "Chrome not found; skipping screenshots"
fi

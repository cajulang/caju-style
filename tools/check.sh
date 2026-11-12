#!/bin/sh
# Checks the compiler against Tailwind CSS 4: every utility of testdata/tokens.txt (those of a real
# site) must produce the same rules as in testdata/tailwind-reference.css.
set -e
cd "$(dirname "$0")/.."
CAJU=${CAJU:-caju}
"$CAJU" run testdata/reference.caju > /tmp/caju-style-check.css
python3 tools/cssdiff.py testdata/tailwind-reference.css /tmp/caju-style-check.css testdata/tokens.txt

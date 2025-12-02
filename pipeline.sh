#!/usr/local/bin/bash
# shellcheck disable=SC1091

test -d .venv || python 3 -m venv .venv
test "$VIRTUAL_ENV" || . .venv/bin/activate
pip install -r dev/requirements.txt

# plumb
for file in pdf/*.pdf; do
  echo "$file"
  python scripts/plumb.py --input "$file" --output-dir csv
done

# delete tables out-of-scope
find csv -not -name '*table3*' -delete

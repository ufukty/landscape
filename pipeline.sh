#!/usr/local/bin/bash

# plumb
for file in pdf/*.pdf; do
  echo "$file"
  python scripts/plumb.py --input "$file" --output-dir csv
done

# delete tables out-of-scope
find csv -not -name '*table3*' -delete

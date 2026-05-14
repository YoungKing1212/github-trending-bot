#!/usr/bin/env python3
import sys
sys.path.insert(0, 'scripts')
from fetch_trending import run_fetch
import json

data = run_fetch()
with open('trending.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('saved', len(data), 'categories')

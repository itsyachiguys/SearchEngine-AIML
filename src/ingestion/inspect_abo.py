import gzip
import json
from pathlib import Path

DATA_FILE = Path(
    "data/raw/abo/listings/metadata/listings_0.json.gz"
)

with gzip.open(DATA_FILE, "rt", encoding="utf-8") as f:
    for i in range(3):
        line = f.readline()

        if not line:
            break

        product = json.loads(line)

        print(f"\n--- PRODUCT {i + 1} ---")
        print(json.dumps(product, indent=2, ensure_ascii=False))
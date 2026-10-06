import gzip
import json
from pathlib import Path
from typing import Iterator


DEFAULT_METADATA_DIR = Path(
    "data/raw/abo/listings/metadata"
)


def iter_metadata_files(
    metadata_dir: Path = DEFAULT_METADATA_DIR,
) -> Iterator[Path]:
    """
    Yield all ABO metadata shards in deterministic order.
    """

    files = sorted(
        metadata_dir.glob("listings_*.json.gz")
    )

    if not files:
        raise FileNotFoundError(
            f"No ABO metadata files found in: {metadata_dir}"
        )

    yield from files


def iter_raw_products(
    metadata_dir: Path = DEFAULT_METADATA_DIR,
) -> Iterator[dict]:
    """
    Stream raw product records from all ABO metadata shards.

    Each line in the decompressed JSONL files represents
    one product listing.
    """

    for metadata_file in iter_metadata_files(metadata_dir):

        with gzip.open(
            metadata_file,
            "rt",
            encoding="utf-8",
        ) as file:

            for line_number, line in enumerate(file, start=1):

                line = line.strip()

                if not line:
                    continue

                try:
                    product = json.loads(line)

                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON in "
                        f"{metadata_file.name} "
                        f"at line {line_number}"
                    ) from exc

                yield product


def iter_us_products(
    metadata_dir: Path = DEFAULT_METADATA_DIR,
) -> Iterator[dict]:
    """
    Stream only US Amazon listings.

    Current target:
        domain_name == 'amazon.com'
    """

    for product in iter_raw_products(metadata_dir):

        if product.get("domain_name") == "amazon.com":
            yield product


if __name__ == "__main__":

    count = 0

    for product in iter_us_products():

        count += 1

        if count <= 3:
            print(
                json.dumps(
                    product,
                    indent=2,
                    ensure_ascii=False,
                )
            )

    print(f"\nUS products: {count}")
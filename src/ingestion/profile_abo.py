import gzip
import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

METADATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "abo"
    / "listings"
    / "metadata"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "abo_profile.json"


# Fields we specifically want to analyze.
TRACKED_FIELDS = [
    "item_id",
    "item_name",
    "brand",
    "bullet_point",
    "product_description",
    "item_keywords",
    "product_type",
    "node",
    "color",
    "material",
    "style",
    "model_name",
    "model_number",
    "model_year",
    "item_dimensions",
    "item_weight",
    "main_image_id",
    "other_image_id",
    "domain_name",
    "marketplace",
    "country",
]


def has_value(value):
    """Return True if a field contains meaningful data."""
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, list):
        return len(value) > 0

    if isinstance(value, dict):
        return len(value) > 0

    return True


def extract_language_tags(value, counter):
    """Recursively collect language_tag values."""
    if isinstance(value, dict):
        language_tag = value.get("language_tag")

        if language_tag:
            counter[language_tag] += 1

        for nested_value in value.values():
            if isinstance(nested_value, (dict, list)):
                extract_language_tags(nested_value, counter)

    elif isinstance(value, list):
        for item in value:
            extract_language_tags(item, counter)


def extract_product_types(value, counter):
    """Collect product_type values."""
    if not isinstance(value, list):
        return

    for item in value:
        if isinstance(item, dict):
            product_type = item.get("value")

            if product_type:
                counter[str(product_type)] += 1


def extract_categories(value, counter):
    """Collect node/category names."""
    if not isinstance(value, list):
        return

    for item in value:
        if not isinstance(item, dict):
            continue

        node_name = item.get("node_name")

        if node_name:
            counter[str(node_name)] += 1


def profile_dataset():
    files = sorted(METADATA_DIR.glob("listings_*.json.gz"))

    if not files:
        raise FileNotFoundError(
            f"No listings_*.json.gz files found in:\n{METADATA_DIR}"
        )

    print("=" * 70)
    print("ABO DATASET PROFILER")
    print("=" * 70)
    print(f"Metadata directory: {METADATA_DIR}")
    print(f"Files found: {len(files)}")
    print()

    total_products = 0
    malformed_records = 0

    field_counts = Counter()
    language_counts = Counter()
    marketplace_counts = Counter()
    country_counts = Counter()
    domain_counts = Counter()
    product_type_counts = Counter()
    category_counts = Counter()

    products_with_main_image = 0
    products_with_other_images = 0
    products_with_dimensions = 0
    products_with_weight = 0

    unique_item_ids = set()
    unique_item_domain_pairs = set()

    file_statistics = {}

    for file_path in files:
        print(f"Processing: {file_path.name}")

        file_records = 0
        file_errors = 0

        with gzip.open(file_path, "rt", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):

                if not line.strip():
                    continue

                try:
                    product = json.loads(line)
                except json.JSONDecodeError:
                    malformed_records += 1
                    file_errors += 1
                    continue

                if not isinstance(product, dict):
                    malformed_records += 1
                    file_errors += 1
                    continue

                total_products += 1
                file_records += 1

                # Field coverage
                for field in TRACKED_FIELDS:
                    if has_value(product.get(field)):
                        field_counts[field] += 1

                # IDs
                item_id = product.get("item_id")
                domain_name = product.get("domain_name")

                if item_id:
                    unique_item_ids.add(str(item_id))

                if item_id and domain_name:
                    unique_item_domain_pairs.add(
                        (str(item_id), str(domain_name))
                    )

                # Languages
                extract_language_tags(product, language_counts)

                # Marketplace
                marketplace = product.get("marketplace")

                if marketplace:
                    marketplace_counts[str(marketplace)] += 1

                # Country
                country = product.get("country")

                if country:
                    country_counts[str(country)] += 1

                # Domain
                if domain_name:
                    domain_counts[str(domain_name)] += 1

                # Product type
                extract_product_types(
                    product.get("product_type"),
                    product_type_counts,
                )

                # Categories
                extract_categories(
                    product.get("node"),
                    category_counts,
                )

                # Images
                if has_value(product.get("main_image_id")):
                    products_with_main_image += 1

                if has_value(product.get("other_image_id")):
                    products_with_other_images += 1

                # Physical attributes
                if has_value(product.get("item_dimensions")):
                    products_with_dimensions += 1

                if has_value(product.get("item_weight")):
                    products_with_weight += 1

        file_statistics[file_path.name] = {
            "records": file_records,
            "malformed_records": file_errors,
        }

        print(f"  Records: {file_records:,}")
        print(f"  Errors:  {file_errors:,}")
        print()

    def percentage(count):
        if total_products == 0:
            return 0.0

        return round((count / total_products) * 100, 2)

    field_coverage = {}

    for field in TRACKED_FIELDS:
        count = field_counts[field]

        field_coverage[field] = {
            "count": count,
            "percentage": percentage(count),
        }

    profile = {
        "dataset": {
            "total_products": total_products,
            "malformed_records": malformed_records,
            "metadata_files": len(files),
            "unique_item_ids": len(unique_item_ids),
            "unique_item_domain_pairs": len(unique_item_domain_pairs),
        },

        "field_coverage": field_coverage,

        "languages": {
            "total_language_tags": sum(language_counts.values()),
            "unique_languages": len(language_counts),
            "top": language_counts.most_common(50),
        },

        "marketplaces": marketplace_counts.most_common(50),

        "countries": country_counts.most_common(50),

        "domains": domain_counts.most_common(50),

        "product_types": product_type_counts.most_common(100),

        "categories": category_counts.most_common(100),

        "media_and_physical_attributes": {
            "main_image": {
                "count": products_with_main_image,
                "percentage": percentage(products_with_main_image),
            },
            "other_images": {
                "count": products_with_other_images,
                "percentage": percentage(products_with_other_images),
            },
            "dimensions": {
                "count": products_with_dimensions,
                "percentage": percentage(products_with_dimensions),
            },
            "weight": {
                "count": products_with_weight,
                "percentage": percentage(products_with_weight),
            },
        },

        "files": file_statistics,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            profile,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 70)
    print("PROFILE COMPLETE")
    print("=" * 70)

    print(f"Total products:        {total_products:,}")
    print(f"Malformed records:     {malformed_records:,}")
    print(f"Unique item IDs:       {len(unique_item_ids):,}")
    print(
        f"Unique item/domain:    "
        f"{len(unique_item_domain_pairs):,}"
    )

    print()
    print("Field coverage:")
    for field in TRACKED_FIELDS:
        print(
            f"  {field:<25} "
            f"{field_counts[field]:>10,} "
            f"({percentage(field_counts[field]):>6.2f}%)"
        )

    print()
    print("Top languages:")
    for language, count in language_counts.most_common(15):
        print(f"  {language:<15} {count:,}")

    print()
    print("Top marketplaces:")
    for marketplace, count in marketplace_counts.most_common(15):
        print(f"  {marketplace:<20} {count:,}")

    print()
    print("Top domains:")
    for domain, count in domain_counts.most_common(15):
        print(f"  {domain:<25} {count:,}")

    print()
    print("Top product types:")
    for product_type, count in product_type_counts.most_common(15):
        print(f"  {product_type:<35} {count:,}")

    print()
    print("Media / physical attributes:")
    print(
        f"  Main image:          "
        f"{products_with_main_image:,} "
        f"({percentage(products_with_main_image):.2f}%)"
    )
    print(
        f"  Other images:        "
        f"{products_with_other_images:,} "
        f"({percentage(products_with_other_images):.2f}%)"
    )
    print(
        f"  Dimensions:          "
        f"{products_with_dimensions:,} "
        f"({percentage(products_with_dimensions):.2f}%)"
    )
    print(
        f"  Weight:              "
        f"{products_with_weight:,} "
        f"({percentage(products_with_weight):.2f}%)"
    )

    print()
    print(f"Full report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    profile_dataset()
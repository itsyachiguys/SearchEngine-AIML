import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROFILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "abo_profile.json"
)

with open(PROFILE, "r", encoding="utf-8") as f:
    data = json.load(f)


print("\n" + "=" * 60)
print("LANGUAGES")
print("=" * 60)

for name, count in data["languages"]["top"]:
    print(f"{name:<15} {count:,}")


print("\n" + "=" * 60)
print("MARKETPLACES")
print("=" * 60)

for name, count in data["marketplaces"]:
    print(f"{name:<25} {count:,}")


print("\n" + "=" * 60)
print("COUNTRIES")
print("=" * 60)

for name, count in data["countries"]:
    print(f"{name:<10} {count:,}")


print("\n" + "=" * 60)
print("DOMAINS")
print("=" * 60)

for name, count in data["domains"]:
    print(f"{name:<30} {count:,}")


print("\n" + "=" * 60)
print("TOP PRODUCT TYPES")
print("=" * 60)

for name, count in data["product_types"][:30]:
    print(f"{name:<40} {count:,}")


print("\n" + "=" * 60)
print("TOP CATEGORIES")
print("=" * 60)

for name, count in data["categories"][:30]:
    print(f"{name:<60} {count:,}")
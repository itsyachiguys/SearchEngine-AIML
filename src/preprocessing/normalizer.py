from typing import Any

from src.preprocessing.schema import Product


def get_value(field: Any) -> Any:
    """
    Extract the first value from an ABO multilingual/list field.
    """
    if not field:
        return None

    if isinstance(field, list):
        if not field:
            return None

        first = field[0]

        if isinstance(first, dict):
            return first.get("value")

        return first

    return field


def get_values(field: Any) -> list[str]:
    """
    Extract all values from an ABO list field.
    """
    if not field:
        return []

    if not isinstance(field, list):
        return [str(field)]

    values = []

    for item in field:
        if isinstance(item, dict):
            value = item.get("value")

            if value is not None:
                values.append(str(value))

        else:
            values.append(str(item))

    return values


def normalize_product(raw: dict) -> Product:

    dimensions = {}

    raw_dimensions = raw.get("item_dimensions")

    if raw_dimensions:
        for dimension_name in ["height", "length", "width"]:
            dimension = raw_dimensions.get(dimension_name)

            if not dimension:
                continue

            normalized = dimension.get("normalized_value", {})

            dimensions[dimension_name] = {
                "value": normalized.get("value"),
                "unit": normalized.get("unit"),
            }

    weight_value = None
    weight_unit = None

    raw_weight = raw.get("item_weight")

    if raw_weight:
        weight = raw_weight[0]

        normalized = weight.get("normalized_value", {})

        weight_value = normalized.get("value")
        weight_unit = normalized.get("unit")

    node = None

    if raw.get("node"):
        node = raw["node"][0].get("node_name")

    return Product(
        item_id=raw["item_id"],
        domain_name=raw["domain_name"],

        marketplace=raw.get("marketplace"),
        country=raw.get("country"),

        title=get_value(raw.get("item_name")),
        brand=get_value(raw.get("brand")),
        description=get_value(raw.get("product_description")),

        bullet_points=get_values(raw.get("bullet_point")),
        keywords=get_values(raw.get("item_keywords")),

        product_type=get_value(raw.get("product_type")),
        category_path=node,

        color=get_value(raw.get("color")),
        material=get_value(raw.get("material")),
        style=get_value(raw.get("style")),
        model_name=get_value(raw.get("model_name")),
        model_number=get_value(raw.get("model_number")),

        model_year=get_value(raw.get("model_year")),

        weight_value=weight_value,
        weight_unit=weight_unit,

        dimensions=dimensions,

        main_image_id=raw.get("main_image_id"),
        other_image_ids=raw.get("other_image_id", []),
    )
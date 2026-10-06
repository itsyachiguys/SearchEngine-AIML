from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LocalizedText:
    """
    Text value together with its language.

    Example:
        language_tag = "en_IN"
        value = "Wireless Bluetooth Headphones"
    """

    language_tag: Optional[str]
    value: str


@dataclass
class ProductAttribute:
    """
    Generic localized product attribute.
    """

    language_tag: Optional[str]
    value: str


@dataclass
class Weight:
    value: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class Dimensions:
    height: Optional[float] = None
    height_unit: Optional[str] = None

    length: Optional[float] = None
    length_unit: Optional[str] = None

    width: Optional[float] = None
    width_unit: Optional[str] = None


@dataclass
class Product:
    """
    Canonical representation of an ABO product listing.

    The raw ABO schema is intentionally not copied directly.
    This schema represents the normalized structure that downstream
    retrieval and ranking systems will consume.
    """

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    item_id: str
    domain_name: str

    # ---------------------------------------------------------
    # Marketplace
    # ---------------------------------------------------------

    marketplace: Optional[str] = None
    country: Optional[str] = None

    # ---------------------------------------------------------
    # Localized textual information
    # ---------------------------------------------------------

    titles: list[LocalizedText] = field(default_factory=list)

    brands: list[LocalizedText] = field(default_factory=list)

    bullet_points: list[LocalizedText] = field(
        default_factory=list
    )

    keywords: list[LocalizedText] = field(
        default_factory=list
    )

    descriptions: list[LocalizedText] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Taxonomy
    # ---------------------------------------------------------

    product_types: list[str] = field(
        default_factory=list
    )

    category_paths: list[LocalizedText] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Product attributes
    # ---------------------------------------------------------

    colors: list[LocalizedText] = field(
        default_factory=list
    )

    materials: list[LocalizedText] = field(
        default_factory=list
    )

    styles: list[LocalizedText] = field(
        default_factory=list
    )

    model_names: list[LocalizedText] = field(
        default_factory=list
    )

    model_numbers: list[str] = field(
        default_factory=list
    )

    model_years: list[int] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Physical attributes
    # ---------------------------------------------------------

    weights: list[Weight] = field(
        default_factory=list
    )

    dimensions: list[Dimensions] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Media
    # ---------------------------------------------------------

    main_image_id: Optional[str] = None

    other_image_ids: list[str] = field(
        default_factory=list
    )
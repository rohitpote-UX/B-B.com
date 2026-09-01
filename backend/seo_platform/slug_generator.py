"""
Brand Battle — 2. SEO-Friendly URLs & 9. Canonical Engine
Generates clean, lowercase, hyphen-separated, stable, canonical slugs (/compare/nike-air-max-270-vs-adidas-ultraboost-23) and ensures A vs B and B vs A resolve to 1 canonical URL.
"""

import re
from typing import Tuple
from models import Product


class SlugGeneratorEngine:
    """Generates canonical SEO slugs and resolves product ordering to prevent duplicate content."""

    @staticmethod
    def slugify(text: str) -> str:
        """Convert arbitrary text to a clean URL slug."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        return text.strip("-")

    def generate_comparison_slug(self, p1: Product, p2: Product) -> Tuple[str, Product, Product]:
        """Generate canonical comparison slug with deterministic product ordering."""
        name1 = f"{p1.brand.name if p1.brand else ''} {p1.name}".strip()
        name2 = f"{p2.brand.name if p2.brand else ''} {p2.name}".strip()

        slug1 = self.slugify(name1)
        slug2 = self.slugify(name2)

        # Deterministic canonical ordering (alphabetical sort) so A vs B and B vs A match same slug
        if slug1 <= slug2:
            canonical_slug = f"{slug1}-vs-{slug2}"
            primary, secondary = p1, p2
        else:
            canonical_slug = f"{slug2}-vs-{slug1}"
            primary, secondary = p2, p1

        return canonical_slug, primary, secondary


# Singleton
slug_generator_engine = SlugGeneratorEngine()

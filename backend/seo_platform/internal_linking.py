"""
Brand Battle — 10. Internal Linking Engine
Surfaces internal links to related comparisons, better alternatives, and same-brand items using Knowledge Graph links.
"""

from typing import List, Dict, Any
from models import Product


class InternalLinkingEngine:
    """Generates contextual internal linking anchors for comparison pages."""

    def generate_internal_links(self, p1: Product, p2: Product) -> List[Dict[str, str]]:
        cat_name = p1.category.name if p1.category else "Electronics"
        b1 = p1.brand.name if p1.brand else "Brand"
        b2 = p2.brand.name if p2.brand else "Brand"

        return [
            {"anchor": f"More {cat_name} Comparisons", "url": f"/compare?category={cat_name}"},
            {"anchor": f"Top {b1} Alternatives", "url": f"/discover?brand={b1}"},
            {"anchor": f"Top {b2} Alternatives", "url": f"/discover?brand={b2}"},
            {"anchor": f"Best Budget Pick Deals", "url": "/deals"},
        ]


# Singleton
internal_linking_engine = InternalLinkingEngine()

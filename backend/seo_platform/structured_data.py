"""
Brand Battle — 6. Structured Data (Schema.org JSON-LD) Engine & 7. Breadcrumb Navigation
Generates comprehensive Schema.org JSON-LD schemas (Product, Offer, FAQPage, BreadcrumbList, WebPage).
"""

from typing import Dict, Any, List
from models import Product
from seo_platform.config import seo_config
from seo_platform.schemas import FAQItemSchema


class StructuredDataEngine:
    """Generates Schema.org compliant JSON-LD structured data."""

    def generate_json_ld(
        self, p1: Product, p2: Product, canonical_slug: str, faqs: List[FAQItemSchema]
    ) -> Dict[str, Any]:
        """Generate combined Schema.org JSON-LD graph."""
        name1 = f"{p1.brand.name if p1.brand else ''} {p1.name}".strip()
        name2 = f"{p2.brand.name if p2.brand else ''} {p2.name}".strip()
        canonical_url = f"{seo_config.domain}/compare/{canonical_slug}"
        cat_name = p1.category.name if p1.category else "Products"

        faq_elements = [
            {
                "@type": "Question",
                "name": item.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item.answer,
                },
            }
            for item in faqs
        ]

        graph = [
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "@id": canonical_url,
                "url": canonical_url,
                "name": f"{name1} vs {name2} Comparison",
                "isPartOf": {
                    "@type": "WebSite",
                    "name": seo_config.site_name,
                    "url": seo_config.domain,
                },
            },
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": seo_config.domain},
                    {"@type": "ListItem", "position": 2, "name": "Compare", "item": f"{seo_config.domain}/compare"},
                    {"@type": "ListItem", "position": 3, "name": cat_name, "item": f"{seo_config.domain}/discover?category={cat_name}"},
                    {"@type": "ListItem", "position": 4, "name": f"{name1} vs {name2}", "item": canonical_url},
                ],
            },
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_elements,
            },
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": name1,
                "offers": {
                    "@type": "Offer",
                    "price": getattr(p1, "current_best_price", 0.0) or 0.0,
                    "priceCurrency": "INR",
                    "availability": "https://schema.org/InStock",
                },
            },
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": name2,
                "offers": {
                    "@type": "Offer",
                    "price": getattr(p2, "current_best_price", 0.0) or 0.0,
                    "priceCurrency": "INR",
                    "availability": "https://schema.org/InStock",
                },
            },
        ]

        return {"@context": "https://schema.org", "@graph": graph}

    def generate_product_json_ld(self, p: Product) -> Dict[str, Any]:
        """Generate single Schema.org Product JSON-LD without fabricated reviews."""
        name = f"{p.brand.name if p.brand else ''} {p.name}".strip()
        price = getattr(p, "current_best_price", 0.0) or 0.0
        
        product_schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "url": f"{seo_config.domain}/product/{p.id}",
        }

        if getattr(p, "image_url", None):
            product_schema["image"] = [p.image_url]

        if getattr(p, "description", None):
            product_schema["description"] = p.description

        if p.brand:
            product_schema["brand"] = {
                "@type": "Brand",
                "name": p.brand.name,
            }

        if price > 0:
            product_schema["offers"] = {
                "@type": "Offer",
                "price": price,
                "priceCurrency": "INR",
                "availability": "https://schema.org/InStock",
                "url": f"{seo_config.domain}/product/{p.id}",
            }

        # Zero fake reviews rule: only include aggregateRating if genuine reviews exist
        if getattr(p, "average_rating", None) and getattr(p, "total_reviews", None) and p.total_reviews > 0:
            product_schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": p.average_rating,
                "reviewCount": p.total_reviews,
                "bestRating": 5,
                "worstRating": 1,
            }

        return product_schema

    def generate_breadcrumbs(self, p1: Product, p2: Product) -> List[Dict[str, str]]:
        name1 = f"{p1.brand.name if p1.brand else ''} {p1.name}".strip()
        name2 = f"{p2.brand.name if p2.brand else ''} {p2.name}".strip()
        cat_name = p1.category.name if p1.category else "Products"

        return [
            {"name": "Home", "url": "/"},
            {"name": "Compare", "url": "/compare"},
            {"name": cat_name, "url": f"/discover?category={cat_name}"},
            {"name": f"{name1} vs {name2}", "url": ""},
        ]


# Singleton
structured_data_engine = StructuredDataEngine()

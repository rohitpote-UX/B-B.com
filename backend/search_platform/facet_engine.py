"""
Brand Battle — Dynamic Faceted Search Engine
Generates filter facets dynamically from the PKG and result set.
"""

import logging
from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Product, Brand, Category, ProductAttribute, ProductTag, MarketplaceOffer

logger = logging.getLogger("brandbattle.search.facets")


class FacetEngine:
    """Generates dynamic faceted filters from search result sets and PKG data."""

    def generate_facets(
        self,
        product_ids: List[int],
        db: Session,
    ) -> Dict[str, Any]:
        """Generate dynamic facets from a result set of product IDs."""
        if not product_ids:
            return {"facets": []}

        products = (
            db.query(Product)
            .filter(Product.id.in_(product_ids), Product.is_active == True)
            .all()
        )

        facets = []

        # 1. Brand facet
        brand_facet = self._build_brand_facet(products, db)
        if brand_facet["options"]:
            facets.append(brand_facet)

        # 2. Category facet
        category_facet = self._build_category_facet(products, db)
        if category_facet["options"]:
            facets.append(category_facet)

        # 3. Price range facet
        price_facet = self._build_price_facet(products)
        if price_facet["options"]:
            facets.append(price_facet)

        # 4. Rating facet
        rating_facet = self._build_rating_facet(products)
        if rating_facet["options"]:
            facets.append(rating_facet)

        # 5. Marketplace facet (from offers)
        marketplace_facet = self._build_marketplace_facet(products, db)
        if marketplace_facet["options"]:
            facets.append(marketplace_facet)

        # 6. Dynamic attribute facets (from ProductAttribute)
        attr_facets = self._build_attribute_facets(products, db)
        facets.extend(attr_facets)

        # 7. Availability facet
        avail_facet = self._build_availability_facet(products)
        if avail_facet["options"]:
            facets.append(avail_facet)

        # 8. Discount facet
        discount_facet = self._build_discount_facet(products)
        if discount_facet["options"]:
            facets.append(discount_facet)

        return {"facets": facets, "total_products": len(products)}

    def _build_brand_facet(self, products: List[Product], db: Session) -> Dict[str, Any]:
        brand_counts: Counter = Counter()
        for p in products:
            if p.brand:
                brand_counts[p.brand.name] += 1

        options = [
            {"value": name, "label": name, "count": count}
            for name, count in brand_counts.most_common(20)
        ]
        return {"key": "brand", "label": "Brand", "type": "multi_select", "options": options}

    def _build_category_facet(self, products: List[Product], db: Session) -> Dict[str, Any]:
        cat_counts: Counter = Counter()
        for p in products:
            if p.category:
                cat_counts[p.category.name] += 1

        options = [
            {"value": name, "label": name, "count": count}
            for name, count in cat_counts.most_common(15)
        ]
        return {"key": "category", "label": "Category", "type": "multi_select", "options": options}

    def _build_price_facet(self, products: List[Product]) -> Dict[str, Any]:
        prices = [p.current_best_price for p in products if p.current_best_price and p.current_best_price > 0]
        if not prices:
            return {"key": "price", "label": "Price", "type": "range", "options": []}

        min_price = min(prices)
        max_price = max(prices)

        # Generate price range buckets
        ranges = []
        if max_price <= 1000:
            buckets = [(0, 250), (250, 500), (500, 750), (750, 1000)]
        elif max_price <= 10000:
            buckets = [(0, 1000), (1000, 3000), (3000, 5000), (5000, 10000)]
        elif max_price <= 50000:
            buckets = [(0, 5000), (5000, 10000), (10000, 25000), (25000, 50000)]
        elif max_price <= 200000:
            buckets = [(0, 10000), (10000, 25000), (25000, 50000), (50000, 100000), (100000, 200000)]
        else:
            buckets = [(0, 25000), (25000, 50000), (50000, 100000), (100000, 200000), (200000, float('inf'))]

        for low, high in buckets:
            count = sum(1 for p in prices if low <= p < high)
            if count > 0:
                if high == float('inf'):
                    label = f"Above {int(low)}"
                else:
                    label = f"{int(low)} - {int(high)}"
                ranges.append({"value": f"{int(low)}-{int(high)}", "label": label, "count": count})

        return {
            "key": "price",
            "label": "Price Range",
            "type": "range",
            "options": ranges,
            "min": round(min_price, 2),
            "max": round(max_price, 2),
        }

    def _build_rating_facet(self, products: List[Product]) -> Dict[str, Any]:
        rating_buckets = {"4+": 0, "3+": 0, "2+": 0, "1+": 0}
        for p in products:
            r = p.average_rating or 0
            if r >= 4.0:
                rating_buckets["4+"] += 1
            if r >= 3.0:
                rating_buckets["3+"] += 1
            if r >= 2.0:
                rating_buckets["2+"] += 1
            if r >= 1.0:
                rating_buckets["1+"] += 1

        options = [
            {"value": key, "label": f"{key} Stars", "count": count}
            for key, count in rating_buckets.items() if count > 0
        ]
        return {"key": "rating", "label": "Rating", "type": "single_select", "options": options}

    def _build_marketplace_facet(self, products: List[Product], db: Session) -> Dict[str, Any]:
        master_ids = [p.master_product_id for p in products if p.master_product_id]
        if not master_ids:
            return {"key": "marketplace", "label": "Marketplace", "type": "multi_select", "options": []}

        marketplace_counts = (
            db.query(MarketplaceOffer.marketplace, func.count(MarketplaceOffer.id))
            .filter(
                MarketplaceOffer.master_product_id.in_(master_ids),
                MarketplaceOffer.is_available == True,
            )
            .group_by(MarketplaceOffer.marketplace)
            .all()
        )

        options = [
            {"value": mp, "label": mp.replace("_", " ").title(), "count": count}
            for mp, count in marketplace_counts
        ]
        return {"key": "marketplace", "label": "Marketplace", "type": "multi_select", "options": options}

    def _build_attribute_facets(self, products: List[Product], db: Session) -> List[Dict[str, Any]]:
        """Build dynamic facets from ProductAttribute table."""
        master_ids = [p.master_product_id for p in products if p.master_product_id]
        if not master_ids:
            return []

        # Get top attribute names and their value distributions
        attr_stats = (
            db.query(
                ProductAttribute.attribute_name,
                ProductAttribute.attribute_value,
                func.count(ProductAttribute.id),
            )
            .filter(
                ProductAttribute.master_product_id.in_(master_ids),
                ProductAttribute.is_searchable == True,
            )
            .group_by(ProductAttribute.attribute_name, ProductAttribute.attribute_value)
            .having(func.count(ProductAttribute.id) >= 1)
            .all()
        )

        # Group by attribute name
        attr_groups: Dict[str, List[tuple]] = {}
        for name, value, count in attr_stats:
            if name not in attr_groups:
                attr_groups[name] = []
            attr_groups[name].append((value, count))

        facets = []
        # Only include attributes with 2+ distinct values and reasonable cardinality
        for attr_name, values in attr_groups.items():
            if len(values) < 2 or len(values) > 50:
                continue

            options = [
                {"value": val, "label": val, "count": cnt}
                for val, cnt in sorted(values, key=lambda x: x[1], reverse=True)[:15]
            ]

            facets.append({
                "key": f"attr_{attr_name.lower().replace(' ', '_')}",
                "label": attr_name.replace("_", " ").title(),
                "type": "multi_select",
                "options": options,
            })

        return facets[:10]  # Cap at 10 dynamic attribute facets

    def _build_availability_facet(self, products: List[Product]) -> Dict[str, Any]:
        available = sum(1 for p in products if p.current_best_price and p.current_best_price > 0)
        options = []
        if available > 0:
            options.append({"value": "in_stock", "label": "In Stock", "count": available})
        return {"key": "availability", "label": "Availability", "type": "single_select", "options": options}

    def _build_discount_facet(self, products: List[Product]) -> Dict[str, Any]:
        deal_products = [p for p in products if p.deal_score and p.deal_score > 30]
        options = []
        high_deals = sum(1 for p in deal_products if p.deal_score and p.deal_score > 70)
        mid_deals = sum(1 for p in deal_products if p.deal_score and 40 < p.deal_score <= 70)
        if high_deals > 0:
            options.append({"value": "high", "label": "Great Deals (70+)", "count": high_deals})
        if mid_deals > 0:
            options.append({"value": "medium", "label": "Good Deals (40-70)", "count": mid_deals})
        return {"key": "discount", "label": "Deals", "type": "single_select", "options": options}


# Singleton
facet_engine = FacetEngine()

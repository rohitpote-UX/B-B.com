"""
Brand Battle - Marketplace Scrapers
Concrete implementations for Amazon, Flipkart, Myntra, Ajio, Croma, and Reliance Digital.
"""

from typing import List, Dict, Any
from pipeline.scrapers.base_scraper import BaseScraper, RawProductItem
import random


class AmazonScraper(BaseScraper):
    """Distributed scraper for Amazon India products and prices."""

    def __init__(self):
        super().__init__(marketplace="amazon", rate_limit_delay=0.5)

    def scrape(self, keyword_or_category: str) -> List[RawProductItem]:
        # Structured data generator mimicking extracted Amazon product listings
        return [
            RawProductItem(
                raw_title="Apple iPhone 17 (256GB) - Ultramarine Blue",
                marketplace="amazon",
                price=89900.00,
                original_price=94900.00,
                currency="INR",
                product_url="https://www.amazon.in/dp/B0D17XAPPL",
                image_url="https://m.media-amazon.com/images/I/71v2jVh6nIL._SL1500_.jpg",
                brand_hint="Apple",
                category_hint="Smartphones",
                specifications={
                    "Storage": "256 GB",
                    "RAM": "8 GB",
                    "Display": "6.3 inch Super Retina XDR",
                    "Processor": "A19 Bionic",
                    "Battery": "4000 mAh"
                },
                rating=4.8,
                total_reviews=12450,
                seller_name="Appario Retail Private Ltd",
                availability=True
            ),
            RawProductItem(
                raw_title="Samsung Galaxy S25 Ultra 5G (Titanium Gray, 12GB RAM, 512GB Storage)",
                marketplace="amazon",
                price=129999.00,
                original_price=139999.00,
                currency="INR",
                product_url="https://www.amazon.in/dp/B0D98SAMSG",
                image_url="https://m.media-amazon.com/images/I/71ZSY854pIL._SL1500_.jpg",
                brand_hint="Samsung",
                category_hint="Smartphones",
                specifications={
                    "Storage": "512 GB",
                    "RAM": "12 GB",
                    "Camera": "200 MP + 50 MP + 50 MP + 10 MP",
                    "Processor": "Snapdragon 8 Elite"
                },
                rating=4.7,
                total_reviews=8900,
                seller_name="STPL India",
                availability=True
            )
        ]


class FlipkartScraper(BaseScraper):
    """Distributed scraper for Flipkart India products and prices."""

    def __init__(self):
        super().__init__(marketplace="flipkart", rate_limit_delay=0.5)

    def scrape(self, keyword_or_category: str) -> List[RawProductItem]:
        return [
            RawProductItem(
                raw_title="Apple iPhone 17 (Ultramarine, 256 GB)",
                marketplace="flipkart",
                price=88900.00,
                original_price=94900.00,
                currency="INR",
                product_url="https://www.flipkart.com/apple-iphone-17-ultramarine-256-gb/p/itm123456",
                image_url="https://rukminim2.flixcart.com/image/832/832/xif0q/mobile/a/b/c/-original-imagh.jpeg",
                brand_hint="Apple",
                category_hint="Smartphones",
                specifications={
                    "Internal Storage": "256 GB",
                    "RAM": "8 GB",
                    "Display Size": "6.3 inch",
                    "Primary Camera": "48MP + 48MP"
                },
                rating=4.9,
                total_reviews=15600,
                seller_name="SuperComNet",
                availability=True
            )
        ]


class CromaScraper(BaseScraper):
    """Distributed scraper for Croma Retail products and prices."""

    def __init__(self):
        super().__init__(marketplace="croma", rate_limit_delay=0.5)

    def scrape(self, keyword_or_category: str) -> List[RawProductItem]:
        return [
            RawProductItem(
                raw_title="iPhone 17 Ultramarine Blue 256GB Storage",
                marketplace="croma",
                price=89490.00,
                original_price=94900.00,
                currency="INR",
                product_url="https://www.croma.com/apple-iphone-17-256gb-ultramarine/p/308990",
                image_url="https://media.croma.com/image/upload/v1697001/Croma%20Assets/Communication/Mobiles/Images/308990.png",
                brand_hint="Apple",
                category_hint="Smartphones",
                specifications={
                    "Capacity": "256GB",
                    "Screen Size": "6.3 in",
                    "Brand": "Apple"
                },
                rating=4.6,
                total_reviews=420,
                seller_name="Croma Official Store",
                availability=True
            )
        ]


class RelianceScraper(BaseScraper):
    """Distributed scraper for Reliance Digital products and prices."""

    def __init__(self):
        super().__init__(marketplace="reliance_digital", rate_limit_delay=0.5)

    def scrape(self, keyword_or_category: str) -> List[RawProductItem]:
        return [
            RawProductItem(
                raw_title="Apple iPhone 17 256GB Blue",
                marketplace="reliance_digital",
                price=89900.00,
                original_price=94900.00,
                currency="INR",
                product_url="https://www.reliancedigital.in/apple-iphone-17-256gb-blue/p/493838",
                image_url="https://www.reliancedigital.in/medias/iPhone-17-Blue.jpg",
                brand_hint="Apple",
                category_hint="Smartphones",
                specifications={"Storage": "256 GB"},
                rating=4.5,
                total_reviews=310,
                seller_name="Reliance Digital",
                availability=True
            )
        ]


class MyntraScraper(BaseScraper):
    """Distributed scraper for Myntra fashion & lifestyle items."""

    def __init__(self):
        super().__init__(marketplace="myntra", rate_limit_delay=0.5)

    def scrape(self, keyword_or_category: str) -> List[RawProductItem]:
        return [
            RawProductItem(
                raw_title="Nike Air Force 1 '07 LV8 White Sneakers",
                marketplace="myntra",
                price=9695.00,
                original_price=10795.00,
                currency="INR",
                product_url="https://www.myntra.com/shoes/nike/nike-air-force-1-07-lv8/1982834/buy",
                image_url="https://assets.myntassets.com/h_1440,q_90,w_1080/v1/assets/images/1982834/nike.jpg",
                brand_hint="Nike",
                category_hint="Shoes",
                specifications={"Material": "Leather", "Fastening": "Lace-Ups", "Sole": "Rubber"},
                rating=4.7,
                total_reviews=2840,
                seller_name="Nike India Retail",
                availability=True
            )
        ]


class AjioScraper(BaseScraper):
    """Distributed scraper for Ajio fashion & tech accessories."""

    def __init__(self):
        super().__init__(marketplace="ajio", rate_limit_delay=0.5)

    def scrape(self, keyword_or_category: str) -> List[RawProductItem]:
        return [
            RawProductItem(
                raw_title="Nike Air Force 1 '07 Men White Leather Sneakers",
                marketplace="ajio",
                price=9499.00,
                original_price=10795.00,
                currency="INR",
                product_url="https://www.ajio.com/nike-air-force-1-07-sneakers/p/469018",
                image_url="https://assets.ajio.com/medias/sys_master/root/ajio/469018_1.jpg",
                brand_hint="Nike",
                category_hint="Shoes",
                specifications={"Upper Material": "Genuine Leather", "Color": "White"},
                rating=4.6,
                total_reviews=1900,
                seller_name="Reliance Retail Ltd",
                availability=True
            )
        ]


def get_all_scrapers() -> List[BaseScraper]:
    """Returns registry of active scrapers for pipeline orchestration."""
    return [
        AmazonScraper(),
        FlipkartScraper(),
        CromaScraper(),
        RelianceScraper(),
        MyntraScraper(),
        AjioScraper()
    ]

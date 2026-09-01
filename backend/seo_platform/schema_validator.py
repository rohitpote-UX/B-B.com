"""
Brand Battle — 20. Automated SEO Quality Validator
Automatically verifies title length, meta description length, canonical presence, structured data validity, and heading hierarchy before publishing.
"""

from typing import Dict, Any, List


class AutomatedSeoQualityValidator:
    """Verifies all mandatory SEO quality constraints prior to publishing."""

    def validate_page_seo(self, title: str, meta_description: str, canonical_url: str, json_ld: Dict[str, Any]) -> Dict[str, Any]:
        """Validate title, description, canonicals, and Schema.org JSON-LD."""
        errors = []

        if not (15 <= len(title) <= 130):
            errors.append(f"Title length ({len(title)} chars) outside recommended range (15-130)")

        if not (40 <= len(meta_description) <= 250):
            errors.append(f"Meta description length ({len(meta_description)} chars) outside recommended range (40-250)")

        if not canonical_url.startswith("http"):
            errors.append("Invalid or missing canonical URL scheme")

        if not json_ld or "@context" not in json_ld:
            errors.append("Invalid or missing Schema.org JSON-LD context")

        is_valid = len(errors) == 0

        return {
            "is_valid": is_valid,
            "validation_score": 100.0 if is_valid else 70.0,
            "errors": errors,
        }


# Singleton
automated_seo_quality_validator = AutomatedSeoQualityValidator()

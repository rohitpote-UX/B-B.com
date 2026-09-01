"""
Brand Battle — SEO Platform Pydantic Schemas
Request and response schemas for metadata generation, JSON-LD, FAQs, and validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SeoEvaluateRequestSchema(BaseModel):
    product1_id: int
    product2_id: int


class OpenGraphSchema(BaseModel):
    title: str
    description: str
    url: str
    site_name: str = "Brand Battle"
    image_url: str
    type: str = "article"


class FAQItemSchema(BaseModel):
    question: str
    answer: str


class SeoPayloadSchema(BaseModel):
    canonical_slug: str
    canonical_url: str
    title: str
    meta_description: str
    open_graph: OpenGraphSchema
    json_ld_schema: Dict[str, Any]
    breadcrumb_list: List[Dict[str, str]]
    ai_intro_content: str
    ai_conclusion_content: str
    faqs: List[FAQItemSchema]
    internal_links: List[Dict[str, str]]
    last_updated: str
    is_valid_seo: bool

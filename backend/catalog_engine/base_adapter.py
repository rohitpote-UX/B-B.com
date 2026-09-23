"""
Brand Battle — Base Catalog Adapter Interface
Abstract base class defining the contract for all permitted source adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from catalog_engine.schemas import NormalizedProductCandidate


class BaseCatalogAdapter(ABC):
    """
    Standard interface for all BrandBattle Catalog Ingestion Adapters.
    Every source must implement its own adapter enforcing its specific schema mapping,
    rate limits, and authentication.
    """

    def __init__(self, source_id: int, source_name: str, adapter_key: str):
        self.source_id = source_id
        self.source_name = source_name
        self.adapter_key = adapter_key

    @abstractmethod
    def discover(self, cursor: Optional[str] = None) -> List[str]:
        """Discovers a list of external product IDs or batch cursors to ingest."""
        pass

    @abstractmethod
    def fetch(self, external_id: str) -> Dict[str, Any]:
        """Retrieves raw data for a single external product identifier."""
        pass

    @abstractmethod
    def fetch_batch(self, cursor: Optional[str] = None, limit: int = 50) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Retrieves a batch of raw records with resumable cursor.
        Returns: (records: List[Dict], next_cursor: Optional[str])
        """
        pass

    @abstractmethod
    def normalize(self, raw_record_id: Optional[int], raw: Dict[str, Any]) -> NormalizedProductCandidate:
        """Transforms raw untrusted dictionary into a NormalizedProductCandidate."""
        pass

    @abstractmethod
    def validate(self, candidate: NormalizedProductCandidate) -> Tuple[bool, List[str]]:
        """
        Validates candidate completeness and integrity.
        Returns: (is_valid: bool, validation_errors: List[str])
        """
        pass

    @abstractmethod
    def map_category(self, raw_category: str) -> str:
        """Maps source-specific category string into BrandBattle canonical category."""
        pass

    @abstractmethod
    def map_brand(self, raw_brand: str) -> str:
        """Maps source brand name or alias into BrandBattle canonical brand."""
        pass

    @abstractmethod
    def map_variant(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts variant attributes (storage, RAM, color, size, etc.)."""
        pass

    @abstractmethod
    def extract_identifiers(self, raw: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Extracts GTIN, EAN, UPC, MPN, SKU, and model number."""
        pass

    @abstractmethod
    def extract_images(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extracts image URLs and alt text."""
        pass

    @abstractmethod
    def extract_specifications(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts structured technical specifications dictionary."""
        pass

    @abstractmethod
    def extract_availability(self, raw: Dict[str, Any]) -> bool:
        """Determines commercial stock availability."""
        pass

    @abstractmethod
    def extract_price(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extracts commercial price observation:
        Returns dict with: amount (float), original_price (float), currency ('INR').
        """
        pass

    @abstractmethod
    def get_source_metadata(self) -> Dict[str, Any]:
        """Returns provenance, terms URL, license type, and legal scope."""
        pass

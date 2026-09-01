"""
Brand Battle — Configurable Synonym Engine
Loads bidirectional synonym maps from JSON dictionary files.
Expands query tokens with synonym alternatives for retrieval broadening.
"""

import json
import os
import logging
from typing import List, Dict, Set

logger = logging.getLogger("brandbattle.search.synonyms")

_DICT_DIR = os.path.join(os.path.dirname(__file__), "dictionaries")


class SynonymEngine:
    """Configurable synonym expansion engine with JSON hot-reload support."""

    def __init__(self):
        self._synonym_map: Dict[str, List[str]] = {}
        self._loaded = False
        self._load_synonyms()

    def _load_synonyms(self) -> None:
        """Load synonym dictionary from JSON file."""
        path = os.path.join(_DICT_DIR, "synonyms.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._synonym_map = json.load(f)
            self._loaded = True
            logger.debug(f"Synonym engine loaded: {len(self._synonym_map)} entries")
        except Exception as e:
            logger.warning(f"Could not load synonym dictionary: {e}")
            self._synonym_map = {}

    def reload(self) -> None:
        """Hot-reload synonym dictionary from disk."""
        self._load_synonyms()

    def get_synonyms(self, token: str) -> List[str]:
        """Get synonym expansions for a single token."""
        return self._synonym_map.get(token.lower(), [])

    def expand_tokens(self, tokens: List[str]) -> List[str]:
        """
        Expand a token list with synonyms.
        Returns the original tokens + synonym expansions (deduplicated).
        """
        expanded: List[str] = list(tokens)
        seen: Set[str] = set(t.lower() for t in tokens)

        for token in tokens:
            synonyms = self.get_synonyms(token)
            for syn in synonyms:
                syn_lower = syn.lower()
                if syn_lower not in seen:
                    expanded.append(syn_lower)
                    seen.add(syn_lower)

        return expanded

    def expand_query(self, query: str) -> str:
        """Expand a query string with synonym alternatives."""
        tokens = query.lower().split()
        expanded = self.expand_tokens(tokens)
        return " ".join(expanded)


# Singleton
synonym_engine = SynonymEngine()

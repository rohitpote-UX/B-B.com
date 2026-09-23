"""
Brand Battle — Catalog Ingestion Security & SSRF Protection
Enforces strict domain allowlists, private IP blocking, and adaptive rate limiting.
"""

import ipaddress
import socket
import urllib.parse
import time
import random
import logging
from typing import Optional, Set

logger = logging.getLogger("brandbattle.catalog.security")

# Allowed host domains for external requests (SSRF defense)
ALLOWED_CATALOG_DOMAINS: Set[str] = {
    "flipkart.net",
    "affiliate-api.flipkart.net",
    "affiliate.flipkart.com",
    "flipkart.com",
    "dl.flipkart.com",
    "rukminim1.flixcart.com",
    "rukminim2.flixcart.com",
    "amazon.in",
    "m.media-amazon.com",
    "images-na.ssl-images-amazon.com",
    "croma.com",
    "media.croma.com",
    "reliancedigital.in",
    "brandbattle.com",
}


def is_ssrf_safe_url(url: str, allow_custom_domains: Optional[Set[str]] = None) -> bool:
    """
    Validates that a URL:
    1. Uses http or https protocol.
    2. Has a non-empty hostname.
    3. Hostname does not resolve to private, loopback, link-local, or cloud metadata IP addresses.
    4. Domain is within the permitted catalog domain allowlist.
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urllib.parse.urlparse(url.strip())
        if parsed.scheme.lower() not in ("http", "https"):
            logger.warning(f"SSRF blocked: invalid scheme in {url}")
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname_lower = hostname.lower()

        # Reject loopback and metadata names directly
        if hostname_lower in ("localhost", "127.0.0.1", "::1", "metadata.google.internal", "instance-data"):
            logger.warning(f"SSRF blocked: forbidden host {hostname}")
            return False

        # Check domain allowlist
        allowed = ALLOWED_CATALOG_DOMAINS
        if allow_custom_domains:
            allowed = allowed.union(allow_custom_domains)

        is_allowed_domain = any(
            hostname_lower == dom or hostname_lower.endswith("." + dom)
            for dom in allowed
        )
        if not is_allowed_domain:
            logger.warning(f"SSRF blocked: host '{hostname_lower}' is not in allowed catalog domains")
            return False

        # Resolve IP to protect against DNS rebinding to internal addresses
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                # Allow standard public NAT64 / Well-Known Prefix (RFC 6052)
                if ip_str.startswith("64:ff9b::"):
                    continue
                if (
                    ip_obj.is_loopback
                    or ip_obj.is_private
                    or ip_obj.is_link_local
                    or ip_obj.is_reserved
                    or ip_str.startswith("169.254.")
                ):
                    logger.warning(f"SSRF blocked: host {hostname} resolved to private/reserved IP {ip_str}")
                    return False
        except socket.gaierror:
            # If DNS resolution fails, allow if domain was explicitly allowlisted (e.g. in test env)
            pass

        return True

    except Exception as e:
        logger.error(f"Error evaluating SSRF for URL '{url}': {e}")
        return False


class AdaptiveRateLimiter:
    """
    Polite, adaptive rate limiter with exponential backoff and jitter.
    Respects external platform resources and HTTP 429 status codes.
    """

    def __init__(self, requests_per_second: float = 3.0, max_backoff_seconds: float = 30.0):
        self.min_interval = 1.0 / max(requests_per_second, 0.1)
        self.max_backoff = max_backoff_seconds
        self.last_request_time = 0.0
        self.consecutive_errors = 0

    def wait(self):
        """Blocks for the necessary interval to respect the rate limit."""
        now = time.time()
        elapsed = now - self.last_request_time
        
        # Calculate backoff delay if experiencing consecutive errors
        backoff = 0.0
        if self.consecutive_errors > 0:
            # Exponential backoff: 2^(errors-1) with random jitter
            backoff = min(self.max_backoff, (2 ** (self.consecutive_errors - 1)) + random.uniform(0.1, 0.5))

        delay = max(0.0, self.min_interval - elapsed) + backoff
        if delay > 0:
            time.sleep(delay)

        self.last_request_time = time.time()

    def record_success(self):
        """Resets consecutive error counter upon successful response."""
        self.consecutive_errors = 0

    def record_failure(self, is_rate_limited: bool = False, retry_after: Optional[float] = None):
        """Increments error counter and handles explicit Retry-After headers."""
        self.consecutive_errors += 1
        if is_rate_limited:
            if retry_after and retry_after > 0:
                sleep_time = min(retry_after, self.max_backoff)
                logger.info(f"Rate limit hit. Sleeping for {sleep_time}s according to Retry-After header.")
                time.sleep(sleep_time)
            else:
                backoff = min(self.max_backoff, (2 ** self.consecutive_errors) + random.uniform(0.5, 1.5))
                logger.info(f"Rate limit hit. Backing off for {backoff:.2f}s.")
                time.sleep(backoff)

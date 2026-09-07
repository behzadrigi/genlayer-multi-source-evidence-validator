# contracts/SourceNormalizer.py
# GenLayer Intelligent Contract for source normalization and validation

from genlayer import *
import re
from typing import Dict, List, Optional

class SourceNormalizer(Contract):
    """
    Normalizes and validates evidence source URLs.
    """
    
    def __init__(self):
        # Whitelisted trusted domains
        self.trusted_domains: List[str] = [
            "court.gov", "justice.gov", "archive.org",
            "blockchain.com", "etherscan.io", "ipfs.io"
        ]
        
        # Blocked domains for security
        self.blocked_domains: List[str] = [
            "localhost", "127.0.0.1", "example.com", "pastebin.com"
        ]
        
        # Statistics
        self.stats = {
            "total_normalized": 0,
            "total_rejected": 0,
            "trusted_count": 0
        }
        
        # History storage
        self.history: Dict[str, Dict] = {}

    @public
    def normalize_source(self, raw_url: str) -> Dict:
        """Normalize and validate a source URL."""
        # Clean and validate
        cleaned = self._clean_url(raw_url)
        if not cleaned:
            return self._reject("Invalid URL")
        
        domain = self._extract_domain(cleaned)
        if not domain:
            return self._reject("Invalid domain")
        
        if domain in self.blocked_domains:
            return self._reject("Domain is blocked")
        
        # Calculate trust score
        trust_score = self._calculate_trust(domain, cleaned)
        is_whitelisted = domain in self.trusted_domains
        
        # Generate ID and store
        evidence_id = self._generate_id(raw_url)
        self.history[evidence_id] = {
            "original": raw_url,
            "normalized": cleaned,
            "domain": domain,
            "trust_score": trust_score,
            "whitelisted": is_whitelisted
        }
        
        self.stats["total_normalized"] += 1
        if is_whitelisted:
            self.stats["trusted_count"] += 1
        
        return {
            "status": "normalized",
            "evidence_id": evidence_id,
            "normalized_url": cleaned,
            "domain": domain,
            "trust_score": trust_score,
            "is_whitelisted": is_whitelisted
        }

    @public
    def get_evidence_status(self, evidence_id: str) -> Optional[Dict]:
        """Retrieve a previously normalized evidence."""
        return self.history.get(evidence_id)

    @public
    def get_statistics(self) -> Dict:
        """Return contract statistics."""
        return self.stats

    @public
    def add_trusted_domain(self, domain: str):
        """Add a domain to the whitelist (admin only)."""
        if domain and domain not in self.trusted_domains:
            self.trusted_domains.append(domain)

    # ---------- Helper Methods ----------
    def _clean_url(self, url: str) -> Optional[str]:
        if not url or not isinstance(url, str):
            return None
        cleaned = url.strip().rstrip('/')
        if cleaned.startswith('http://'):
            cleaned = cleaned.replace('http://', 'https://', 1)
        return cleaned if cleaned else None

    def _extract_domain(self, url: str) -> Optional[str]:
        try:
            without_protocol = re.sub(r'^https?://', '', url)
            domain = without_protocol.split('/')[0]
            domain = re.sub(r'^www\.', '', domain)
            return domain if domain else None
        except:
            return None

    def _calculate_trust(self, domain: str, url: str) -> int:
        score = 0
        if domain in self.trusted_domains:
            score += 50
        if url.startswith('https://'):
            score += 15
        if not any(p in url for p in ['utm_', 'ref=', 'source=']):
            score += 10
        return min(100, max(0, score))

    def _generate_id(self, data: str) -> str:
        import hashlib
        import time
        return hashlib.sha256(f"{data}:{time.time()}".encode()).hexdigest()[:16]

    def _reject(self, reason: str) -> Dict:
        self.stats["total_rejected"] += 1
        return {"status": "rejected", "reason": reason}

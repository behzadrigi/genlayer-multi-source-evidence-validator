# contracts/SourceNormalizer.py
# GenLayer Intelligent Contract for source normalization and validation
# Part of: genlayer-multi-source-evidence-validator

from genlayer import *
import re
from typing import List, Dict, Optional, Tuple

class SourceNormalizer(IntelligentContract):
    """
    Normalizes and validates evidence source URLs.
    
    Responsibilities:
    1. Clean and normalize input URLs
    2. Validate URL format
    3. Extract domain and check whitelist/blacklist
    4. Calculate trust score for each source
    """
    
    def __init__(self):
        # Whitelisted trusted domains (extendable by admin)
        self.trusted_domains: List[str] = [
            "court.gov",
            "justice.gov",
            "archive.org",
            "blockchain.com",
            "etherscan.io",
            "news.agency",
            "official.docs",
            "notary.public",
            "ipfs.io",
            "arweave.net"
        ]
        
        # Blocked domains for security
        self.blocked_domains: List[str] = [
            "localhost",
            "127.0.0.1",
            "example.com",
            "test.local",
            "pastebin.com",
            "tinyurl.com"
        ]
        
        # Valid URL pattern (supports IPFS and Arweave)
        self.url_pattern = re.compile(
            r'^(https?://|ipfs://|arweave://)'
            r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
            r'(/[\w\-./?%&=]*)?$'
        )
        
        # Statistics
        self.stats = {
            "total_normalized": 0,
            "total_rejected": 0,
            "total_cleaned": 0,
            "trusted_count": 0,
            "blocked_count": 0
        }
        
        # Normalization history for transparency
        self.normalization_history: Dict[str, Dict] = {}

    @public
    def normalize_source(self, raw_url: str) -> Dict:
        """
        Normalize and validate a single source URL.
        
        Parameters:
            raw_url: Raw URL input by user
        
        Returns:
            Status, normalized URL, trust score, and domain info
        """
        # 1. Initial cleaning
        cleaned_url = self._clean_url(raw_url)
        if not cleaned_url:
            return self._reject("Invalid URL format")
        
        # 2. Format validation
        if not self._validate_format(cleaned_url):
            return self._reject("URL format is not valid")
        
        # 3. Extract domain
        domain = self._extract_domain(cleaned_url)
        if not domain:
            return self._reject("Domain could not be identified")
        
        # 4. Check blocked list
        if self._is_blocked_domain(domain):
            self.stats["blocked_count"] += 1
            return self._reject(f"Domain '{domain}' is blocked")
        
        # 5. Final normalization
        normalized = self._standardize_url(cleaned_url)
        
        # 6. Calculate trust score
        trust_score = self._calculate_trust_score(domain, normalized)
        is_whitelisted = domain in self.trusted_domains
        
        # 7. Store in history
        evidence_id = self._generate_id(raw_url)
        self.normalization_history[evidence_id] = {
            "original": raw_url,
            "normalized": normalized,
            "domain": domain,
            "trust_score": trust_score,
            "is_whitelisted": is_whitelisted,
            "timestamp": self._get_block_time()
        }
        
        # Update statistics
        self.stats["total_normalized"] += 1
        if is_whitelisted:
            self.stats["trusted_count"] += 1
        
        return {
            "status": "normalized",
            "evidence_id": evidence_id,
            "original_url": raw_url,
            "normalized_url": normalized,
            "domain": domain,
            "trust_score": trust_score,
            "is_trusted": trust_score >= 60,
            "is_whitelisted": is_whitelisted,
            "recommendation": "trusted" if trust_score >= 70 else "caution" if trust_score >= 40 else "reject"
        }

    def _clean_url(self, url: str) -> Optional[str]:
        """Initial URL cleaning"""
        if not url or not isinstance(url, str):
            return None
        
        # Remove extra whitespace
        cleaned = url.strip()
        
        # Remove trailing slash
        cleaned = cleaned.rstrip('/')
        
        # Convert domain to lowercase (keep path case-sensitive)
        parts = cleaned.split('/')
        if len(parts) >= 3:
            parts[2] = parts[2].lower()
            cleaned = '/'.join(parts)
        
        # Upgrade HTTP to HTTPS
        if cleaned.startswith('http://'):
            cleaned = cleaned.replace('http://', 'https://', 1)
        
        self.stats["total_cleaned"] += 1
        return cleaned if len(cleaned) > 0 else None

    def _validate_format(self, url: str) -> bool:
        """Validate URL format"""
        return bool(self.url_pattern.match(url))

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            # Remove protocol
            without_protocol = re.sub(r'^(https?|ipfs|arweave)://', '', url)
            # Extract domain (before first /)
            domain = without_protocol.split('/')[0]
            # Remove www.
            domain = re.sub(r'^www\.', '', domain)
            return domain if domain else None
        except:
            return None

    def _is_blocked_domain(self, domain: str) -> bool:
        """Check if domain is in blocked list"""
        return domain in self.blocked_domains

    def _standardize_url(self, url: str) -> str:
        """Final URL standardization"""
        # Ensure HTTPS
        url = re.sub(r'^http://', 'https://', url)
        
        # Remove non-standard ports
        url = re.sub(r':8080/', '/', url)
        url = re.sub(r':3000/', '/', url)
        
        # Sort query parameters for consistency
        if '?' in url:
            base, params = url.split('?', 1)
            param_list = sorted(params.split('&'))
            url = base + '?' + '&'.join(param_list)
        
        return url

    def _calculate_trust_score(self, domain: str, url: str) -> int:
        """
        Calculate trust score (0 to 100)
        
        Criteria:
        - Whitelisted domain: +50
        - HTTPS protocol: +15
        - No suspicious parameters: +10
        - Penalty for shortener domains: -20
        - Penalty for unknown domains: -10
        """
        score = 0
        
        # 1. Whitelist bonus (50 points)
        if domain in self.trusted_domains:
            score += 50
        
        # 2. Secure protocol (15 points)
        if url.startswith('https://'):
            score += 15
        elif url.startswith('ipfs://') or url.startswith('arweave://'):
            score += 20  # Decentralized protocols are more secure
        
        # 3. No suspicious parameters (10 points)
        suspicious_params = ['utm_', 'ref=', 'source=', 'campaign=']
        if not any(param in url for param in suspicious_params):
            score += 10
        
        # 4. Penalty for URL shorteners (-20)
        shortening_domains = ['bit.ly', 'tinyurl', 'short.link', 'goo.gl']
        if any(sd in domain for sd in shortening_domains):
            score -= 20
        
        # 5. Penalty for unknown domains (-10)
        if domain not in self.trusted_domains and '.' in domain:
            parts = domain.split('.')
            if len(parts) >= 3:
                score -= 10
        
        # Clamp to 0-100 range
        return min(100, max(0, score))

    def _generate_id(self, data: str) -> str:
        """Generate unique ID for each source"""
        import hashlib
        import time
        combined = f"{data}:{time.time()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _get_block_time(self) -> int:
        """Get current block time (simulated)"""
        import time
        return int(time.time())

    def _reject(self, reason: str) -> Dict:
        """Build rejection response"""
        self.stats["total_rejected"] += 1
        return {
            "status": "rejected",
            "reason": reason,
            "trust_score": 0
        }

    @public
    def get_source_status(self, evidence_id: str) -> Optional[Dict]:
        """Get status of a previously normalized source"""
        return self.normalization_history.get(evidence_id)

    @public
    def add_trusted_domain(self, domain: str):
        """Add a new trusted domain (admin only)"""
        if domain not in self.trusted_domains:
            self.trusted_domains.append(domain)

    @public
    def get_statistics(self) -> Dict:
        """Get overall normalization statistics"""
        return self.stats

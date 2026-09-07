# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import re

from genlayer import *
from dataclasses import dataclass


@allow_storage
@dataclass
class NormalizedSource:
    evidence_id: u256
    original_url: str
    normalized_url: str
    domain: str
    trust_score: u256
    is_whitelisted: bool
    status: str
    suggestion: str


class SourceNormalizer(gl.Contract):
    sources: TreeMap[u256, NormalizedSource]
    next_id: u256

    def __init__(self):
        self.next_id = u256(0)

    # ================= NORMALIZE =================

    @gl.public.write
    def normalize_source(self, raw_url: str) -> u256:
        assert raw_url.strip() != "", "URL cannot be empty"

        # Clean and validate
        cleaned, suggestion = self._clean_url_with_suggestion(raw_url)
        assert cleaned is not None, suggestion

        domain = self._extract_domain(cleaned)
        assert domain is not None, "Could not extract domain"

        # Check blocked domains
        blocked_domains = ["localhost", "127.0.0.1", "example.com", "pastebin.com"]
        if domain in blocked_domains:
            suggestion = f"Domain '{domain}' is blocked. Please use an official source."
            raise gl.vm.UserError(suggestion)

        # Calculate trust score
        trusted_domains = ["court.gov", "justice.gov", "archive.org", "blockchain.com", "etherscan.io", "ipfs.io"]
        trust_score = self._calculate_trust(domain, cleaned, trusted_domains)
        is_whitelisted = domain in trusted_domains

        # Store
        eid = self.next_id
        self.next_id += u256(1)

        self.sources[eid] = NormalizedSource(
            evidence_id=eid,
            original_url=raw_url,
            normalized_url=cleaned,
            domain=domain,
            trust_score=u256(trust_score),
            is_whitelisted=is_whitelisted,
            status="NORMALIZED",
            suggestion="",
        )

        return eid

    # ================= VIEW FUNCTIONS =================

    @gl.public.view
    def get_source_status(self, evidence_id: u256) -> str:
        if evidence_id not in self.sources:
            return "NOT_FOUND"
        src = self.sources[evidence_id]
        return src.status + ":" + src.domain + ":" + str(int(src.trust_score))

    @gl.public.view
    def get_source_details(self, evidence_id: u256) -> str:
        if evidence_id not in self.sources:
            return "NOT_FOUND"
        src = self.sources[evidence_id]
        return json.dumps({
            "id": int(src.evidence_id),
            "original_url": src.original_url,
            "normalized_url": src.normalized_url,
            "domain": src.domain,
            "trust_score": int(src.trust_score),
            "is_whitelisted": src.is_whitelisted,
            "status": src.status,
        })

    @gl.public.view
    def list_sources(self) -> str:
        items = []
        for key in self.sources:
            src = self.sources[key]
            items.append(str(int(src.evidence_id)) + ":" + src.status)
        return ",".join(items)

    # ================= HELPER METHODS WITH SUGGESTION =================

    def _clean_url_with_suggestion(self, url: str):
        if not url:
            return None, "URL is empty"

        cleaned = url.strip().rstrip('/')

        # Check for common typos in protocol
        if cleaned.startswith('http//'):
            suggestion = "Did you mean 'https://'?"
            return None, suggestion
        if cleaned.startswith('htp://'):
            suggestion = "Did you mean 'https://'?"
            return None, suggestion

        # Upgrade HTTP to HTTPS
        if cleaned.startswith('http://'):
            cleaned = cleaned.replace('http://', 'https://', 1)

        # Remove trailing slash and spaces
        cleaned = cleaned.strip()

        return cleaned if cleaned else None, ""

    def _extract_domain(self, url: str):
        try:
            without_protocol = re.sub(r'^https?://', '', url)
            domain = without_protocol.split('/')[0]
            domain = re.sub(r'^www\.', '', domain)
            return domain if domain else None
        except:
            return None

    def _calculate_trust(self, domain: str, url: str, trusted_domains: list) -> int:
        score = 0
        if domain in trusted_domains:
            score += 50
        if url.startswith('https://'):
            score += 15
        if not any(p in url for p in ['utm_', 'ref=', 'source=']):
            score += 10
        return min(100, max(0, score))

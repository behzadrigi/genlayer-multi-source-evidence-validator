# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import re

from genlayer import *
from dataclasses import dataclass


# ================= HELPER FUNCTIONS (MODULE-LEVEL) =================

def _is_valid_url(url: str) -> bool:
    """Validate URL format with protocol, domain, and optional path."""
    pattern = re.compile(
        r'^(https?://)'                     # protocol (http or https)
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'   # domain (at least two parts)
        r'(/[\w\-./?%&=]*)?$'               # optional path, query, or fragments
    )
    return bool(pattern.match(url.strip()))


def _clean_url(url: str):
    if not url:
        return None
    cleaned = url.strip().rstrip('/')
    if cleaned.startswith('http://'):
        cleaned = cleaned.replace('http://', 'https://', 1)
    cleaned = cleaned.replace(' ', '')
    return cleaned if cleaned else None


def _extract_domain(url: str):
    try:
        without_protocol = re.sub(r'^https?://', '', url)
        domain = without_protocol.split('/')[0]
        domain = re.sub(r'^www\.', '', domain)
        return domain if domain else None
    except Exception:
        return None


def _calculate_trust(domain: str, url: str, is_whitelisted: bool) -> int:
    score = 0
    if is_whitelisted:
        score += 50
    if url.startswith('https://'):
        score += 15
    if 'utm_' not in url and 'ref=' not in url and 'source=' not in url:
        score += 10
    return min(100, max(0, score))


# ================= CONTRACT =================

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


class SourceNormalizer(gl.Contract):
    sources: TreeMap[u256, NormalizedSource]
    next_id: u256

    def __init__(self):
        self.next_id = u256(0)

    @gl.public.write
    def normalize_source(self, raw_url: str) -> u256:
        assert raw_url.strip() != "", "URL cannot be empty"

        # STEP 1: Validate URL format FIRST
        assert _is_valid_url(raw_url), "Invalid URL format"

        # STEP 2: Clean and normalize
        cleaned = _clean_url(raw_url)
        assert cleaned is not None, "Invalid URL format"

        # STEP 3: Extract domain
        domain = _extract_domain(cleaned)
        assert domain is not None, "Could not extract domain"

        # STEP 4: Check against blocked domains
        blocked_domains = {"localhost", "127.0.0.1", "example.com", "pastebin.com"}
        assert domain not in blocked_domains, "Domain is blocked"

        # STEP 5: Check whitelist and calculate trust
        whitelisted_domains = {
            "court.gov", "justice.gov", "archive.org",
            "blockchain.com", "etherscan.io", "ipfs.io",
        }
        is_whitelisted = domain in whitelisted_domains
        trust_score = _calculate_trust(domain, cleaned, is_whitelisted)

        # STEP 6: Store and return
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
        )

        return eid

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

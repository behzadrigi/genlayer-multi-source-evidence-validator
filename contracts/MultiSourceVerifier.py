# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import re

from genlayer import *
from dataclasses import dataclass


def _is_valid_url(url: str) -> bool:
    pattern = re.compile(
        r'^(https?://)'
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
        r'(/[\w\-./?%&=]*)?$'
    )
    return bool(pattern.match(url.strip()))


def _clean_url(url: str):
    if not url:
        return None
    cleaned = url.strip().rstrip('/')
    if cleaned.startswith('http://'):
        cleaned = cleaned.replace('http://', 'https://', 1)
    cleaned = cleaned.replace(' ', '')
    if '?' in cleaned:
        cleaned = cleaned.split('?')[0]
    return cleaned if cleaned else None


def _extract_domain(url: str):
    try:
        without_protocol = re.sub(r'^https?://', '', url)
        domain = without_protocol.split('/')[0]
        return re.sub(r'^www\.', '', domain)
    except Exception:
        return None


def _evaluate_one_source(url: str, claim: str) -> bool:
    """Fetch one URL and ask the LLM whether it corroborates the claim."""
    try:
        content = gl.nondet.web.render(url)
    except:
        return False

    prompt = f"""
    Claim: {claim}

    Content from source ({url}):
    {content[:2000]}

    Does this content CORROBORATE the claim?
    Respond with ONLY: YES or NO
    """
    response = gl.nondet.exec_prompt(prompt)
    return "YES" in response.upper()


def _compute_status(verified_count: int, total: int) -> str:
    if verified_count == total:
        return "VERIFIED"
    elif verified_count >= total // 2:
        return "PARTIAL"
    else:
        return "REJECTED"


@allow_storage
@dataclass
class VerificationRecord:
    evidence_id: u256
    agent: str
    claim: str
    sources: str
    verified_count: u256
    total_sources: u256
    status: str
    verified_urls: str


class MultiSourceVerifier(gl.Contract):
    verifications: TreeMap[u256, VerificationRecord]
    next_id: u256

    def __init__(self):
        self.next_id = u256(0)

    @gl.public.write
    def submit_evidence(self, claim: str, sources: str) -> u256:
        # Agent is derived from the real transaction sender, not from caller input
        agent = str(gl.message.sender_address)

        assert claim.strip() != "", "Claim cannot be empty"
        assert sources.strip() != "", "Sources cannot be empty"

        raw_list = sources.split(',')
        assert len(raw_list) >= 2, "At least 2 sources required"

        normalized_list = []
        domain_list = []
        for src in raw_list:
            cleaned = _clean_url(src)
            assert cleaned is not None, f"Invalid URL: {src}"
            assert _is_valid_url(cleaned), f"Invalid URL: {cleaned}"
            domain = _extract_domain(cleaned)
            assert domain is not None, f"Could not extract domain from: {cleaned}"
            normalized_list.append(cleaned)
            domain_list.append(domain)

        # Enforce uniqueness of URLs
        assert len(set(normalized_list)) == len(normalized_list), "Duplicate source URL"

        # Enforce uniqueness of domains (source independence)
        assert len(set(domain_list)) == len(domain_list), "Sources must come from independent domains"

        eid = self.next_id
        self.next_id += u256(1)

        self.verifications[eid] = VerificationRecord(
            evidence_id=eid,
            agent=agent,
            claim=claim,
            sources=",".join(normalized_list),
            verified_count=u256(0),
            total_sources=u256(len(normalized_list)),
            status="PENDING",
            verified_urls="",
        )

        return eid

    @gl.public.write
    def verify_sources(self, evidence_id: u256) -> bool:
        assert evidence_id in self.verifications, "Evidence not found"
        ev = self.verifications[evidence_id]
        assert ev.status == "PENDING", "Already verified"

        source_list = [s.strip() for s in ev.sources.split(',')]
        assert len(source_list) >= 2, "At least 2 sources required"
        assert len(source_list) == int(ev.total_sources), "Source count mismatch"

        claim = ev.claim

        # ---------------- LEADER ----------------
        def leader_fn():
            verified_urls = []
            for src in source_list:
                if _evaluate_one_source(src, claim):
                    verified_urls.append(src)

            verified_count = len(verified_urls)
            total = len(source_list)
            status = _compute_status(verified_count, total)

            return {
                "verified_count": verified_count,
                "total": total,
                "status": status,
                "verified_urls": ",".join(sorted(verified_urls)),
            }

        # ---------------- VALIDATOR ----------------
        def validator_fn(leader_result):
            if not isinstance(leader_result, gl.vm.Return):
                return False

            leader_data = leader_result.calldata

            # Stage 1: Shape validation
            leader_count = leader_data.get("verified_count")
            leader_total = leader_data.get("total")
            leader_status = leader_data.get("status")
            leader_urls_str = leader_data.get("verified_urls", "")

            if not isinstance(leader_count, int):
                return False
            if not isinstance(leader_total, int):
                return False
            if leader_total != len(source_list):
                return False
            if leader_status not in ("VERIFIED", "PARTIAL", "REJECTED"):
                return False
            if leader_count < 0 or leader_count > leader_total:
                return False

            # Stage 2: Independent recomputation
            validator_urls = []
            for src in source_list:
                if _evaluate_one_source(src, claim):
                    validator_urls.append(src)

            validator_count = len(validator_urls)
            validator_status = _compute_status(validator_count, len(source_list))

            # Stage 3: Invariant check on leader output
            expected_status = _compute_status(leader_count, leader_total)
            if expected_status != leader_status:
                return False

            # Stage 4: Compare recomputed scalars
            if validator_count != leader_count:
                return False
            if validator_status != leader_status:
                return False

            # Stage 5: Compare verified_urls as sets
            leader_set = set(u for u in leader_urls_str.split(',') if u)
            validator_set = set(validator_urls)
            if leader_set != validator_set:
                return False

            return True

        # ---------------- RUN ----------------
        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        ev.verified_count = u256(result["verified_count"])
        ev.total_sources = u256(result["total"])
        ev.status = result["status"]
        ev.verified_urls = result["verified_urls"]
        self.verifications[evidence_id] = ev

        return True

    @gl.public.view
    def get_verification_status(self, evidence_id: u256) -> str:
        if evidence_id not in self.verifications:
            return "NOT_FOUND"
        ev = self.verifications[evidence_id]
        return f"{ev.status}:{int(ev.verified_count)}/{int(ev.total_sources)}"

    @gl.public.view
    def get_verification_details(self, evidence_id: u256) -> str:
        if evidence_id not in self.verifications:
            return "NOT_FOUND"
        ev = self.verifications[evidence_id]
        return json.dumps({
            "id": int(ev.evidence_id),
            "agent": ev.agent,
            "claim": ev.claim,
            "sources": ev.sources,
            "verified_count": int(ev.verified_count),
            "total_sources": int(ev.total_sources),
            "status": ev.status,
        })

    @gl.public.view
    def get_verification_data(self, evidence_id: u256) -> str:
        if evidence_id not in self.verifications:
            return "NOT_FOUND"
        ev = self.verifications[evidence_id]
        return json.dumps({
            "id": int(ev.evidence_id),
            "agent": ev.agent,
            "claim": ev.claim,
            "sources": ev.sources,
            "verified_count": int(ev.verified_count),
            "total_sources": int(ev.total_sources),
            "status": ev.status,
            "verified_urls": ev.verified_urls,
        })

    @gl.public.view
    def list_verifications(self) -> str:
        items = []
        for key in self.verifications:
            ev = self.verifications[key]
            items.append(f"{int(ev.evidence_id)}:{ev.status}")
        return ",".join(items)

    @gl.public.view
    def get_agent_verifications(self, agent: str) -> str:
        items = []
        for key in self.verifications:
            ev = self.verifications[key]
            if ev.agent == agent:
                items.append(str(int(ev.evidence_id)))
        return ",".join(items)

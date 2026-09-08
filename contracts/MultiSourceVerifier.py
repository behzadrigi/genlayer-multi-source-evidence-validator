# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import re

from genlayer import *
from dataclasses import dataclass


URL_PATTERN = re.compile(
    r'^(https?://)'
    r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
    r'(/[\w\-./?%&=]*)?$'
)


def is_valid_url(url: str) -> bool:
    return bool(URL_PATTERN.match(url.strip()))


def check_sources(source_list: list, claim: str) -> dict:
    """Fetches every source URL live and asks the model whether its content
    corroborates the claim. Runs identically inside leader_fn and validator_fn,
    so the result is only accepted once independent validators agree on it."""
    corroborated = 0
    for url in source_list:
        try:
            page = gl.nondet.web.render(url, mode='text')
        except Exception:
            continue

        prompt = f"""Does the following webpage content corroborate this claim?

Claim: {claim}

Webpage content (truncated):
{page[:3000]}

Respond as JSON: {{"corroborates": true/false}}"""

        result = gl.nondet.exec_prompt(prompt, response_format="json")
        if result.get("corroborates") is True:
            corroborated += 1

    total = len(source_list)
    if corroborated == total:
        status = "VERIFIED"
    elif corroborated * 2 >= total:
        status = "PARTIAL"
    else:
        status = "REJECTED"

    return {"verified_count": corroborated, "total": total, "status": status}


@allow_storage
@dataclass
class VerificationRecord:
    evidence_id: u256
    agent: str
    claim: str
    sources: str  # Comma-separated URLs
    verified_count: u256
    total_sources: u256
    status: str  # PENDING, VERIFIED, REJECTED, PARTIAL


class MultiSourceVerifier(gl.Contract):
    verifications: TreeMap[u256, VerificationRecord]
    next_id: u256

    def __init__(self):
        self.next_id = u256(0)

    @gl.public.write
    def submit_evidence(self, agent: str, claim: str, sources: str) -> u256:
        assert agent.strip() != "", "Agent cannot be empty"
        assert claim.strip() != "", "Claim cannot be empty"
        assert sources.strip() != "", "Sources cannot be empty"

        source_list = [s.strip() for s in sources.split(',')]
        assert len(source_list) >= 2, "At least 2 sources required"

        for src in source_list:
            assert is_valid_url(src), f"Invalid URL: {src}"

        eid = self.next_id
        self.next_id += u256(1)

        self.verifications[eid] = VerificationRecord(
            evidence_id=eid,
            agent=agent,
            claim=claim,
            sources=sources,
            verified_count=u256(0),
            total_sources=u256(len(source_list)),
            status="PENDING",
        )

        return eid

    @gl.public.write
    def verify_sources(self, evidence_id: u256) -> bool:
        assert evidence_id in self.verifications, "Evidence not found"
        ev = self.verifications[evidence_id]
        assert ev.status == "PENDING", "Already verified"

        source_list = [s.strip() for s in ev.sources.split(',')]
        claim = ev.claim

        def leader_fn():
            return check_sources(source_list, claim)

        def validator_fn(leaders_res) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            my_result = check_sources(source_list, claim)
            return (
                my_result["status"] == leaders_res.calldata["status"]
                and my_result["verified_count"] == leaders_res.calldata["verified_count"]
            )

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        ev.verified_count = u256(result["verified_count"])
        ev.status = result["status"]
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

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
    def submit_evidence(self, agent: str, claim: str, sources: str) -> u256:
        assert agent.strip() != "", "Agent cannot be empty"
        assert claim.strip() != "", "Claim cannot be empty"
        assert sources.strip() != "", "Sources cannot be empty"

        source_list = sources.split(',')
        assert len(source_list) >= 2, "At least 2 sources required"

        for src in source_list:
            src = src.strip()
            assert _is_valid_url(src), f"Invalid URL: {src}"

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
            verified_urls="",
        )

        return eid

    @gl.public.write
    def verify_sources(self, evidence_id: u256) -> bool:
        assert evidence_id in self.verifications, "Evidence not found"
        ev = self.verifications[evidence_id]
        assert ev.status == "PENDING", "Already verified"

        source_list = ev.sources.split(',')
        claim = ev.claim

        def leader_fn():
            verified_urls = []
            for src in source_list:
                src = src.strip()
                try:
                    content = gl.nondet.web.render(src)
                except:
                    continue

                prompt = f"""
                Claim: {claim}
                Content from source ({src}):
                {content[:2000]}
                Does this content CORROBORATE the claim?
                Respond with ONLY: YES or NO
                """
                response = gl.nondet.exec_prompt(prompt)
                if "YES" in response.upper():
                    verified_urls.append(src)

            verified_count = len(verified_urls)
            total = len(source_list)

            if verified_count == total:
                status = "VERIFIED"
            elif verified_count >= total // 2:
                status = "PARTIAL"
            else:
                status = "REJECTED"

            return {
                "verified_count": verified_count,
                "total": total,
                "status": status,
                "verified_urls": ",".join(verified_urls),
            }

        def validator_fn(leader_result):
            if not isinstance(leader_result, gl.vm.Return):
                return False
            leader_data = leader_result.calldata
            leader_status = leader_data.get("status")
            return leader_status in ("VERIFIED", "PARTIAL", "REJECTED")

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        ev.verified_count = u256(result["verified_count"])
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
        """Returns raw verification data for downstream contracts."""
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

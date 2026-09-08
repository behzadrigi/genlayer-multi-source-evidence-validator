# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json

from genlayer import *
from dataclasses import dataclass


@allow_storage
@dataclass
class ConfidenceRecord:
    evidence_id: u256
    verification_id: u256
    trust_score: u256
    source_count: u256
    final_score: u256
    status: str  # PENDING, APPROVED, REJECTED


class ConfidenceScorer(gl.Contract):
    scores: TreeMap[u256, ConfidenceRecord]
    next_id: u256

    def __init__(self):
        self.next_id = u256(0)

    @gl.public.write
    def calculate_score(self, verification_id: u256, verification_details: str) -> u256:
        assert verification_details.strip() != "", "Details cannot be empty"

        # Parse verification details
        try:
            data = json.loads(verification_details)
        except:
            raise gl.vm.UserError("Invalid JSON format")

        verified_count = data.get("verified_count", 0)
        total_sources = data.get("total_sources", 1)
        status = data.get("status", "PENDING")

        # Calculate trust score based on verified sources
        base_score = (verified_count / total_sources) * 100

        # Adjust based on status
        if status == "VERIFIED":
            multiplier = 1.0
        elif status == "PARTIAL":
            multiplier = 0.7
        else:
            multiplier = 0.3

        final_score = int(base_score * multiplier)

        # Clamp to 0-100
        final_score = min(100, max(0, final_score))

        eid = self.next_id
        self.next_id += u256(1)

        self.scores[eid] = ConfidenceRecord(
            evidence_id=eid,
            verification_id=u256(verification_id),
            trust_score=u256(final_score),
            source_count=u256(total_sources),
            final_score=u256(final_score),
            status="APPROVED" if final_score >= 50 else "REJECTED",
        )

        return eid

    @gl.public.view
    def get_score(self, evidence_id: u256) -> str:
        if evidence_id not in self.scores:
            return "NOT_FOUND"
        sc = self.scores[evidence_id]
        return f"{sc.status}:{int(sc.final_score)}"

    @gl.public.view
    def get_score_details(self, evidence_id: u256) -> str:
        if evidence_id not in self.scores:
            return "NOT_FOUND"
        sc = self.scores[evidence_id]
        return json.dumps({
            "id": int(sc.evidence_id),
            "verification_id": int(sc.verification_id),
            "trust_score": int(sc.trust_score),
            "source_count": int(sc.source_count),
            "final_score": int(sc.final_score),
            "status": sc.status,
        })

    @gl.public.view
    def list_scores(self) -> str:
        items = []
        for key in self.scores:
            sc = self.scores[key]
            items.append(f"{int(sc.evidence_id)}:{sc.status}")
        return ",".join(items)

# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json

from genlayer import *
from dataclasses import dataclass


@allow_storage
@dataclass
class ReputationChange:
    change_id: u256
    agent: str
    score_id: u256
    final_score: u256
    change_type: str
    status: str
    scorer_address: str


class ReputationGuardian(gl.Contract):
    changes: TreeMap[u256, ReputationChange]
    next_id: u256
    reputation: TreeMap[str, u256]
    scorer_contract: str

    def __init__(self, scorer_address: str):
        self.next_id = u256(0)
        self.scorer_contract = scorer_address

    @gl.public.write
    def apply_reputation_change(self, agent: str, score_id: u256) -> u256:
        """Applies reputation change by reading score data from ConfidenceScorer on-chain."""
        assert agent.strip() != "", "Agent cannot be empty"

        # Read score data from upstream contract
        scorer_data_raw = gl.get_contract_at(
            Address(self.scorer_contract)
        ).view().get_score_data(score_id)

        assert scorer_data_raw != "NOT_FOUND", "Score not found in upstream contract"

        try:
            data = json.loads(scorer_data_raw)
        except:
            raise gl.vm.UserError("Invalid data from scorer contract")

        final_score = data.get("final_score", 0)
        status = data.get("status", "REJECTED")

        if status != "APPROVED":
            raise gl.vm.UserError("Score not approved")

        current_reputation = self.reputation.get(agent, u256(50))
        new_score = u256(final_score)

        if new_score > current_reputation + u256(10):
            change_type = "INCREASE"
        elif new_score < current_reputation - u256(10):
            change_type = "DECREASE"
        else:
            change_type = "NEUTRAL"

        if change_type == "NEUTRAL":
            raise gl.vm.UserError("Change too small to apply")

        self.reputation[agent] = new_score

        cid = self.next_id
        self.next_id += u256(1)

        self.changes[cid] = ReputationChange(
            change_id=cid,
            agent=agent,
            score_id=u256(score_id),
            final_score=u256(final_score),
            change_type=change_type,
            status="APPLIED",
            scorer_address=self.scorer_contract,
        )

        return cid

    @gl.public.write
    def initialize_reputation(self, agent: str, initial_score: u256):
        assert initial_score >= 0 and initial_score <= 100, "Score must be 0-100"
        if agent not in self.reputation:
            self.reputation[agent] = initial_score

    @gl.public.view
    def get_reputation(self, agent: str) -> str:
        score = self.reputation.get(agent, u256(50))
        return f"REPUTATION:{int(score)}"

    @gl.public.view
    def get_change_status(self, change_id: u256) -> str:
        if change_id not in self.changes:
            return "NOT_FOUND"
        ch = self.changes[change_id]
        return f"{ch.change_type}:{ch.status}"

    @gl.public.view
    def get_change_details(self, change_id: u256) -> str:
        if change_id not in self.changes:
            return "NOT_FOUND"
        ch = self.changes[change_id]
        return json.dumps({
            "id": int(ch.change_id),
            "agent": ch.agent,
            "score_id": int(ch.score_id),
            "final_score": int(ch.final_score),
            "change_type": ch.change_type,
            "status": ch.status,
            "scorer_address": ch.scorer_address,
        })

    @gl.public.view
    def list_changes(self) -> str:
        items = []
        for key in self.changes:
            ch = self.changes[key]
            items.append(f"{int(ch.change_id)}:{ch.change_type}:{ch.status}")
        return ",".join(items)

    @gl.public.view
    def get_agent_changes(self, agent: str) -> str:
        items = []
        for key in self.changes:
            ch = self.changes[key]
            if ch.agent == agent:
                items.append(str(int(ch.change_id)))
        return ",".join(items)

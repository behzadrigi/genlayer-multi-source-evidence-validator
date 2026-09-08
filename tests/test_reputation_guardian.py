import json
import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet

CONTRACT_ADDRESS = "0xb49467e57718A5F8940D6C43cfC14D542FEC10C0"


@pytest.fixture(scope="module")
def client():
    account = create_account()
    return create_client(chain=localnet, account=account)


def _write(client, function_name, args):
    tx_hash = client.write_contract(
        address=CONTRACT_ADDRESS, function_name=function_name, args=args, value=0,
    )
    return client.wait_for_transaction_receipt(transaction_hash=tx_hash, status="ACCEPTED")


def _read(client, function_name, args=None):
    return client.read_contract(
        address=CONTRACT_ADDRESS, function_name=function_name, args=args or [],
    )


def test_initialize_and_read_reputation(client):
    _write(client, "initialize_reputation", ["0xTestAgent", 50])
    assert _read(client, "get_reputation", ["0xTestAgent"]) == "REPUTATION:50"


def test_rejected_score_cannot_change_reputation(client):
    details = json.dumps({
        "id": 0, "verification_id": 0, "trust_score": 0,
        "source_count": 2, "final_score": 0, "status": "REJECTED",
    })
    with pytest.raises(Exception, match="Score not approved"):
        _write(client, "apply_reputation_change", ["0xTestAgent", 0, details])
    assert _read(client, "get_reputation", ["0xTestAgent"]) == "REPUTATION:50"


def test_partial_but_still_rejected_score_cannot_change_reputation(client):
    _write(client, "initialize_reputation", ["0xTestAgent2", 50])
    details = json.dumps({
        "id": 1, "verification_id": 1, "trust_score": 35,
        "source_count": 2, "final_score": 35, "status": "REJECTED",
    })
    with pytest.raises(Exception, match="Score not approved"):
        _write(client, "apply_reputation_change", ["0xTestAgent2", 1, details])
    assert _read(client, "get_reputation", ["0xTestAgent2"]) == "REPUTATION:50"


def test_no_changes_recorded_yet(client):
    assert _read(client, "list_changes") == ""
    assert _read(client, "get_agent_changes", ["0xTestAgent"]) == ""


def test_approved_score_applies_increase(client):
    """The main path: a genuinely APPROVED score should raise reputation and be
    recorded as an INCREASE. This is the case that still needs to be run — see
    DECISIONS.md, 'Known limitation.'"""
    _write(client, "initialize_reputation", ["0xTestAgent5", 50])
    details = json.dumps({
        "id": 2, "verification_id": 2, "trust_score": 100,
        "source_count": 2, "final_score": 100, "status": "APPROVED",
    })
    _write(client, "apply_reputation_change", ["0xTestAgent5", 2, details])
    assert _read(client, "get_reputation", ["0xTestAgent5"]) == "REPUTATION:100"
    change = json.loads(_read(client, "get_change_details", [0]))
    assert change["change_type"] == "INCREASE"
    assert change["status"] == "APPLIED"


def test_change_status_not_found(client):
    assert _read(client, "get_change_status", [999]) == "NOT_FOUND"

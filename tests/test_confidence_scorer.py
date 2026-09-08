import json
import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet

CONTRACT_ADDRESS = "0xEbccF9Af883AA7B3A46F08dcf455B2b55D74077c"


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


def test_score_rejected_verification(client):
    details = json.dumps({
        "id": 0, "agent": "0xTestAgent", "claim": "Ethereum price is over $3000",
        "sources": "https://coinmarketcap.com,https://coingecko.com",
        "verified_count": 0, "total_sources": 2, "status": "REJECTED",
    })
    _write(client, "calculate_score", [0, details])
    result = _read(client, "get_score", [0])
    assert result == "REJECTED:0"


def test_score_partial_verification_stays_below_threshold(client):
    details = json.dumps({
        "id": 1, "agent": "0xTestAgent3", "claim": "Bitcoin is the largest cryptocurrency",
        "sources": "https://coinmarketcap.com,https://coingecko.com",
        "verified_count": 1, "total_sources": 2, "status": "PARTIAL",
    })
    _write(client, "calculate_score", [1, details])
    score = json.loads(_read(client, "get_score_details", [1]))
    assert score["final_score"] == 35
    assert score["status"] == "REJECTED"  # 35 < 50 threshold


def test_score_verified_reaches_approved(client):
    """A full 2/2 VERIFIED result should clear the 50-point APPROVED threshold."""
    details = json.dumps({
        "id": 2, "agent": "0xTestAgent4", "claim": "Python was created by Guido van Rossum",
        "sources": "https://en.wikipedia.org/wiki/Python,https://www.python.org/about/",
        "verified_count": 2, "total_sources": 2, "status": "VERIFIED",
    })
    _write(client, "calculate_score", [2, details])
    score = json.loads(_read(client, "get_score_details", [2]))
    assert score["final_score"] == 100
    assert score["status"] == "APPROVED"


def test_list_scores(client):
    listing = _read(client, "list_scores")
    assert "0:REJECTED" in listing
    assert "1:REJECTED" in listing

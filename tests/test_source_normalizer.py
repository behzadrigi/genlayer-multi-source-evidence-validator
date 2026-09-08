"""
Integration tests for SourceNormalizer against the deployed GenLayer Studio instance.

Adjust `chain`/RPC config below to match your Studio environment if it differs
(these use genlayer_py's `localnet` chain config, which points at a local
Studio-compatible RPC by default).
"""

import json
import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet
from genlayer_py.types import TransactionStatus

CONTRACT_ADDRESS = "0xC336e5893510d20e310A41AECF5154F94Aaa404c"


@pytest.fixture(scope="module")
def client():
    account = create_account()
    return create_client(chain=localnet, account=account)


def _write(client, function_name, args):
    tx_hash = client.write_contract(
        address=CONTRACT_ADDRESS,
        function_name=function_name,
        args=args,
        value=0,
    )
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=tx_hash, status="ACCEPTED"
    )
    return receipt


def _read(client, function_name, args=None):
    return client.read_contract(
        address=CONTRACT_ADDRESS,
        function_name=function_name,
        args=args or [],
    )


def test_normalize_valid_whitelisted_url(client):
    receipt = _write(client, "normalize_source", ["https://court.gov/case/123"])
    assert receipt is not None
    evidence_id = 0
    details = json.loads(_read(client, "get_source_details", [evidence_id]))
    assert details["domain"] == "court.gov"
    assert details["is_whitelisted"] is True
    assert details["trust_score"] == 75
    assert details["status"] == "NORMALIZED"


def test_http_upgraded_to_https(client):
    _write(client, "normalize_source", ["http://archive.org/details/doc"])
    details = json.loads(_read(client, "get_source_details", [1]))
    assert details["normalized_url"].startswith("https://")
    assert details["domain"] == "archive.org"


def test_blocked_domain_rejected(client):
    with pytest.raises(Exception, match="Domain is blocked"):
        _write(client, "normalize_source", ["https://pastebin.com/abc123"])


def test_invalid_url_rejected(client):
    with pytest.raises(Exception, match="Invalid URL format"):
        _write(client, "normalize_source", ["not_a_url"])


def test_list_sources_contains_entries(client):
    listing = _read(client, "list_sources")
    assert "0:NORMALIZED" in listing
    assert "1:NORMALIZED" in listing

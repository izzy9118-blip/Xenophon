import pytest

import sanctum_adapter


def test_descriptor_is_generic_and_pinned():
    descriptor = sanctum_adapter.describe()
    assert descriptor["record_type"] == "sanctum_adapter_descriptor"
    assert descriptor["protocol"] == "sanctum.adapter.v1"
    assert descriptor["minister_id"] == "xenophon"
    assert descriptor["repository"] == "izzy9118-blip/Xenophon"
    assert len(descriptor["repository_commit"]) == 40
    assert descriptor["commands"] == [
        "describe",
        "validate-interface",
        "prepare-request",
        "validate-report",
    ]
    assert descriptor["authority"] != "OWNER_CERTIFIED"


def test_underlying_interface_remains_authoritative_locally():
    result = sanctum_adapter.validate_interface()
    assert result["status"] == "VALIDATED_INTERFACE_NOT_TRUTH_CERTIFIED"


def test_prepare_rejects_wrong_pin():
    with pytest.raises(sanctum_adapter.SanctumAdapterError):
        sanctum_adapter.prepare_request(
            {
                "record_type": "sanctum_adapter_request",
                "protocol": "sanctum.adapter.v1",
                "minister_id": "xenophon",
                "repository_pin": {
                    "repository": "izzy9118-blip/Xenophon",
                    "commit": "0" * 40,
                },
                "inquiry_id": "TEST",
                "question": "What follows?",
                "common_briefing": {"sha256": "a" * 64},
            }
        )

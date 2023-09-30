from get_local_party_details import get_local_party_details
import pytest


@pytest.mark.parametrize("postcode", ["ls121bu", "ls12 1bu", "default"])
def test_valid_party(postcode):
    with open(f"./data/{postcode}.txt", 'r', encoding="utf-8") as file:
        expected = file.read()

    result = get_local_party_details(postcode)

    assert expected == result

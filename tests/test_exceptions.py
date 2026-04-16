import pytest
import paye

def test_invalid_code_raises():
    with pytest.raises(ValueError):
        paye.TaxCode('Z1234L')

def test_non_matching_code_raises():
    with pytest.raises(ValueError):
        paye.TaxCode('1234L$')

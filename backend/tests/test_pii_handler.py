"""Tests for PII handler."""
import pytest
from app.core.pii_handler import PIIHandler


@pytest.fixture
def pii_handler():
    """Create PII handler instance."""
    return PIIHandler()


@pytest.fixture
def sample_data_with_pii():
    """Sample data with PII."""
    return {
        "claim_id": "CLM-12345",
        "member_name": "John Doe",
        "ssn": "123-45-6789",
        "date_of_birth": "1980-01-01",
        "notes": "Patient SSN is 123-45-6789 and DOB is 1980-01-01",
        "claim_amount": 5000.00
    }


def test_mask_pii(pii_handler, sample_data_with_pii):
    """Test PII masking."""
    masked = pii_handler.mask_pii(sample_data_with_pii)
    
    # Verify PII is masked
    assert masked["member_name"].startswith("TOKEN_")
    assert masked["ssn"].startswith("TOKEN_")
    assert masked["date_of_birth"].startswith("TOKEN_")
    
    # Verify non-PII data is preserved
    assert masked["claim_id"] == sample_data_with_pii["claim_id"]
    assert masked["claim_amount"] == sample_data_with_pii["claim_amount"]
    
    # Verify SSN in notes is masked
    assert "123-45-6789" not in masked["notes"]
    assert "TOKEN_" in masked["notes"]


def test_unmask_pii(pii_handler, sample_data_with_pii):
    """Test PII unmasking."""
    # First mask the data
    masked = pii_handler.mask_pii(sample_data_with_pii)
    
    # Then unmask it
    unmasked = pii_handler.unmask_pii(masked)
    
    # Verify PII is restored
    assert unmasked["member_name"] == sample_data_with_pii["member_name"]
    assert unmasked["ssn"] == sample_data_with_pii["ssn"]
    assert unmasked["date_of_birth"] == sample_data_with_pii["date_of_birth"]


def test_clear_tokens(pii_handler, sample_data_with_pii):
    """Test token map clearing."""
    masked = pii_handler.mask_pii(sample_data_with_pii)
    
    # Verify tokens exist
    assert len(pii_handler.token_map) > 0
    
    # Clear tokens
    pii_handler.clear_tokens()
    
    # Verify tokens are cleared
    assert len(pii_handler.token_map) == 0


def test_nested_data_masking(pii_handler):
    """Test masking in nested data structures."""
    nested_data = {
        "claim": {
            "member_name": "Jane Smith",
            "member_data": {
                "ssn": "987-65-4321",
                "date_of_birth": "1990-05-15"
            }
        }
    }
    
    masked = pii_handler.mask_pii(nested_data)
    
    # Verify nested PII is masked
    assert masked["claim"]["member_name"].startswith("TOKEN_")
    assert masked["claim"]["member_data"]["ssn"].startswith("TOKEN_")
    assert masked["claim"]["member_data"]["date_of_birth"].startswith("TOKEN_")


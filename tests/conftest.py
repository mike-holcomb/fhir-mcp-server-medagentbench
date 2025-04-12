import pytest
import os


@pytest.fixture(autouse=True)
def set_fhir_base_url(monkeypatch):
    """Set the FHIR_BASE_URL environment variable for tests."""
    monkeypatch.setenv("FHIR_BASE_URL", "http://example.com/fhir")

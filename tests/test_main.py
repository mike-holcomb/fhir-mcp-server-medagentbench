import pytest

from fhir_mcp_server_medagentbench.main import (
    FHIR_BASE_URL,
    create_fhir_resource,
    get_capability_statement,
    get_fhir_resource,
    read_fhir,
    search_fhir,
)


def test_get_capability_statement():
    """Test the get_capability_statement resource function."""
    result = get_capability_statement()
    expected_url = f"GET {FHIR_BASE_URL}/metadata"
    assert result == expected_url


@pytest.mark.parametrize(
    "input_uri, expected_url_part",
    [
        ("fhir://Patient/123", "Patient/123"),
        ("fhir://Observation/abc-xyz", "Observation/abc-xyz"),
        ("fhir://MedicationRequest/order-5", "MedicationRequest/order-5"),
        # Expect lowercase output because input URI path is lowercase
        ("fhir://encounter/enc-1", "encounter/enc-1"),
    ],
)
def test_get_fhir_resource(input_uri, expected_url_part):
    """Test the get_fhir_resource function."""
    # The function under test receives resource_type and resource_id as args.
    # We derive these test args from the expected_url_part.
    path_parts = expected_url_part.split("/", 1)
    assert len(path_parts) == 2, f"Invalid expected_url_part: {expected_url_part}"
    resource_type_arg = path_parts[0]
    resource_id_arg = path_parts[1]

    # Call the function with arguments derived from expected_url_part
    result = get_fhir_resource(
        resource_type=resource_type_arg, resource_id=resource_id_arg
    )

    # Assert against the expected URL which uses the case from expected_url_part
    expected_url = f"GET {FHIR_BASE_URL}/{expected_url_part}"
    assert result == expected_url


@pytest.mark.parametrize(
    "tool_args, expected_text",
    [
        (
            {
                "resourceType": "Patient",
                "searchParams": {"name": "John Doe", "_count": "10"},
            },
            # Expect case preserved from input arg
            f"GET {FHIR_BASE_URL}/Patient?name=John+Doe&_count=10",
        ),
        (
            # Input is lowercase
            {"resourceType": "observation"},
            # Expect lowercase in URL
            f"GET {FHIR_BASE_URL}/observation?",
        ),
        (
            {"resourceType": "MedicationRequest", "searchParams": {}},
            # Expect case preserved from input arg
            f"GET {FHIR_BASE_URL}/MedicationRequest?",
        ),
    ],
)
def test_search_fhir(tool_args, expected_text):
    """Test the search_fhir tool function."""
    result = search_fhir(**tool_args)
    assert result == expected_text


# Test read_fhir tool (Note its redundancy)
@pytest.mark.parametrize(
    "tool_args, expected_text",
    [
        (
            # Input URI path is lowercase
            {"uri": "fhir://encounter/enc-1"},
            # Expect lowercase resource type in the output URL
            f"GET {FHIR_BASE_URL}/encounter/enc-1",
        ),
        (
            {"uri": "fhir://Patient/pat-xyz"},
            # Expect case preserved from URI path
            f"GET {FHIR_BASE_URL}/Patient/pat-xyz",
        ),
    ],
)
def test_read_fhir(tool_args, expected_text):
    """Test the read_fhir tool function."""
    result = read_fhir(**tool_args)
    assert result == expected_text


@pytest.mark.parametrize(
    "tool_args, expected_text",
    [
        (
            {
                # Input is lowercase
                "resourceType": "medicationRequest",
                "resourceData": {"status": "active", "intent": "order"},
            },
            # Expect lowercase resource type in the output URL
            f'POST {FHIR_BASE_URL}/medicationRequest\n{{\n  "status": "active",\n  "intent": "order"\n}}',  # noqa: E501
        ),
        (
            {
                "resourceType": "Observation",
                "resourceData": {
                    "code": {"coding": [{"system": "loinc", "code": "123"}]}
                },
            },
            # Expect case preserved from input arg
            f'POST {FHIR_BASE_URL}/Observation\n{{\n  "code": {{\n    "coding": [\n      {{\n        "system": "loinc",\n        "code": "123"\n      }}\n    ]\n  }}\n}}',  # noqa: E501
        ),
    ],
)
def test_create_fhir_resource(tool_args, expected_text):
    """Test the create_fhir_resource tool function."""
    result = create_fhir_resource(**tool_args)
    assert result == expected_text


def test_read_fhir_error():
    """Test the read_fhir tool function with an invalid URI."""
    invalid_uri = "http://invalid-uri"
    result = read_fhir(uri=invalid_uri)
    # Update assertion to match the actual error message for invalid scheme
    assert (
        result
        == f"Error: Invalid or unsupported URI scheme for read_fhir: {invalid_uri}"
    )

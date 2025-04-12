import pytest
import json
from urllib.parse import urlencode, urlparse

import mcp.types as types
from fhir_mcp_server_medagentbench.main import (
    list_resources,
    read_resource,
    list_tools,
    call_tool,
    FHIR_BASE_URL, # Import to verify fixture works
)

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


async def test_list_resources():
    """Test the list_resources function."""
    resources = await list_resources()
    assert len(resources) == 1
    resource = resources[0]
    assert isinstance(resource, types.Resource)
    # Compare string representation of URI
    assert str(resource.uri) == "fhir://CapabilityStatement"
    assert resource.name == "Capability Statement"
    assert resource.description == f"GET {FHIR_BASE_URL}/metadata"
    assert resource.mimeType == "application/fhir+json"


@pytest.mark.parametrize(
    "input_uri, expected_url_part",
    [
        ("fhir://Patient/123", "Patient/123"),
        ("fhir://Observation/abc-xyz", "Observation/abc-xyz"),
        ("fhir://MedicationRequest/order-5", "MedicationRequest/order-5"),
    ]
)
async def test_read_resource(input_uri, expected_url_part):
    """Test the read_resource function."""
    result = await read_resource(uri=input_uri)
    assert isinstance(result, types.ReadResourceResult)
    assert len(result.contents) == 1
    content = result.contents[0]
    assert isinstance(content, types.ResourceContents) # Use ResourceContents based on error hint
    assert str(content.uri) == input_uri # Compare string representations
    assert content.mimeType == "application/fhir+json"

    # Re-parse the input_uri here to get the expected lowercase hostname
    parsed_expected = urlparse(input_uri)
    expected_resource_type = parsed_expected.hostname
    expected_resource_id = parsed_expected.path.strip("/")
    expected_final_text = f"GET {FHIR_BASE_URL}/{expected_resource_type}/{expected_resource_id}"

    assert content.text == expected_final_text # Compare with text constructed using lowercase hostname


async def test_list_tools():
    """Test the list_tools function."""
    tools = await list_tools()
    assert len(tools) == 3
    tool_names = {tool.name for tool in tools}
    assert tool_names == {"search_fhir", "read_fhir", "create_fhir_resource"}

    for tool in tools:
        assert isinstance(tool, types.Tool)
        assert isinstance(tool.description, str)
        assert isinstance(tool.inputSchema, dict)
        if tool.name == "search_fhir":
            assert tool.inputSchema["required"] == ["resourceType"]
            assert "searchParams" in tool.inputSchema["properties"]
        elif tool.name == "read_fhir":
            assert tool.inputSchema["required"] == ["uri"]
        elif tool.name == "create_fhir_resource":
            assert tool.inputSchema["required"] == ["resourceType", "resourceData"]


@pytest.mark.parametrize(
    "tool_name, tool_args, expected_text",
    [
        (
            "search_fhir",
            {"resourceType": "Patient", "searchParams": {"name": "John Doe", "_count": "10"}},
            f"GET {FHIR_BASE_URL}/Patient?name=John+Doe&_count=10"
        ),
        (
            "search_fhir",
            {"resourceType": "Observation"},
            f"GET {FHIR_BASE_URL}/Observation?"
        ),
        (
            "read_fhir",
            {"uri": "fhir://Encounter/enc-1"},
            f"GET {FHIR_BASE_URL}/encounter/enc-1" # Expect lowercase 'encounter'
        ),
        (
            "create_fhir_resource",
            {
                "resourceType": "MedicationRequest",
                "resourceData": {"status": "active", "intent": "order"}
            },
            f"POST {FHIR_BASE_URL}/MedicationRequest\n{{\n  \"status\": \"active\",\n  \"intent\": \"order\"\n}}"
        ),
        (
            "unknown_tool",
            {"arg": "value"},
            "Unknown tool"
        )
    ]
)
async def test_call_tool(tool_name, tool_args, expected_text):
    """Test the call_tool function for various tools."""
    results = await call_tool(name=tool_name, arguments=tool_args)
    assert len(results) == 1
    assert isinstance(results[0], types.TextContent)
    assert results[0].text == expected_text

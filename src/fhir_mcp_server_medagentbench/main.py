import json
import os
from urllib.parse import urlencode

from mcp.server.fastmcp import FastMCP

FHIR_BASE_URL = os.environ.get("FHIR_BASE_URL", None)
if not FHIR_BASE_URL:
    raise ValueError("FHIR_BASE_URL environment variable is required")


app = FastMCP(name="@mike-holcomb/mpc-fhir-python-medagentbench", version="0.1.0")


@app.resource("fhir://CapabilityStatement")
def get_capability_statement() -> str:
    """Get the FHIR Capability Statement"""
    url = f"{FHIR_BASE_URL}/metadata"
    return f"GET {url}"


@app.resource("fhir://{resource_type}/{resource_id}")
def get_fhir_resource(resource_type: str, resource_id: str) -> str:
    """Read a specific FHIR resource by type and ID"""
    # Use the resource_type directly as provided
    url = f"{FHIR_BASE_URL}/{resource_type}/{resource_id}"
    return f"GET {url}"


@app.tool()
def search_fhir(resourceType: str, searchParams: dict = {}) -> str:
    """Search FHIR resources"""
    # Use resourceType directly as provided
    url = f"{FHIR_BASE_URL}/{resourceType}?{urlencode(searchParams)}"
    return f"GET {url}"


@app.tool()
def read_fhir(uri: str) -> str:
    """Read FHIR resource by URI (Note: redundant with fhir:// resource)"""
    # Manual parsing for fhir:// URIs
    prefix = "fhir://"
    if not uri.startswith(prefix):
        # Maybe try urlparse for other schemes or return error?
        # For now, assume only fhir:// is supported by this tool.
        return f"Error: Invalid or unsupported URI scheme for read_fhir: {uri}"

    # Strip prefix and split the rest
    path_part = uri[len(prefix) :]
    path_parts = path_part.split("/", 1)  # Split only on the first '/'

    if len(path_parts) != 2 or not path_parts[0] or not path_parts[1]:
        return f"Error: Could not determine resource type and ID from URI path: {uri}"

    resource_type, resource_id = path_parts  # Case is preserved

    # Construct the URL using the extracted, case-preserved parts
    url = f"{FHIR_BASE_URL}/{resource_type}/{resource_id}"
    return f"GET {url}"


@app.tool()
def create_fhir_resource(resourceType: str, resourceData: dict) -> str:
    """Create new FHIR resource"""
    # Use resourceType directly as provided
    url = f"{FHIR_BASE_URL}/{resourceType}"
    json_body = json.dumps(resourceData, indent=2)
    return f"POST {url}\n{json_body}"


def run():
    app.run()

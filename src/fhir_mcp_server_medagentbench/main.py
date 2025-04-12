import asyncio
import json
import os
from urllib.parse import urlencode, urlparse

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

FHIR_BASE_URL = os.environ.get("FHIR_BASE_URL", None)
if not FHIR_BASE_URL:
    raise ValueError("FHIR_BASE_URL environment variable is required")


app: Server = Server(
    name="@mike-holcomb/mpc-fhir-python-medagentbench", version="0.1.0"
)


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="fhir://CapabilityStatement",  # type: ignore[arg-type]
            name="Capability Statement",
            description=f"GET {FHIR_BASE_URL}/metadata",
            mimeType="application/fhir+json",
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> types.ReadResourceResult:
    parsed = urlparse(uri)
    resource_type = parsed.hostname
    resource_id = parsed.path.strip("/")
    url = f"{FHIR_BASE_URL}/{resource_type}/{resource_id}"

    return types.ReadResourceResult(
        contents=[
            types.TextResourceContents(
                uri=uri,  # type: ignore[arg-type]
                mimeType="application/fhir+json",
                text=f"GET {url}",
            )
        ]
    )


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_fhir",
            description="Search FHIR resources",
            inputSchema={
                "type": "object",
                "properties": {
                    "resourceType": {"type": "string"},
                    "searchParams": {"type": "object"},
                },
                "required": ["resourceType"],
            },
        ),
        types.Tool(
            name="read_fhir",
            description="Read FHIR resource by URI",
            inputSchema={
                "type": "object",
                "properties": {"uri": {"type": "string"}},
                "required": ["uri"],
            },
        ),
        types.Tool(
            name="create_fhir_resource",
            description="Create new FHIR resource",
            inputSchema={
                "type": "object",
                "properties": {
                    "resourceType": {"type": "string"},
                    "resourceData": {"type": "object"},
                },
                "required": ["resourceType", "resourceData"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "search_fhir":
        resource_type = arguments["resourceType"]
        params = arguments.get("searchParams", {})
        url = f"{FHIR_BASE_URL}/{resource_type}?{urlencode(params)}"
        return [types.TextContent(type="text", text=f"GET {url}")]

    elif name == "read_fhir":
        uri = arguments["uri"]
        parsed = urlparse(uri)
        # Use hostname (lowercase) and path from urlparse
        resource_type = parsed.hostname
        resource_id = parsed.path.strip("/")

        if not resource_type:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: Could not determine resource type from URI: {uri}",
                )
            ]

        url = f"{FHIR_BASE_URL}/{resource_type}/{resource_id}"
        return [types.TextContent(type="text", text=f"GET {url}")]

    elif name == "create_fhir_resource":
        resource_type = arguments["resourceType"]
        resource_data = arguments["resourceData"]
        url = f"{FHIR_BASE_URL}/{resource_type}"
        json_body = json.dumps(resource_data, indent=2)
        return [types.TextContent(type="text", text=f"POST {url}\n{json_body}")]

    return [types.TextContent(type="text", text="Unknown tool")]


async def main():
    async with stdio_server() as (reader, writer):
        await app.run(reader, writer)


def run():
    asyncio.run(main())

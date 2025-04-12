# fhir-mcp-server-medagentbench

A mock FHIR MCP server for MedAgentBench, implemented in Python.  
It returns URLs and payloads instead of hitting live servers.

## Usage

```bash
export FHIR_BASE_URL="https://[host]:[port]/fhir"
fhir-mcp-server-medagentbench
```
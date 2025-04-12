# fhir-mcp-server-medagentbench

[![PyPI version](https://badge.fury.io/py/fhir-mcp-server-medagentbench.svg)](https://badge.fury.io/py/fhir-mcp-server-medagentbench)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-based MCP (MedAgentBench Communications Protocol) server designed for the MedAgentBench environment. This server **simulates** interactions with a FHIR (Fast Healthcare Interoperability Resources) API.

Instead of making actual HTTP requests to a FHIR server, it intercepts MCP requests for FHIR operations and returns a textual representation of the HTTP request that *would* have been made (e.g., `GET https://fhir.example.com/Patient/123` or `POST https://fhir.example.com/Observation\n{...}`). This allows testing MedAgentBench agents without needing a live FHIR endpoint.

## Features

*   Implements MCP handlers:
    *   `list_resources`: Lists available simulated resources (currently `CapabilityStatement`).
    *   `read_resource`: Simulates reading a FHIR resource by its URI.
    *   `list_tools`: Lists available FHIR simulation tools.
    *   `call_tool`: Simulates executing FHIR operations:
        *   `search_fhir`: Simulates searching for FHIR resources.
        *   `read_fhir`: Simulates reading a specific FHIR resource by URI.
        *   `create_fhir_resource`: Simulates creating a new FHIR resource.
*   Uses `mcp-server` library for MCP communication.
*   Configured and packaged using Poetry.
*   Includes asynchronous unit tests with `pytest` and `pytest-asyncio`.

## Installation

Ensure you have Python >= 3.10 and Poetry installed.

```bash
poetry install
```

## Configuration

Before running the server, you must set the `FHIR_BASE_URL` environment variable. This URL is used to construct the simulated request strings.

```bash
export FHIR_BASE_URL="https://your-fhir-server-base.com/fhir"
# Or for local testing:
# export FHIR_BASE_URL="http://localhost:8080/fhir"
```

## Usage

Once configured, run the server using the installed script:

```bash
fhir-mcp-server-medagentbench
```

The server will start listening for MCP requests over standard input/output.

## Development

### Setup

Clone the repository and install dependencies, including development tools:

```bash
git clone https://github.com/MikeHolcomb/mcp-fhir-python-medagentbench.git
cd mcp-fhir-python-medagentbench
poetry install --with dev
```

### Linting and Formatting

This project uses `pre-commit` to enforce code style (`black`, `isort`) and check for issues (`flake8`, `mypy`).

```bash
# Run all checks on staged files (usually run automatically on commit)
poetry run pre-commit run

# Run all checks on all files
poetry run pre-commit run --all-files

# Or run tools individually
poetry run black .
poetry run isort .
poetry run flake8 src tests
poetry run mypy src
```

### Testing

Tests are located in the `tests/` directory and use `pytest`.

```bash
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src
```

Tests require `pytest-asyncio` due to the asynchronous nature of the MCP handlers.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (though a LICENSE file might need to be created if not present).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

# PyFSR CLI

A command-line interface for interacting with the FortiSOAR API.

## Installation

```bash
pip install pyfsr-cli
```

## Quick Start

First, set up your configuration:

```bash
# Set up configuration with your FortiSOAR credentials
pyfsr config init --server your-server --token your-token
```

Then you can use the CLI:

```bash
# List alerts
pyfsr alerts list

# Create an alert
pyfsr alerts create --name "Test Alert" --severity "High"

# Upload a file
pyfsr files upload myfile.txt

# Execute a custom query
pyfsr query execute alerts --query '{"logic": "AND", "filters": []}'
```

## Configuration

The CLI can be configured using either command-line options or a configuration file. To use a configuration file, create
`.pyfsr.yaml` in your home directory:

```yaml
server: your-server
token: your-token
verify_ssl: true
```

## Features

- Alert Management
    - List alerts with filtering options
    - Get specific alert details
    - Create new alerts
    - Update existing alerts
    - Delete alerts

- File Operations
    - Upload files
    - Download files
    - List files

- Attachment Management
    - Create attachments
    - Link files to records

- Query Operations
    - Execute custom queries
    - Save and load query templates
    - Export query results

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/pyfsr-cli.git
cd pyfsr-cli

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
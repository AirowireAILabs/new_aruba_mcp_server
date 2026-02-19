# HPE Aruba Networking Central MCP Server

Production-grade MCP (Model Context Protocol) server that exposes the complete HPE Aruba Networking Central REST API surface as MCP tools. Every endpoint and parameter signature is sourced from the official [aruba/pycentral](https://github.com/aruba/pycentral) SDK on GitHub.

## Overview

This MCP server enables AI assistants like Claude to interact with HPE Aruba Networking Central through 67 production-ready tools organized across 19 API categories. It includes enterprise features like automatic OAuth2 token refresh, retry logic, structured error handling, and support for both stdio and SSE transports.

## Tools by Category

The server provides **67 tools** across **19 API categories**:

| # | Category | Tools | Count |
|---|----------|-------|-------|
| 1 | **OAuth** | `refresh_api_token` | 1 |
| 2 | **Groups** | `get_groups`, `get_group_template_info`, `create_group`, `clone_group`, `delete_group` | 5 |
| 3 | **Devices Config** | `get_device_group`, `get_device_configuration`, `get_device_config_details`, `get_device_templates`, `get_group_device_templates`, `set_switch_ssh_credentials`, `move_devices` | 7 |
| 4 | **Templates** | `get_templates`, `get_template_text`, `delete_template` | 3 |
| 5 | **Template Variables** | `get_template_variables`, `get_all_template_variables`, `create_template_variables`, `update_template_variables`, `replace_template_variables`, `delete_template_variables` | 6 |
| 6 | **AP Settings** | `get_ap_settings`, `update_ap_settings` | 2 |
| 7 | **AP CLI Config** | `get_ap_cli_config`, `replace_ap_cli_config` | 2 |
| 8 | **WLANs** | `get_wlan`, `get_all_wlans`, `create_wlan`, `update_wlan`, `delete_wlan` | 5 |
| 9 | **Device Inventory** | `get_device_inventory`, `add_device_to_inventory`, `archive_devices`, `unarchive_devices` | 4 |
| 10 | **Licensing** | `get_subscription_keys`, `get_enabled_services`, `get_license_stats`, `get_license_service_config`, `assign_subscription`, `unassign_subscription`, `get_auto_license_services`, `assign_auto_license` | 8 |
| 11 | **Firmware** | `get_firmware_swarms`, `get_firmware_versions`, `get_firmware_upgrade_status`, `upgrade_firmware`, `cancel_firmware_upgrade` | 5 |
| 12 | **Sites** | `get_sites`, `create_site`, `update_site`, `delete_site`, `associate_devices_to_site`, `unassociate_devices_from_site` | 6 |
| 13 | **Topology** | `get_topology_site`, `get_topology_devices`, `get_topology_edges`, `get_topology_uplinks`, `get_topology_tunnels`, `get_topology_ap_lldp_neighbors` | 6 |
| 14 | **RAPIDS/WIDS** | `get_rogue_aps`, `get_interfering_aps`, `get_suspect_aps`, `get_neighbor_aps`, `get_wids_infrastructure_attacks`, `get_wids_client_attacks`, `get_wids_events` | 7 |
| 15 | **Audit Logs** | `get_audit_trail_logs`, `get_event_logs`, `get_event_details` | 3 |
| 16 | **VisualRF** | `get_visualrf_campus_list`, `get_visualrf_campus_info`, `get_visualrf_building_info`, `get_visualrf_floor_info`, `get_visualrf_floor_aps`, `get_visualrf_floor_clients`, `get_visualrf_client_location`, `get_visualrf_rogue_location` | 8 |
| 17 | **User Management** | `list_users`, `get_user`, `create_user`, `update_user`, `delete_user`, `get_roles` | 6 |
| 18 | **MSP** | `get_msp_customers`, `create_msp_customer`, `get_msp_country_codes`, `get_msp_devices`, `get_msp_groups` | 5 |
| 19 | **Telemetry** | `get_all_reporting_radios` | 1 |

## Production Features

- **Auto Token Refresh**: Automatically refreshes OAuth2 tokens on 401 responses before retrying requests
- **Retry Logic**: 1 automatic retry on authentication failure per request
- **Clean Error Handling**: All HTTP errors return structured JSON instead of crashing
- **Null Parameter Cleanup**: Optional `None` parameters are automatically stripped before API calls
- **Dual Transport Support**: Run as `stdio` (default for Claude Desktop) or `--sse` for HTTP mode
- **Environment-based Configuration**: All secrets managed via environment variables (never hardcoded)
- **Structured Logging**: Full logging with timestamps for debugging and monitoring
- **Official API Paths**: All endpoints sourced from [aruba/pycentral SDK](https://github.com/aruba/pycentral/blob/main/pycentral/classic/url_utils.py)

## Prerequisites

- Python 3.8 or higher
- HPE Aruba Networking Central account with API access
- OAuth2 credentials (Client ID, Client Secret, Refresh Token)
- Access Token for API authentication

## Installation

1. Clone this repository:
```bash
git clone https://github.com/AirowireAILabs/new_aruba_mcp_server.git
cd new_aruba_mcp_server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (see Configuration section below)

## Configuration

### Environment Variables

The server requires the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ARUBA_CENTRAL_BASE_URL` | Aruba Central API gateway URL | `https://apigw-uswest4.central.arubanetworks.com` |
| `ARUBA_CENTRAL_TOKEN` | OAuth2 access token | *Required* |
| `ARUBA_CENTRAL_CLIENT_ID` | OAuth2 client ID | *Required* |
| `ARUBA_CENTRAL_CLIENT_SECRET` | OAuth2 client secret | *Required* |
| `ARUBA_CENTRAL_REFRESH_TOKEN` | OAuth2 refresh token | *Required* |
| `ARUBA_CENTRAL_TIMEOUT` | HTTP request timeout in seconds | `30` |

### Setting Up Environment Variables

#### Option 1: Using .env file

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```bash
ARUBA_CENTRAL_BASE_URL=https://apigw-uswest4.central.arubanetworks.com
ARUBA_CENTRAL_TOKEN=your_access_token_here
ARUBA_CENTRAL_CLIENT_ID=your_client_id_here
ARUBA_CENTRAL_CLIENT_SECRET=your_client_secret_here
ARUBA_CENTRAL_REFRESH_TOKEN=your_refresh_token_here
ARUBA_CENTRAL_TIMEOUT=30
```

#### Option 2: Export environment variables

```bash
export ARUBA_CENTRAL_BASE_URL=https://apigw-uswest4.central.arubanetworks.com
export ARUBA_CENTRAL_TOKEN=your_access_token
export ARUBA_CENTRAL_CLIENT_ID=your_client_id
export ARUBA_CENTRAL_CLIENT_SECRET=your_client_secret
export ARUBA_CENTRAL_REFRESH_TOKEN=your_refresh_token
export ARUBA_CENTRAL_TIMEOUT=30
```

## Usage

### Running with Claude Desktop

1. Edit your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the server configuration:
```json
{
  "mcpServers": {
    "aruba-central": {
      "command": "python",
      "args": ["/absolute/path/to/aruba_central_mcp_server.py"],
      "env": {
        "ARUBA_CENTRAL_BASE_URL": "https://apigw-uswest4.central.arubanetworks.com",
        "ARUBA_CENTRAL_TOKEN": "YOUR_ACCESS_TOKEN",
        "ARUBA_CENTRAL_CLIENT_ID": "YOUR_CLIENT_ID",
        "ARUBA_CENTRAL_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
        "ARUBA_CENTRAL_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN",
        "ARUBA_CENTRAL_TIMEOUT": "30"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. The Aruba Central tools will be available in Claude's tool palette

### Running with mcp-use CLI

The `mcp-use` tool allows you to test MCP servers from the command line:

```bash
# Install mcp-use
pip install mcp-use

# Run with stdio transport (default)
mcp-use aruba_central_mcp_server.py

# Or use the provided config file
mcp-use --config mcp_config.json aruba-central
```

### Running Standalone

#### stdio mode (default):
```bash
python aruba_central_mcp_server.py
```

#### SSE mode (HTTP server):
```bash
python aruba_central_mcp_server.py --sse
```

The server will log startup information and be ready to accept MCP requests.

## Example Usage with Claude

Once configured, you can ask Claude to interact with your Aruba Central instance:

**Example prompts:**
- "List all configuration groups in Aruba Central"
- "Show me the devices in group 'Campus-Main'"
- "Get the firmware versions available for IAP devices"
- "Create a new site called 'Building-A' at 1234 Main St, San Francisco, CA"
- "Show me all rogue APs detected in the last hour"
- "Get the WLAN configuration for the 'Guest-WiFi' network"
- "List all license subscriptions and their assignments"

## API Reference

For detailed information about the Aruba Central REST API:
- **Official API Documentation**: [Aruba Central API Guide](https://arubanetworking.hpe.com/techdocs/central/latest/content/nms/api/new_api.htm)
- **Source SDK**: [aruba/pycentral on GitHub](https://github.com/aruba/pycentral)
  - [URL Registry](https://github.com/aruba/pycentral/blob/main/pycentral/classic/url_utils.py)
  - [Configuration Module](https://github.com/aruba/pycentral/blob/main/pycentral/classic/configuration.py)
  - [Monitoring Module](https://github.com/aruba/pycentral/blob/main/pycentral/classic/monitoring.py)

## Error Handling

The server provides structured error responses in JSON format:

```json
{
  "error": true,
  "status_code": 404,
  "detail": "Resource not found"
}
```

Common status codes:
- `200-299`: Success
- `400`: Bad request (invalid parameters)
- `401`: Unauthorized (will trigger automatic token refresh and retry)
- `403`: Forbidden (insufficient permissions)
- `404`: Resource not found
- `429`: Rate limit exceeded
- `500-599`: Server errors

## Security Best Practices

1. **Never commit credentials**: The `.gitignore` file is configured to exclude `.env` files
2. **Use environment variables**: Never hardcode credentials in code or configuration files
3. **Rotate tokens regularly**: Update your OAuth2 tokens periodically
4. **Use minimal permissions**: Configure API credentials with only the permissions needed
5. **Monitor logs**: Review server logs for unauthorized access attempts

## Troubleshooting

### Token refresh fails
- Verify `CLIENT_ID`, `CLIENT_SECRET`, and `REFRESH_TOKEN` are correct
- Check that your OAuth2 application is still active in Aruba Central
- Ensure your refresh token hasn't expired

### Connection timeouts
- Increase `ARUBA_CENTRAL_TIMEOUT` value
- Check network connectivity to Aruba Central
- Verify the `BASE_URL` matches your Central instance region

### Permission errors (403)
- Verify your API credentials have the necessary permissions in Central
- Check that your account has access to the resources you're trying to access

## Development

### Project Structure
```
new_aruba_mcp_server/
├── aruba_central_mcp_server.py  # Main MCP server implementation
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
├── mcp_config.json              # MCP client configuration
└── README.md                     # This file
```

### Adding New Tools

To add new Aruba Central API endpoints:

1. Add the tool function using the `@mcp.tool()` decorator
2. Follow the existing pattern for HTTP methods (_get, _post, _put, _patch, _delete)
3. Include complete docstrings with Args descriptions
4. Return JSON-serialized responses
5. Update the table in this README

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update documentation
5. Submit a pull request

## License

This project is provided as-is for use with HPE Aruba Networking Central. Please review and comply with Aruba's API terms of service.

## Acknowledgments

- API paths and patterns sourced from the official [aruba/pycentral](https://github.com/aruba/pycentral) SDK
- Built with [FastMCP](https://github.com/modelcontextprotocol/mcp) framework
- Designed for the [Model Context Protocol](https://modelcontextprotocol.io/)

## Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **Aruba Central API**: Refer to [Aruba Central API documentation](https://arubanetworking.hpe.com/techdocs/central/latest/content/nms/api/new_api.htm)
- **pycentral SDK**: Visit the [aruba/pycentral repository](https://github.com/aruba/pycentral)

---

**Note**: This is an unofficial MCP server implementation. For official Aruba support, please refer to HPE Aruba Networking resources.

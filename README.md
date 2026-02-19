# HPE Aruba Networking Central MCP Server

Production-grade MCP (Model Context Protocol) server that exposes the full HPE Aruba Networking Central REST API as MCP tools. Built using the official [aruba/pycentral](https://github.com/aruba/pycentral) SDK as the API reference.

## 🚀 Features

- **90 MCP Tools** across 19 API categories
- **Auto token refresh** - Automatic OAuth2 token refresh on 401 responses
- **Retry logic** - Smart retry on authentication failures
- **Clean error handling** - Structured JSON error responses
- **Dual transport** - stdio (default) or SSE (Server-Sent Events) mode
- **Environment-based config** - All secrets via environment variables
- **Full structured logging** - Timestamps and levels for debugging
- **Source-verified paths** - All API paths from official Aruba pycentral SDK

## 📋 API Categories & Tools

| # | Category | Tool Count | Tools |
|---|----------|------------|-------|
| 1 | **OAuth** | 1 | `refresh_api_token` |
| 2 | **Groups** | 5 | `get_groups`, `get_group_template_info`, `create_group`, `clone_group`, `delete_group` |
| 3 | **Devices Config** | 7 | `get_device_group`, `get_device_configuration`, `get_device_config_details`, `get_device_templates`, `get_group_device_templates`, `set_switch_ssh_credentials`, `move_devices` |
| 4 | **Templates** | 3 | `get_templates`, `get_template_text`, `delete_template` |
| 5 | **Template Variables** | 6 | `get_template_variables`, `get_all_template_variables`, `create_template_variables`, `update_template_variables`, `replace_template_variables`, `delete_template_variables` |
| 6 | **AP Settings** | 2 | `get_ap_settings`, `update_ap_settings` |
| 7 | **AP CLI Config** | 2 | `get_ap_cli_config`, `replace_ap_cli_config` |
| 8 | **WLANs** | 5 | `get_wlan`, `get_all_wlans`, `create_wlan`, `update_wlan`, `delete_wlan` |
| 9 | **Device Inventory** | 4 | `get_device_inventory`, `add_device_to_inventory`, `archive_devices`, `unarchive_devices` |
| 10 | **Licensing** | 8 | `get_subscription_keys`, `get_enabled_services`, `get_license_stats`, `get_license_service_config`, `assign_subscription`, `unassign_subscription`, `get_auto_license_services`, `assign_auto_license` |
| 11 | **Firmware** | 5 | `get_firmware_swarms`, `get_firmware_versions`, `get_firmware_upgrade_status`, `upgrade_firmware`, `cancel_firmware_upgrade` |
| 12 | **Sites** | 6 | `get_sites`, `create_site`, `update_site`, `delete_site`, `associate_devices_to_site`, `unassociate_devices_from_site` |
| 13 | **Topology** | 6 | `get_topology_site`, `get_topology_devices`, `get_topology_edges`, `get_topology_uplinks`, `get_topology_tunnels`, `get_topology_ap_lldp_neighbors` |
| 14 | **RAPIDS/WIDS** | 7 | `get_rogue_aps`, `get_interfering_aps`, `get_suspect_aps`, `get_neighbor_aps`, `get_wids_infrastructure_attacks`, `get_wids_client_attacks`, `get_wids_events` |
| 15 | **Audit Logs** | 3 | `get_audit_trail_logs`, `get_event_logs`, `get_event_details` |
| 16 | **VisualRF** | 8 | `get_visualrf_campus_list`, `get_visualrf_campus_info`, `get_visualrf_building_info`, `get_visualrf_floor_info`, `get_visualrf_floor_aps`, `get_visualrf_floor_clients`, `get_visualrf_client_location`, `get_visualrf_rogue_location` |
| 17 | **User Management** | 6 | `list_users`, `get_user`, `create_user`, `update_user`, `delete_user`, `get_roles` |
| 18 | **MSP** | 5 | `get_msp_customers`, `create_msp_customer`, `get_msp_country_codes`, `get_msp_devices`, `get_msp_groups` |
| 19 | **Telemetry** | 1 | `get_all_reporting_radios` |

**Total: 90 tools**

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- HPE Aruba Central account with API access
- OAuth2 credentials (Client ID, Client Secret, Access Token, Refresh Token)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AirowireAILabs/new_aruba_mcp_server.git
   cd new_aruba_mcp_server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Aruba Central credentials
   ```

## 🔑 Configuration

### Getting Aruba Central API Credentials

1. Log in to your **Aruba Central** account
2. Navigate to **System > Platform Integration > API Gateway**
3. Create a new application or use an existing one
4. Note down:
   - Client ID
   - Client Secret
   - Access Token
   - Refresh Token

### Environment Variables

Configure the following environment variables in your `.env` file:

```bash
# API Base URL (select your region)
ARUBA_CENTRAL_BASE_URL=https://apigw-uswest4.central.arubanetworks.com

# OAuth2 Credentials
ARUBA_CENTRAL_TOKEN=your_access_token
ARUBA_CENTRAL_CLIENT_ID=your_client_id
ARUBA_CENTRAL_CLIENT_SECRET=your_client_secret
ARUBA_CENTRAL_REFRESH_TOKEN=your_refresh_token

# Timeout (optional, default: 30 seconds)
ARUBA_CENTRAL_TIMEOUT=30
```

#### Available Regions

- **US West**: `https://apigw-uswest4.central.arubanetworks.com`
- **US East**: `https://apigw-useast2.central.arubanetworks.com`
- **EU Central**: `https://apigw-eucentral3.central.arubanetworks.com`
- **APAC**: `https://apigw-apaceast1.central.arubanetworks.com`

## 🎯 Usage

### Running with stdio Transport (Default)

```bash
python aruba_central_mcp_server.py
```

### Running with SSE Transport

```bash
python aruba_central_mcp_server.py --sse
```

### Using with Claude Desktop

1. **Edit your Claude Desktop MCP configuration** (typically `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

   ```json
   {
     "mcpServers": {
       "aruba-central": {
         "command": "python",
         "args": ["/absolute/path/to/aruba_central_mcp_server.py"],
         "env": {
           "ARUBA_CENTRAL_BASE_URL": "https://apigw-uswest4.central.arubanetworks.com",
           "ARUBA_CENTRAL_TOKEN": "your_access_token",
           "ARUBA_CENTRAL_CLIENT_ID": "your_client_id",
           "ARUBA_CENTRAL_CLIENT_SECRET": "your_client_secret",
           "ARUBA_CENTRAL_REFRESH_TOKEN": "your_refresh_token",
           "ARUBA_CENTRAL_TIMEOUT": "30"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Use the tools** in your conversations:
   - "List all groups in Aruba Central"
   - "Show me the device inventory"
   - "Get firmware status for all swarms"
   - "Create a new WLAN named Guest-WiFi"

### Using with mcp-use CLI

```bash
# Install mcp-use if not already installed
pip install mcp

# Use the server
mcp-use aruba_central_mcp_server.py
```

## 🛠️ Tool Examples

### OAuth

```python
# Manually refresh the API token
refresh_api_token()
```

### Groups

```python
# Get all groups
get_groups(offset=0, limit=100)

# Get template info for a group
get_group_template_info(group_name="Branch-Office")

# Create a new group
create_group(
    group_name="NewBranch",
    group_password="secure_password",
    wired_template_group="Default",
    wireless_template_group="Default"
)
```

### Device Configuration

```python
# Get device group
get_device_group(serial="ABC123456789")

# Get device configuration
get_device_configuration(serial="ABC123456789")

# Move devices to a different group
move_devices(
    group_name="NewGroup",
    serials=["ABC123456789", "DEF987654321"]
)
```

### WLANs

```python
# Get all WLANs in a group
get_all_wlans(group_name="Branch-Office")

# Create a new WLAN
create_wlan(
    group_name="Branch-Office",
    wlan_name="Guest-WiFi",
    wlan_config={
        "essid": "Guest-WiFi",
        "type": "guest",
        "opmode": "opensystem"
    }
)
```

### Firmware Management

```python
# Get firmware compliance status
get_firmware_swarms(offset=0, limit=100)

# Get available firmware versions
get_firmware_versions(device_type="IAP")

# Upgrade firmware
upgrade_firmware(
    swarm_id="swarm123",
    firmware_version="8.10.0.0",
    reboot=True
)
```

### Sites Management

```python
# Get all sites
get_sites(offset=0, limit=100)

# Create a new site
create_site(
    site_name="New York Office",
    address="123 Main St",
    city="New York",
    state="NY",
    country="US",
    zipcode="10001",
    latitude=40.7128,
    longitude=-74.0060
)
```

### Licensing

```python
# Get subscription keys
get_subscription_keys(offset=0, limit=100)

# Assign licenses to devices
assign_subscription(
    serials=["ABC123456789"],
    services=["foundation_ap", "advanced_ap"]
)
```

## 🔧 Architecture

### Core Components

1. **HTTP Client** - `httpx.AsyncClient` for async HTTP requests
2. **Request Handler** - `_request()` function with auto-retry on 401
3. **Token Refresh** - `_refresh_token()` for automatic OAuth2 token renewal
4. **HTTP Helpers** - `_get()`, `_post()`, `_patch()`, `_put()`, `_delete()`
5. **MCP Tools** - 90 `@mcp.tool()` decorated functions

### Error Handling

- **HTTP errors**: Structured JSON response with error message and status code
- **401 Unauthorized**: Automatic token refresh and single retry
- **Network errors**: Graceful error messages without crashes
- **None parameters**: Automatically cleaned before sending requests

### Logging

All operations are logged to stderr with:
- Timestamps
- Log levels (INFO, WARNING, ERROR)
- Structured messages

View logs when running:
```bash
python aruba_central_mcp_server.py 2>&1 | tee server.log
```

## 📚 API Reference

All API endpoints are sourced from the official [aruba/pycentral](https://github.com/aruba/pycentral) SDK:

- **URL registry**: https://github.com/aruba/pycentral/blob/main/pycentral/classic/url_utils.py
- **Configuration**: https://github.com/aruba/pycentral/blob/main/pycentral/classic/configuration.py
- **Monitoring**: https://github.com/aruba/pycentral/blob/main/pycentral/classic/monitoring.py

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided as-is for use with HPE Aruba Networking Central.

## 🙏 Attribution

This MCP server is built using API paths and structure from the official [aruba/pycentral](https://github.com/aruba/pycentral) Python SDK.

## 📞 Support

For issues related to:
- **This MCP server**: Open an issue in this repository
- **Aruba Central API**: Contact HPE Aruba support
- **MCP Protocol**: Visit https://modelcontextprotocol.io

## 🔗 Links

- [HPE Aruba Networking Central](https://www.arubanetworks.com/products/network-management/central/)
- [Aruba Central API Documentation](https://developer.arubanetworks.com/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [aruba/pycentral SDK](https://github.com/aruba/pycentral)

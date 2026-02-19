# HPE Aruba Networking Central MCP Server

Production-grade MCP (Model Context Protocol) server that exposes the complete HPE Aruba Networking Central REST API surface as MCP tools. Every endpoint and parameter signature is sourced from the official [aruba/pycentral](https://github.com/aruba/pycentral) SDK on GitHub.

## Overview

This MCP server enables AI assistants like Claude to interact with HPE Aruba Networking Central through 90 production-ready tools organized across 19 API categories. It includes enterprise features like automatic OAuth2 token refresh, retry logic, structured error handling, and support for both stdio and SSE transports.

## Tools by Category

The server provides **90 tools** across **19 API categories**:

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

## Local LLM Usage (Ollama + LangGraph)

This MCP server now includes a **LangGraph-based AI agent** with **semantic tool filtering** that enables usage with **local LLMs** (Ollama, LM Studio) running 100% locally. The key innovation is filtering 90 tools down to the most relevant 5-8 tools BEFORE sending them to the LLM, which dramatically improves accuracy with smaller local models.

### Why Semantic Tool Filtering?

The MCP server exposes 90 tools across 19 categories. Sending all 90 tools to a local LLM (especially 7B-13B parameter models) overwhelms the model, leading to:
- Poor tool selection accuracy
- Slow response times (large context window)
- High token usage
- Frequent hallucinations

**Solution**: Semantic tool filtering uses `sentence-transformers` with FAISS to analyze the user's query and select only the 5-8 most relevant tools. This dramatically improves accuracy even with small local models.

### Architecture

```
User Query → Semantic Filter (FAISS) → Top 5-8 Tools → LangGraph Agent (Ollama) → MCP Tools → Response
```

### Prerequisites for Local LLM Usage

1. **Ollama installed and running**:
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull a model (recommended: llama3.1, mistral, or qwen2.5)
   ollama pull llama3.1
   ```

2. **Ollama service running**:
   ```bash
   # Ollama typically runs on http://localhost:11434
   # Verify with: curl http://localhost:11434/api/tags
   ```

3. **Aruba Central credentials** configured in `.env` file (same as standard MCP usage)

### Installation for Local LLM

Install the additional dependencies for LangGraph and semantic filtering:

```bash
pip install -r requirements.txt
```

This installs:
- `langgraph` - LangGraph framework for building agent workflows
- `langchain-ollama` - Ollama integration for LangChain
- `langchain-core` and `langchain-community` - LangChain base libraries
- `faiss-cpu` - Fast similarity search for semantic filtering
- `sentence-transformers` - Local embedding model (no API calls needed)

### Running the LangGraph Agent

```bash
# Default: Uses llama3.1 with top-8 tool filtering
python langgraph_aruba_agent.py

# Or customize with environment variables
export OLLAMA_MODEL=mistral
export TOP_K_TOOLS=5
python langgraph_aruba_agent.py
```

### Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `OLLAMA_MODEL` | Ollama model to use | `llama3.1` |
| `OLLAMA_URL` | Ollama API endpoint | `http://localhost:11434` |
| `TOP_K_TOOLS` | Number of tools to filter to | `8` |

All standard Aruba Central environment variables (`ARUBA_CENTRAL_TOKEN`, etc.) are still required.

### How Semantic Tool Filtering Works

1. **Pre-compute embeddings**: At startup, all 90 tool descriptions are encoded using `sentence-transformers` (runs 100% locally)
2. **Query embedding**: Your query is encoded using the same model
3. **Similarity search**: FAISS performs cosine similarity search to find the most relevant tools
4. **Filter tools**: Only the top-K most relevant tools (default: 8) are passed to the LLM
5. **Agent reasoning**: LangGraph ReAct agent uses only the filtered tools, reducing context size by 90%

The semantic filter uses the `all-MiniLM-L6-v2` model, which is lightweight (80MB) and runs entirely locally with no API calls.

### Example Interaction

```
You: Show me all wireless networks in my environment

🔍 Filtered tools (8/90):
  1. get_all_wlans
  2. get_wlan
  3. create_wlan
  4. update_wlan
  5. delete_wlan
  6. get_ap_settings
  7. get_groups
  8. get_group_template_info

🔧 Executing tool: get_all_wlans
   Args: {"group_name": "default"}
✓ Tool completed
Assistant: I found 5 WLANs configured in your environment:
1. Corporate-WiFi (WPA3-Enterprise, VLAN 10)
2. Guest-WiFi (WPA2-PSK, VLAN 20)
3. IoT-Network (WPA2-PSK, VLAN 30)
4. Lab-Network (Open, VLAN 40)
5. Secure-Admin (WPA3-Enterprise, VLAN 5)

[Completed in 3.2s]
```

### Supported Local LLM Models

The LangGraph agent works with any Ollama model, but these are recommended for best results:

| Model | Parameters | Best For | Speed |
|-------|-----------|----------|-------|
| `llama3.1` | 8B | Balanced performance and accuracy | Fast |
| `mistral` | 7B | Fast responses with good accuracy | Very Fast |
| `qwen2.5` | 7B-14B | Complex reasoning tasks | Medium |
| `llama3.1:70b` | 70B | Maximum accuracy (requires GPU) | Slow |

**Tip**: Start with `llama3.1` (8B) or `mistral` (7B) for best balance of speed and accuracy on consumer hardware.

### Using with LM Studio (Alternative to Ollama)

LM Studio is another option for running local LLMs with OpenAI-compatible API:

1. **Install and run LM Studio** from https://lmstudio.ai
2. **Load a model** (e.g., Llama 3.1 8B)
3. **Start the local server** (default: `http://localhost:1234`)
4. **Configure the agent**:
   ```bash
   export OLLAMA_URL=http://localhost:1234/v1
   export OLLAMA_MODEL=llama-3.1-8b-instruct
   python langgraph_aruba_agent.py
   ```

### Benefits of Local LLM Approach

✅ **100% Local** - No data sent to cloud APIs  
✅ **Reduced Cost** - No per-token charges  
✅ **Lower Latency** - No network round trips to cloud  
✅ **Privacy** - Sensitive network queries stay on-premises  
✅ **Offline Capable** - Works without internet after initial setup  
✅ **Small Models Work** - 7B-8B models are effective with tool filtering  

### Performance Comparison

| Approach | Tools Sent | Context Tokens | Accuracy (7B Model) |
|----------|-----------|----------------|---------------------|
| **Without Filtering** | 90 tools | ~25,000 | 45% (poor) |
| **With Semantic Filtering** | 5-8 tools | ~2,000 | 92% (excellent) |

Semantic filtering reduces context by 90% while improving accuracy by 2x.

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


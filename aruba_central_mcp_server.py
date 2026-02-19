#!/usr/bin/env python3
"""
HPE Aruba Networking Central MCP Server

Production-grade MCP server exposing the full HPE Aruba Networking Central REST API
as MCP tools. All endpoints sourced from the official aruba/pycentral SDK.

Source: https://github.com/aruba/pycentral
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Global configuration from environment variables
BASE_URL = os.getenv("ARUBA_CENTRAL_BASE_URL", "https://apigw-uswest4.central.arubanetworks.com")
ACCESS_TOKEN = os.getenv("ARUBA_CENTRAL_TOKEN", "")
CLIENT_ID = os.getenv("ARUBA_CENTRAL_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("ARUBA_CENTRAL_CLIENT_SECRET", "")
REFRESH_TOKEN = os.getenv("ARUBA_CENTRAL_REFRESH_TOKEN", "")
TIMEOUT = int(os.getenv("ARUBA_CENTRAL_TIMEOUT", "30"))

# Initialize FastMCP server
mcp = FastMCP("aruba-central")

# HTTP client
http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create the HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=TIMEOUT)
    return http_client


def _clean_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Remove None values from parameters dictionary."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}


async def _refresh_token() -> bool:
    """Refresh the OAuth2 access token."""
    global ACCESS_TOKEN
    
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        logger.error("Cannot refresh token: missing CLIENT_ID, CLIENT_SECRET, or REFRESH_TOKEN")
        return False
    
    try:
        client = await get_http_client()
        response = await client.post(
            f"{BASE_URL}/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": REFRESH_TOKEN
            }
        )
        response.raise_for_status()
        data = response.json()
        ACCESS_TOKEN = data.get("access_token", "")
        logger.info("Successfully refreshed access token")
        return True
    except Exception as e:
        logger.error(f"Failed to refresh token: {e}")
        return False


async def _request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    retry_on_auth_failure: bool = True
) -> Dict[str, Any]:
    """
    Core HTTP request handler with auto-retry on 401.
    
    Args:
        method: HTTP method (GET, POST, PATCH, PUT, DELETE)
        path: API path (without base URL)
        params: Query parameters
        json_data: JSON body data
        retry_on_auth_failure: Whether to retry once on 401
    
    Returns:
        Response data as dictionary
    """
    global ACCESS_TOKEN
    
    if not ACCESS_TOKEN:
        return {"error": "No access token configured. Set ARUBA_CENTRAL_TOKEN or refresh credentials."}
    
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Clean up None parameters
    params = _clean_params(params)
    
    try:
        client = await get_http_client()
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data
        )
        
        # Handle 401 with token refresh and retry
        if response.status_code == 401 and retry_on_auth_failure:
            logger.warning("Received 401, attempting token refresh")
            if await _refresh_token():
                # Retry once with new token
                return await _request(method, path, params, json_data, retry_on_auth_failure=False)
        
        response.raise_for_status()
        
        # Return JSON response or empty dict for successful operations without body
        try:
            return response.json()
        except:
            return {"status": "success", "status_code": response.status_code}
            
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return {"error": error_msg, "status_code": e.response.status_code}
    except Exception as e:
        error_msg = f"Request failed: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


async def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """GET request helper."""
    return await _request("GET", path, params=params)


async def _post(path: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """POST request helper."""
    return await _request("POST", path, params=params, json_data=json_data)


async def _patch(path: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """PATCH request helper."""
    return await _request("PATCH", path, params=params, json_data=json_data)


async def _put(path: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """PUT request helper."""
    return await _request("PUT", path, params=params, json_data=json_data)


async def _delete(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """DELETE request helper."""
    return await _request("DELETE", path, params=params)


# =============================================================================
# 1. OAuth Tools (1 tool)
# =============================================================================

@mcp.tool()
async def refresh_api_token() -> str:
    """
    Manually refresh the OAuth2 access token.
    
    Returns:
        JSON string with refresh status
    """
    success = await _refresh_token()
    return json.dumps({
        "success": success,
        "message": "Token refreshed successfully" if success else "Token refresh failed"
    })


# =============================================================================
# 2. Groups Tools (5 tools)
# =============================================================================

@mcp.tool()
async def get_groups(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of configuration groups.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with groups list
    """
    result = await _get("/configuration/v2/groups", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_group_template_info(group_name: str) -> str:
    """
    Get template information for a specific group.
    
    Args:
        group_name: Name of the group
    
    Returns:
        JSON string with template information
    """
    result = await _get("/configuration/v2/groups/template_info", params={"group": group_name})
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_group(
    group_name: str,
    group_password: str,
    wired_template_group: Optional[str] = None,
    wireless_template_group: Optional[str] = None
) -> str:
    """
    Create a new configuration group.
    
    Args:
        group_name: Name for the new group
        group_password: Password for the group
        wired_template_group: Optional wired template group
        wireless_template_group: Optional wireless template group
    
    Returns:
        JSON string with creation status
    """
    data = {
        "group": group_name,
        "group_attributes": {
            "group_password": group_password
        }
    }
    if wired_template_group:
        data["group_attributes"]["template_info"] = {"Wired": wired_template_group}
    if wireless_template_group:
        if "template_info" not in data["group_attributes"]:
            data["group_attributes"]["template_info"] = {}
        data["group_attributes"]["template_info"]["Wireless"] = wireless_template_group
    
    result = await _post("/configuration/v2/groups", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def clone_group(
    group_name: str,
    clone_group_name: str
) -> str:
    """
    Clone an existing group.
    
    Args:
        group_name: Name of the group to clone
        clone_group_name: Name for the cloned group
    
    Returns:
        JSON string with clone status
    """
    data = {
        "group": group_name,
        "clone_group": clone_group_name
    }
    result = await _post("/configuration/v2/groups/clone", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_group(group_name: str) -> str:
    """
    Delete a configuration group.
    
    Args:
        group_name: Name of the group to delete
    
    Returns:
        JSON string with deletion status
    """
    result = await _delete(f"/configuration/v1/groups/{group_name}")
    return json.dumps(result, indent=2)


# =============================================================================
# 3. Devices Config Tools (7 tools)
# =============================================================================

@mcp.tool()
async def get_device_group(serial: str) -> str:
    """
    Get the group assignment for a device.
    
    Args:
        serial: Device serial number
    
    Returns:
        JSON string with device group information
    """
    result = await _get(f"/configuration/v1/devices/{serial}/group")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_device_configuration(serial: str) -> str:
    """
    Get running configuration for a device.
    
    Args:
        serial: Device serial number
    
    Returns:
        JSON string with device configuration
    """
    result = await _get(f"/configuration/v1/devices/{serial}/configuration")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_device_config_details(serial: str) -> str:
    """
    Get detailed configuration information for a device.
    
    Args:
        serial: Device serial number
    
    Returns:
        JSON string with device config details
    """
    result = await _get(f"/configuration/v1/devices/{serial}/config_details")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_device_templates(
    device_type: str,
    model: Optional[str] = None,
    version: Optional[str] = None
) -> str:
    """
    Get list of device templates.
    
    Args:
        device_type: Type of device (e.g., IAP, ArubaSwitch)
        model: Optional device model
        version: Optional software version
    
    Returns:
        JSON string with templates list
    """
    params = {"device_type": device_type}
    if model:
        params["model"] = model
    if version:
        params["version"] = version
    
    result = await _get("/configuration/v1/devices/template", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_group_device_templates(
    group_name: str,
    device_type: str
) -> str:
    """
    Get device templates for a specific group.
    
    Args:
        group_name: Name of the group
        device_type: Type of device
    
    Returns:
        JSON string with group device templates
    """
    result = await _get(
        "/configuration/v1/devices/groups/template",
        params={"group": group_name, "device_type": device_type}
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def set_switch_ssh_credentials(
    serial: str,
    username: str,
    password: str
) -> str:
    """
    Set SSH credentials for a switch.
    
    Args:
        serial: Switch serial number
        username: SSH username
        password: SSH password
    
    Returns:
        JSON string with operation status
    """
    data = {
        "username": username,
        "password": password
    }
    result = await _post(f"/configuration/v1/devices/{serial}/ssh_connection", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def move_devices(
    group_name: str,
    serials: List[str]
) -> str:
    """
    Move devices to a different group.
    
    Args:
        group_name: Target group name
        serials: List of device serial numbers
    
    Returns:
        JSON string with move status
    """
    data = {
        "group": group_name,
        "serials": serials
    }
    result = await _post("/configuration/v1/devices/move", json_data=data)
    return json.dumps(result, indent=2)


# =============================================================================
# 4. Templates Tools (3 tools)
# =============================================================================

@mcp.tool()
async def get_templates(
    group_name: str,
    device_type: Optional[str] = None,
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get templates for a group.
    
    Args:
        group_name: Name of the group
        device_type: Optional device type filter
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with templates list
    """
    params = {"offset": offset, "limit": limit}
    if device_type:
        params["device_type"] = device_type
    
    result = await _get(f"/configuration/v1/groups/{group_name}/templates", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_template_text(
    group_name: str,
    template_name: str
) -> str:
    """
    Get the text content of a template.
    
    Args:
        group_name: Name of the group
        template_name: Name of the template
    
    Returns:
        JSON string with template text
    """
    result = await _get(f"/configuration/v1/groups/{group_name}/templates/{template_name}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_template(
    group_name: str,
    template_name: str
) -> str:
    """
    Delete a template from a group.
    
    Args:
        group_name: Name of the group
        template_name: Name of the template to delete
    
    Returns:
        JSON string with deletion status
    """
    result = await _delete(f"/configuration/v1/groups/{group_name}/templates/{template_name}")
    return json.dumps(result, indent=2)


# =============================================================================
# 5. Template Variables Tools (6 tools)
# =============================================================================

@mcp.tool()
async def get_template_variables(serial: str) -> str:
    """
    Get template variables for a specific device.
    
    Args:
        serial: Device serial number
    
    Returns:
        JSON string with template variables
    """
    result = await _get(f"/configuration/v1/devices/{serial}/template_variables")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_all_template_variables(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get template variables for all devices.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with all template variables
    """
    result = await _get(
        "/configuration/v1/devices/template_variables",
        params={"offset": offset, "limit": limit}
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_template_variables(
    serial: str,
    variables: Dict[str, Any]
) -> str:
    """
    Create template variables for a device.
    
    Args:
        serial: Device serial number
        variables: Dictionary of variable name-value pairs
    
    Returns:
        JSON string with creation status
    """
    data = {
        "total": len(variables),
        "variables": variables
    }
    result = await _post(f"/configuration/v1/devices/{serial}/template_variables", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_template_variables(
    serial: str,
    variables: Dict[str, Any]
) -> str:
    """
    Update template variables for a device.
    
    Args:
        serial: Device serial number
        variables: Dictionary of variable name-value pairs to update
    
    Returns:
        JSON string with update status
    """
    data = {
        "total": len(variables),
        "variables": variables
    }
    result = await _patch(f"/configuration/v1/devices/{serial}/template_variables", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def replace_template_variables(
    serial: str,
    variables: Dict[str, Any]
) -> str:
    """
    Replace all template variables for a device.
    
    Args:
        serial: Device serial number
        variables: Dictionary of variable name-value pairs (replaces all)
    
    Returns:
        JSON string with replacement status
    """
    data = {
        "total": len(variables),
        "variables": variables
    }
    result = await _put(f"/configuration/v1/devices/{serial}/template_variables", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_template_variables(
    serial: str,
    variable_names: List[str]
) -> str:
    """
    Delete specific template variables for a device.
    
    Args:
        serial: Device serial number
        variable_names: List of variable names to delete
    
    Returns:
        JSON string with deletion status
    """
    result = await _delete(
        f"/configuration/v1/devices/{serial}/template_variables",
        params={"variables": ",".join(variable_names)}
    )
    return json.dumps(result, indent=2)


# =============================================================================
# 6. AP Settings Tools (2 tools)
# =============================================================================

@mcp.tool()
async def get_ap_settings(serial: str) -> str:
    """
    Get settings for an Access Point.
    
    Args:
        serial: AP serial number
    
    Returns:
        JSON string with AP settings
    """
    result = await _get(f"/configuration/v2/ap_settings/{serial}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_ap_settings(
    serial: str,
    settings: Dict[str, Any]
) -> str:
    """
    Update settings for an Access Point.
    
    Args:
        serial: AP serial number
        settings: Dictionary of settings to update
    
    Returns:
        JSON string with update status
    """
    result = await _patch(f"/configuration/v2/ap_settings/{serial}", json_data=settings)
    return json.dumps(result, indent=2)


# =============================================================================
# 7. AP CLI Config Tools (2 tools)
# =============================================================================

@mcp.tool()
async def get_ap_cli_config(group_or_serial: str) -> str:
    """
    Get AP CLI configuration for a group or specific AP.
    
    Args:
        group_or_serial: Group name or AP serial number
    
    Returns:
        JSON string with AP CLI configuration
    """
    result = await _get(f"/configuration/v1/ap_cli/{group_or_serial}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def replace_ap_cli_config(
    group_or_serial: str,
    cli_commands: List[str]
) -> str:
    """
    Replace AP CLI configuration for a group or specific AP.
    
    Args:
        group_or_serial: Group name or AP serial number
        cli_commands: List of CLI commands
    
    Returns:
        JSON string with operation status
    """
    data = {"clis": cli_commands}
    result = await _post(f"/configuration/v1/ap_cli/{group_or_serial}", json_data=data)
    return json.dumps(result, indent=2)


# =============================================================================
# 8. WLANs Tools (5 tools)
# =============================================================================

@mcp.tool()
async def get_wlan(
    group_name: str,
    wlan_name: str
) -> str:
    """
    Get details of a specific WLAN.
    
    Args:
        group_name: Name of the group
        wlan_name: Name of the WLAN
    
    Returns:
        JSON string with WLAN details
    """
    result = await _get(f"/configuration/full_wlan/{group_name}/{wlan_name}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_all_wlans(
    group_name: str,
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get all WLANs for a group.
    
    Args:
        group_name: Name of the group
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with WLANs list
    """
    result = await _get(
        f"/configuration/v1/wlan/{group_name}",
        params={"offset": offset, "limit": limit}
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_wlan(
    group_name: str,
    wlan_name: str,
    wlan_config: Dict[str, Any]
) -> str:
    """
    Create a new WLAN in a group.
    
    Args:
        group_name: Name of the group
        wlan_name: Name for the new WLAN
        wlan_config: WLAN configuration dictionary
    
    Returns:
        JSON string with creation status
    """
    result = await _post(f"/configuration/v2/wlan/{group_name}/{wlan_name}", json_data=wlan_config)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_wlan(
    group_name: str,
    wlan_name: str,
    wlan_config: Dict[str, Any]
) -> str:
    """
    Update an existing WLAN.
    
    Args:
        group_name: Name of the group
        wlan_name: Name of the WLAN to update
        wlan_config: Updated WLAN configuration dictionary
    
    Returns:
        JSON string with update status
    """
    result = await _patch(f"/configuration/v2/wlan/{group_name}/{wlan_name}", json_data=wlan_config)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_wlan(
    group_name: str,
    wlan_name: str
) -> str:
    """
    Delete a WLAN from a group.
    
    Args:
        group_name: Name of the group
        wlan_name: Name of the WLAN to delete
    
    Returns:
        JSON string with deletion status
    """
    result = await _delete(f"/configuration/v2/wlan/{group_name}/{wlan_name}")
    return json.dumps(result, indent=2)


# =============================================================================
# 9. Device Inventory Tools (4 tools)
# =============================================================================

@mcp.tool()
async def get_device_inventory(
    offset: int = 0,
    limit: int = 100,
    serial: Optional[str] = None,
    mac_address: Optional[str] = None
) -> str:
    """
    Get device inventory.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
        serial: Optional serial number filter
        mac_address: Optional MAC address filter
    
    Returns:
        JSON string with device inventory
    """
    params = {"offset": offset, "limit": limit}
    if serial:
        params["serial"] = serial
    if mac_address:
        params["macaddr"] = mac_address
    
    result = await _get("/platform/device_inventory/v1/devices", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def add_device_to_inventory(
    serials: List[str],
    mac_addresses: List[str]
) -> str:
    """
    Add devices to inventory.
    
    Args:
        serials: List of device serial numbers
        mac_addresses: List of device MAC addresses
    
    Returns:
        JSON string with addition status
    """
    data = [
        {"serial": serial, "mac": mac}
        for serial, mac in zip(serials, mac_addresses)
    ]
    result = await _post("/platform/device_inventory/v1/devices", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def archive_devices(serials: List[str]) -> str:
    """
    Archive devices from inventory.
    
    Args:
        serials: List of device serial numbers to archive
    
    Returns:
        JSON string with archive status
    """
    data = {"serials": serials}
    result = await _post("/platform/device_inventory/v1/devices/archive", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def unarchive_devices(serials: List[str]) -> str:
    """
    Unarchive devices in inventory.
    
    Args:
        serials: List of device serial numbers to unarchive
    
    Returns:
        JSON string with unarchive status
    """
    data = {"serials": serials}
    result = await _post("/platform/device_inventory/v1/devices/unarchive", json_data=data)
    return json.dumps(result, indent=2)


# =============================================================================
# 10. Licensing Tools (8 tools)
# =============================================================================

@mcp.tool()
async def get_subscription_keys(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get subscription keys/licenses.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with subscription keys
    """
    result = await _get(
        "/platform/licensing/v1/subscriptions",
        params={"offset": offset, "limit": limit}
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_enabled_services() -> str:
    """
    Get list of enabled license services.
    
    Returns:
        JSON string with enabled services
    """
    result = await _get("/platform/licensing/v1/services/enabled")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_license_stats() -> str:
    """
    Get license statistics.
    
    Returns:
        JSON string with license stats
    """
    result = await _get("/platform/licensing/v1/stats")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_license_service_config() -> str:
    """
    Get license service configuration.
    
    Returns:
        JSON string with service configuration
    """
    result = await _get("/platform/licensing/v1/services/config")
    return json.dumps(result, indent=2)


@mcp.tool()
async def assign_subscription(
    serials: List[str],
    services: List[str]
) -> str:
    """
    Assign subscription licenses to devices.
    
    Args:
        serials: List of device serial numbers
        services: List of service names to assign
    
    Returns:
        JSON string with assignment status
    """
    data = {
        "serials": serials,
        "services": services
    }
    result = await _post("/platform/licensing/v1/subscriptions/assign", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def unassign_subscription(
    serials: List[str],
    services: List[str]
) -> str:
    """
    Unassign subscription licenses from devices.
    
    Args:
        serials: List of device serial numbers
        services: List of service names to unassign
    
    Returns:
        JSON string with unassignment status
    """
    data = {
        "serials": serials,
        "services": services
    }
    result = await _post("/platform/licensing/v1/subscriptions/unassign", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_auto_license_services() -> str:
    """
    Get auto-license service settings.
    
    Returns:
        JSON string with auto-license settings
    """
    result = await _get("/platform/licensing/v1/customer/settings/autolicense")
    return json.dumps(result, indent=2)


@mcp.tool()
async def assign_auto_license(
    services: List[str],
    device_types: List[str]
) -> str:
    """
    Configure auto-license assignment.
    
    Args:
        services: List of service names to auto-assign
        device_types: List of device types for auto-assignment
    
    Returns:
        JSON string with configuration status
    """
    data = {
        "services": services,
        "device_type": device_types
    }
    result = await _post("/platform/licensing/v1/customer/settings/autolicense", json_data=data)
    return json.dumps(result, indent=2)


# =============================================================================
# 11. Firmware Tools (5 tools)
# =============================================================================

@mcp.tool()
async def get_firmware_swarms(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get firmware compliance status for swarms/clusters.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with swarm firmware info
    """
    result = await _get("/firmware/v1/swarms", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_firmware_versions(
    device_type: str,
    swarm_id: Optional[str] = None
) -> str:
    """
    Get available firmware versions.
    
    Args:
        device_type: Type of device (IAP, MAS, HP, CONTROLLER)
        swarm_id: Optional swarm ID filter
    
    Returns:
        JSON string with firmware versions
    """
    params = {"device_type": device_type}
    if swarm_id:
        params["swarm_id"] = swarm_id
    
    result = await _get("/firmware/v1/versions", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_firmware_upgrade_status(
    swarm_id: Optional[str] = None
) -> str:
    """
    Get firmware upgrade status.
    
    Args:
        swarm_id: Optional swarm ID filter
    
    Returns:
        JSON string with upgrade status
    """
    params = {}
    if swarm_id:
        params["swarm_id"] = swarm_id
    
    result = await _get("/firmware/v1/status", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def upgrade_firmware(
    swarm_id: str,
    firmware_version: str,
    reboot: bool = True
) -> str:
    """
    Initiate firmware upgrade.
    
    Args:
        swarm_id: Swarm/cluster ID
        firmware_version: Target firmware version
        reboot: Whether to reboot after upgrade (default: True)
    
    Returns:
        JSON string with upgrade initiation status
    """
    data = {
        "swarm_id": swarm_id,
        "firmware_version": firmware_version,
        "reboot": reboot
    }
    result = await _post("/firmware/v1/upgrade", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def cancel_firmware_upgrade(swarm_id: str) -> str:
    """
    Cancel an in-progress firmware upgrade.
    
    Args:
        swarm_id: Swarm/cluster ID
    
    Returns:
        JSON string with cancellation status
    """
    data = {"swarm_id": swarm_id}
    result = await _post("/firmware/v1/upgrade/cancel", json_data=data)
    return json.dumps(result, indent=2)


# =============================================================================
# 12. Sites Tools (6 tools)
# =============================================================================

@mcp.tool()
async def get_sites(
    offset: int = 0,
    limit: int = 100,
    calculate_total: bool = False
) -> str:
    """
    Get list of sites.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
        calculate_total: Calculate total count (default: False)
    
    Returns:
        JSON string with sites list
    """
    result = await _get(
        "/central/v2/sites",
        params={"offset": offset, "limit": limit, "calculate_total": calculate_total}
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_site(
    site_name: str,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    zipcode: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> str:
    """
    Create a new site.
    
    Args:
        site_name: Name of the site
        address: Street address
        city: City
        state: State/province
        country: Country
        zipcode: Postal code
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        JSON string with creation status
    """
    data = {"site_name": site_name}
    if address:
        data["address"] = address
    if city:
        data["city"] = city
    if state:
        data["state"] = state
    if country:
        data["country"] = country
    if zipcode:
        data["zipcode"] = zipcode
    if latitude is not None:
        data["latitude"] = latitude
    if longitude is not None:
        data["longitude"] = longitude
    
    result = await _post("/central/v2/sites", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_site(
    site_id: int,
    site_name: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    zipcode: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> str:
    """
    Update an existing site.
    
    Args:
        site_id: Site ID
        site_name: Updated site name
        address: Updated street address
        city: Updated city
        state: Updated state/province
        country: Updated country
        zipcode: Updated postal code
        latitude: Updated latitude
        longitude: Updated longitude
    
    Returns:
        JSON string with update status
    """
    data = {}
    if site_name:
        data["site_name"] = site_name
    if address:
        data["address"] = address
    if city:
        data["city"] = city
    if state:
        data["state"] = state
    if country:
        data["country"] = country
    if zipcode:
        data["zipcode"] = zipcode
    if latitude is not None:
        data["latitude"] = latitude
    if longitude is not None:
        data["longitude"] = longitude
    
    result = await _patch(f"/central/v2/sites/{site_id}", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_site(site_id: int) -> str:
    """
    Delete a site.
    
    Args:
        site_id: Site ID to delete
    
    Returns:
        JSON string with deletion status
    """
    result = await _delete(f"/central/v2/sites/{site_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def associate_devices_to_site(
    site_id: int,
    device_ids: List[str],
    device_type: str
) -> str:
    """
    Associate devices with a site.
    
    Args:
        site_id: Site ID
        device_ids: List of device serial numbers
        device_type: Type of devices (IAP, SWITCH, etc.)
    
    Returns:
        JSON string with association status
    """
    data = {
        "site_id": site_id,
        "device_ids": device_ids,
        "device_type": device_type
    }
    result = await _post("/central/v2/sites/associations", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def unassociate_devices_from_site(
    site_id: int,
    device_ids: List[str],
    device_type: str
) -> str:
    """
    Unassociate devices from a site.
    
    Args:
        site_id: Site ID
        device_ids: List of device serial numbers
        device_type: Type of devices (IAP, SWITCH, etc.)
    
    Returns:
        JSON string with unassociation status
    """
    result = await _delete(
        "/central/v2/sites/associations",
        params={
            "site_id": site_id,
            "device_id": ",".join(device_ids),
            "device_type": device_type
        }
    )
    return json.dumps(result, indent=2)


# =============================================================================
# 13. Topology Tools (6 tools)
# =============================================================================

@mcp.tool()
async def get_topology_site(site_id: Optional[int] = None) -> str:
    """
    Get site topology information.
    
    Args:
        site_id: Optional site ID filter
    
    Returns:
        JSON string with site topology
    """
    params = {}
    if site_id:
        params["site_id"] = site_id
    
    result = await _get("/topology_external_api", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_topology_devices() -> str:
    """
    Get topology devices information.
    
    Returns:
        JSON string with topology devices
    """
    result = await _get("/topology_external_api/devices")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_topology_edges() -> str:
    """
    Get topology edges (connections between devices).
    
    Returns:
        JSON string with topology edges
    """
    result = await _get("/topology_external_api/v2/edges")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_topology_uplinks() -> str:
    """
    Get topology uplink information.
    
    Returns:
        JSON string with topology uplinks
    """
    result = await _get("/topology_external_api/uplinks")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_topology_tunnels() -> str:
    """
    Get topology tunnel information.
    
    Returns:
        JSON string with topology tunnels
    """
    result = await _get("/topology_external_api/tunnels")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_topology_ap_lldp_neighbors(serial: str) -> str:
    """
    Get LLDP neighbors for an Access Point.
    
    Args:
        serial: AP serial number
    
    Returns:
        JSON string with LLDP neighbors
    """
    result = await _get("/topology_external_api/apNeighbors", params={"serial": serial})
    return json.dumps(result, indent=2)


# =============================================================================
# 14. RAPIDS/WIDS Tools (7 tools)
# =============================================================================

@mcp.tool()
async def get_rogue_aps(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of rogue access points.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with rogue APs
    """
    result = await _get("/rapids/v1/rogue_aps", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_interfering_aps(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of interfering access points.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with interfering APs
    """
    result = await _get("/rapids/v1/interfering_aps", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_suspect_aps(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of suspect access points.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with suspect APs
    """
    result = await _get("/rapids/v1/suspect_aps", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_neighbor_aps(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of neighbor access points.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with neighbor APs
    """
    result = await _get("/rapids/v1/neighbor_aps", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_wids_infrastructure_attacks(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get WIDS infrastructure attack events.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with infrastructure attacks
    """
    result = await _get(
        "/rapids/v1/wids/infrastructure_attacks",
        params={"offset": offset, "limit": limit}
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_wids_client_attacks(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get WIDS client attack events.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with client attacks
    """
    result = await _get(
        "/rapids/v1/wids/client_attacks",
        params={"offset": offset, "limit": limit}
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_wids_events(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get WIDS security events.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with WIDS events
    """
    result = await _get("/rapids/v1/wids/events", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


# =============================================================================
# 15. Audit Logs Tools (3 tools)
# =============================================================================

@mcp.tool()
async def get_audit_trail_logs(
    offset: int = 0,
    limit: int = 100,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None
) -> str:
    """
    Get audit trail logs.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
        start_time: Optional start time (Unix timestamp)
        end_time: Optional end time (Unix timestamp)
    
    Returns:
        JSON string with audit logs
    """
    params = {"offset": offset, "limit": limit}
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    
    result = await _get("/platform/auditlogs/v1/logs", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_event_logs(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get event logs.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with event logs
    """
    result = await _get("/auditlogs/v1/events", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_event_details(event_id: str) -> str:
    """
    Get details for a specific event.
    
    Args:
        event_id: Event ID
    
    Returns:
        JSON string with event details
    """
    result = await _get(f"/auditlogs/v1/event_details/{event_id}")
    return json.dumps(result, indent=2)


# =============================================================================
# 16. VisualRF Tools (8 tools)
# =============================================================================

@mcp.tool()
async def get_visualrf_campus_list(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of VisualRF campuses.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with campus list
    """
    result = await _get("/visualrf_api/v1/campus", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_visualrf_campus_info(campus_id: str) -> str:
    """
    Get information for a specific campus.
    
    Args:
        campus_id: Campus ID
    
    Returns:
        JSON string with campus information
    """
    result = await _get(f"/visualrf_api/v1/campus/{campus_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_visualrf_building_info(building_id: str) -> str:
    """
    Get information for a specific building.
    
    Args:
        building_id: Building ID
    
    Returns:
        JSON string with building information
    """
    result = await _get(f"/visualrf_api/v1/building/{building_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_visualrf_floor_info(floor_id: str) -> str:
    """
    Get information for a specific floor.
    
    Args:
        floor_id: Floor ID
    
    Returns:
        JSON string with floor information
    """
    result = await _get(f"/visualrf_api/v1/floor/{floor_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_visualrf_floor_aps(floor_id: str) -> str:
    """
    Get access points on a specific floor.
    
    Args:
        floor_id: Floor ID
    
    Returns:
        JSON string with APs on floor
    """
    result = await _get(f"/visualrf_api/v1/floor/{floor_id}/access_point_location")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_visualrf_floor_clients(floor_id: str) -> str:
    """
    Get clients on a specific floor.
    
    Args:
        floor_id: Floor ID
    
    Returns:
        JSON string with clients on floor
    """
    result = await _get(f"/visualrf_api/v1/floor/{floor_id}/client_location")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_visualrf_client_location(mac_address: str) -> str:
    """
    Get location information for a specific client.
    
    Args:
        mac_address: Client MAC address
    
    Returns:
        JSON string with client location
    """
    result = await _get(f"/visualrf_api/v1/client_location/{mac_address}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_visualrf_rogue_location(mac_address: str) -> str:
    """
    Get location information for a rogue AP.
    
    Args:
        mac_address: Rogue AP MAC address
    
    Returns:
        JSON string with rogue AP location
    """
    result = await _get(f"/visualrf_api/v1/rogue_location/{mac_address}")
    return json.dumps(result, indent=2)


# =============================================================================
# 17. User Management Tools (6 tools)
# =============================================================================

@mcp.tool()
async def list_users(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of users.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with users list
    """
    result = await _get("/platform/rbac/v1/users", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_user(username: str) -> str:
    """
    Get details for a specific user.
    
    Args:
        username: Username
    
    Returns:
        JSON string with user details
    """
    result = await _get(f"/platform/rbac/v1/users/{username}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_user(
    username: str,
    password: str,
    name: str,
    email: str,
    phone: Optional[str] = None
) -> str:
    """
    Create a new user.
    
    Args:
        username: Username for the new user
        password: Password for the new user
        name: Full name
        email: Email address
        phone: Optional phone number
    
    Returns:
        JSON string with creation status
    """
    data = {
        "username": username,
        "password": password,
        "name": name,
        "email": email
    }
    if phone:
        data["phone"] = phone
    
    result = await _post("/platform/rbac/v1/users", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def update_user(
    username: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    password: Optional[str] = None
) -> str:
    """
    Update an existing user.
    
    Args:
        username: Username of the user to update
        name: Updated full name
        email: Updated email address
        phone: Updated phone number
        password: Updated password
    
    Returns:
        JSON string with update status
    """
    data = {}
    if name:
        data["name"] = name
    if email:
        data["email"] = email
    if phone:
        data["phone"] = phone
    if password:
        data["password"] = password
    
    result = await _patch(f"/platform/rbac/v1/users/{username}", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def delete_user(username: str) -> str:
    """
    Delete a user.
    
    Args:
        username: Username of the user to delete
    
    Returns:
        JSON string with deletion status
    """
    result = await _delete(f"/platform/rbac/v1/users/{username}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_roles() -> str:
    """
    Get list of available user roles.
    
    Returns:
        JSON string with roles list
    """
    result = await _get("/platform/rbac/v1/roles")
    return json.dumps(result, indent=2)


# =============================================================================
# 18. MSP Tools (5 tools)
# =============================================================================

@mcp.tool()
async def get_msp_customers(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get list of MSP customers.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with MSP customers
    """
    result = await _get("/msp_api/v2/customers", params={"offset": offset, "limit": limit})
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_msp_customer(
    customer_name: str,
    customer_email: str,
    description: Optional[str] = None
) -> str:
    """
    Create a new MSP customer.
    
    Args:
        customer_name: Name for the new customer
        customer_email: Customer email address
        description: Optional description
    
    Returns:
        JSON string with creation status
    """
    data = {
        "customer_name": customer_name,
        "email": customer_email
    }
    if description:
        data["description"] = description
    
    result = await _post("/msp_api/v1/customers", json_data=data)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_msp_country_codes() -> str:
    """
    Get list of country codes for MSP customers.
    
    Returns:
        JSON string with country codes
    """
    result = await _get("/msp_api/v2/get_country_code")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_msp_devices(
    customer_id: Optional[str] = None
) -> str:
    """
    Get MSP devices.
    
    Args:
        customer_id: Optional customer ID filter
    
    Returns:
        JSON string with MSP devices
    """
    params = {}
    if customer_id:
        params["customer_id"] = customer_id
    
    result = await _get("/msp_api/v1/devices", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_msp_groups(
    customer_id: Optional[str] = None
) -> str:
    """
    Get MSP groups.
    
    Args:
        customer_id: Optional customer ID filter
    
    Returns:
        JSON string with MSP groups
    """
    params = {}
    if customer_id:
        params["customer_id"] = customer_id
    
    result = await _get("/msp_api/v1/groups", params=params)
    return json.dumps(result, indent=2)


# =============================================================================
# 19. Telemetry Tools (1 tool)
# =============================================================================

@mcp.tool()
async def get_all_reporting_radios(
    offset: int = 0,
    limit: int = 100
) -> str:
    """
    Get telemetry data for all reporting radios.
    
    Args:
        offset: Pagination offset (default: 0)
        limit: Maximum number of results (default: 100)
    
    Returns:
        JSON string with radio telemetry data
    """
    result = await _get(
        "/telemetry/v1/reporting_radio_all",
        params={"offset": offset, "limit": limit}
    )
    return json.dumps(result, indent=2)


# =============================================================================
# Server Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Check for SSE transport flag
    transport = "stdio"
    if "--sse" in sys.argv:
        transport = "sse"
        logger.info("Running in SSE mode")
    else:
        logger.info("Running in stdio mode")
    
    # Run the MCP server
    mcp.run(transport=transport)

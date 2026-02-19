"""
Tool Registry for Aruba Central MCP Server

This module contains metadata for all 90 MCP tools organized by category.
Used for semantic filtering to reduce the tool context sent to local LLMs.
"""

# Complete tool registry with metadata for semantic filtering
TOOL_REGISTRY = {
    # OAuth (1 tool)
    "refresh_api_token": {
        "category": "oauth",
        "description": "Manually refresh the OAuth2 access token. Used when the current access token has expired and needs to be renewed using the refresh token.",
        "keywords": ["oauth", "token", "refresh", "authentication", "renew", "access", "credentials"]
    },
    
    # Groups (5 tools)
    "get_groups": {
        "category": "groups",
        "description": "Get list of configuration groups. Returns all configuration groups with pagination support. Groups organize devices with common configuration settings.",
        "keywords": ["groups", "list", "configuration", "get", "view", "show", "display"]
    },
    "get_group_template_info": {
        "category": "groups",
        "description": "Get template information for a specific group. Shows which templates are assigned to the group and template details.",
        "keywords": ["group", "template", "info", "details", "configuration", "assigned"]
    },
    "create_group": {
        "category": "groups",
        "description": "Create a new configuration group. Groups organize devices with common settings for wired and wireless devices.",
        "keywords": ["create", "group", "new", "add", "configuration", "setup"]
    },
    "clone_group": {
        "category": "groups",
        "description": "Clone an existing configuration group. Creates a copy of a group with all its settings and templates.",
        "keywords": ["clone", "copy", "duplicate", "group", "replicate"]
    },
    "delete_group": {
        "category": "groups",
        "description": "Delete a configuration group. Removes the group and its configuration from the system.",
        "keywords": ["delete", "remove", "group", "destroy", "erase"]
    },
    
    # Devices Config (7 tools)
    "get_device_group": {
        "category": "devices",
        "description": "Get the group assignment for a device by serial number. Shows which configuration group the device belongs to.",
        "keywords": ["device", "group", "assignment", "serial", "membership", "belongs"]
    },
    "get_device_configuration": {
        "category": "devices",
        "description": "Get the running configuration for a device. Returns the current active configuration of the device.",
        "keywords": ["device", "configuration", "running", "config", "settings", "current"]
    },
    "get_device_config_details": {
        "category": "devices",
        "description": "Get detailed configuration information for a device including configuration status and details.",
        "keywords": ["device", "configuration", "details", "info", "status"]
    },
    "get_device_templates": {
        "category": "devices",
        "description": "Get list of device templates. Filter by device type like IAP, ArubaSwitch, MobilityController, or CX switches.",
        "keywords": ["device", "templates", "list", "IAP", "switch", "controller", "CX"]
    },
    "get_group_device_templates": {
        "category": "devices",
        "description": "Get device templates for a specific group. Shows all templates assigned to devices in a configuration group.",
        "keywords": ["group", "device", "templates", "assigned", "configuration"]
    },
    "set_switch_ssh_credentials": {
        "category": "devices",
        "description": "Set SSH credentials for a switch device. Configure username and password for SSH access to the switch.",
        "keywords": ["switch", "ssh", "credentials", "username", "password", "access"]
    },
    "move_devices": {
        "category": "devices",
        "description": "Move devices to a different group. Transfer one or more devices from their current group to a target group.",
        "keywords": ["move", "device", "transfer", "group", "migrate", "relocate"]
    },
    
    # Templates (3 tools)
    "get_templates": {
        "category": "templates",
        "description": "Get templates in a configuration group. List all templates of a specific type (IAP, ArubaSwitch, etc.) in a group.",
        "keywords": ["templates", "list", "get", "configuration", "group", "view"]
    },
    "get_template_text": {
        "category": "templates",
        "description": "Get the text content of a template. Returns the actual configuration text/commands in the template.",
        "keywords": ["template", "text", "content", "view", "show", "configuration"]
    },
    "delete_template": {
        "category": "templates",
        "description": "Delete a template from a group. Remove a configuration template from the specified group.",
        "keywords": ["delete", "template", "remove", "erase", "destroy"]
    },
    
    # Template Variables (6 tools)
    "get_template_variables": {
        "category": "variables",
        "description": "Get template variables for a specific device. Returns variable values used in templates for the device.",
        "keywords": ["template", "variables", "device", "values", "parameters"]
    },
    "get_all_template_variables": {
        "category": "variables",
        "description": "Get template variables for all devices. Returns variable values across all devices with pagination.",
        "keywords": ["template", "variables", "all", "devices", "list", "values"]
    },
    "create_template_variables": {
        "category": "variables",
        "description": "Create template variables for a device. Add new variable values to use in device templates.",
        "keywords": ["create", "template", "variables", "add", "new", "device"]
    },
    "update_template_variables": {
        "category": "variables",
        "description": "Update template variables for a device. Modify existing variable values for device templates.",
        "keywords": ["update", "template", "variables", "modify", "change", "device"]
    },
    "replace_template_variables": {
        "category": "variables",
        "description": "Replace all template variables for a device. Completely replace the entire set of template variables.",
        "keywords": ["replace", "template", "variables", "overwrite", "device"]
    },
    "delete_template_variables": {
        "category": "variables",
        "description": "Delete template variables for a device. Remove specific template variable values from a device.",
        "keywords": ["delete", "template", "variables", "remove", "erase", "device"]
    },
    
    # AP Settings (2 tools)
    "get_ap_settings": {
        "category": "ap",
        "description": "Get configuration settings for an access point. Returns AP-specific settings like radio, SSID, and power settings.",
        "keywords": ["access point", "AP", "settings", "configuration", "wireless", "radio"]
    },
    "update_ap_settings": {
        "category": "ap",
        "description": "Update configuration settings for an access point. Modify AP settings like radio power, channel, or SSID.",
        "keywords": ["update", "access point", "AP", "settings", "modify", "change", "wireless"]
    },
    
    # AP CLI Config (2 tools)
    "get_ap_cli_config": {
        "category": "ap",
        "description": "Get CLI configuration for an access point. Returns command-line interface configuration commands for the AP.",
        "keywords": ["access point", "AP", "CLI", "config", "commands", "configuration"]
    },
    "replace_ap_cli_config": {
        "category": "ap",
        "description": "Replace CLI configuration for an access point. Overwrites the entire CLI configuration with new commands.",
        "keywords": ["replace", "access point", "AP", "CLI", "config", "overwrite"]
    },
    
    # WLANs (5 tools)
    "get_wlan": {
        "category": "wlans",
        "description": "Get configuration for a specific WLAN/SSID. Returns wireless network settings including security, VLAN, and radio settings.",
        "keywords": ["WLAN", "SSID", "wireless", "network", "get", "view", "wifi"]
    },
    "get_all_wlans": {
        "category": "wlans",
        "description": "Get all WLAN/SSID configurations in a group. Lists all wireless networks configured in a configuration group.",
        "keywords": ["WLAN", "SSID", "wireless", "networks", "list", "all", "wifi"]
    },
    "create_wlan": {
        "category": "wlans",
        "description": "Create a new WLAN/SSID configuration. Add a new wireless network with security, VLAN, and radio settings.",
        "keywords": ["create", "WLAN", "SSID", "wireless", "network", "new", "add", "wifi"]
    },
    "update_wlan": {
        "category": "wlans",
        "description": "Update an existing WLAN/SSID configuration. Modify wireless network settings like security or VLAN.",
        "keywords": ["update", "WLAN", "SSID", "wireless", "network", "modify", "change", "wifi"]
    },
    "delete_wlan": {
        "category": "wlans",
        "description": "Delete a WLAN/SSID configuration. Remove a wireless network from the configuration group.",
        "keywords": ["delete", "WLAN", "SSID", "wireless", "network", "remove", "erase", "wifi"]
    },
    
    # Device Inventory (4 tools)
    "get_device_inventory": {
        "category": "inventory",
        "description": "Get device inventory list. Returns all devices with details like serial, MAC, model, and status.",
        "keywords": ["inventory", "devices", "list", "hardware", "equipment", "assets"]
    },
    "add_device_to_inventory": {
        "category": "inventory",
        "description": "Add a device to inventory. Register a new device using serial number and MAC address.",
        "keywords": ["add", "device", "inventory", "register", "new", "onboard"]
    },
    "archive_devices": {
        "category": "inventory",
        "description": "Archive devices from inventory. Move devices to archived state to hide them from active inventory.",
        "keywords": ["archive", "device", "inventory", "hide", "deactivate", "remove"]
    },
    "unarchive_devices": {
        "category": "inventory",
        "description": "Unarchive devices to inventory. Restore archived devices back to active inventory.",
        "keywords": ["unarchive", "device", "inventory", "restore", "reactivate", "recover"]
    },
    
    # Licensing (8 tools)
    "get_subscription_keys": {
        "category": "licensing",
        "description": "Get subscription license keys. Returns all subscription keys with their status and expiration.",
        "keywords": ["subscription", "license", "keys", "list", "view", "show"]
    },
    "get_enabled_services": {
        "category": "licensing",
        "description": "Get enabled services for devices. Shows which licensed services are active on specific devices.",
        "keywords": ["services", "enabled", "license", "active", "features"]
    },
    "get_license_stats": {
        "category": "licensing",
        "description": "Get license statistics and usage. Returns counts of license assignments, available licenses, and consumption.",
        "keywords": ["license", "statistics", "stats", "usage", "consumption", "summary"]
    },
    "get_license_service_config": {
        "category": "licensing",
        "description": "Get license service configuration. Returns settings for license services like Foundation, Advanced, etc.",
        "keywords": ["license", "service", "configuration", "settings", "foundation", "advanced"]
    },
    "assign_subscription": {
        "category": "licensing",
        "description": "Assign subscription license to devices. Allocate a subscription key to specific devices or device types.",
        "keywords": ["assign", "subscription", "license", "allocate", "device"]
    },
    "unassign_subscription": {
        "category": "licensing",
        "description": "Unassign subscription license from devices. Remove subscription allocation from devices.",
        "keywords": ["unassign", "subscription", "license", "remove", "deallocate", "device"]
    },
    "get_auto_license_services": {
        "category": "licensing",
        "description": "Get auto-licensing services configuration. Shows which services are set for automatic license assignment.",
        "keywords": ["auto", "license", "services", "automatic", "assignment"]
    },
    "assign_auto_license": {
        "category": "licensing",
        "description": "Configure auto-licensing for services. Set services to automatically assign licenses to eligible devices.",
        "keywords": ["assign", "auto", "license", "automatic", "configure", "enable"]
    },
    
    # Firmware (5 tools)
    "get_firmware_swarms": {
        "category": "firmware",
        "description": "Get firmware information for device swarms. Returns firmware versions for swarm clusters.",
        "keywords": ["firmware", "swarms", "cluster", "version", "software"]
    },
    "get_firmware_versions": {
        "category": "firmware",
        "description": "Get available firmware versions. Lists firmware images available for device types like IAP, AOS, or CX.",
        "keywords": ["firmware", "versions", "available", "images", "software", "list"]
    },
    "get_firmware_upgrade_status": {
        "category": "firmware",
        "description": "Get status of firmware upgrades. Returns progress and status of ongoing firmware upgrade operations.",
        "keywords": ["firmware", "upgrade", "status", "progress", "update"]
    },
    "upgrade_firmware": {
        "category": "firmware",
        "description": "Upgrade device firmware. Start a firmware upgrade operation for devices to a specific version.",
        "keywords": ["upgrade", "firmware", "update", "install", "deploy", "software"]
    },
    "cancel_firmware_upgrade": {
        "category": "firmware",
        "description": "Cancel an ongoing firmware upgrade. Stop a firmware upgrade operation that is in progress.",
        "keywords": ["cancel", "firmware", "upgrade", "stop", "abort", "halt"]
    },
    
    # Sites (6 tools)
    "get_sites": {
        "category": "sites",
        "description": "Get list of sites. Returns all sites with location information including address and geolocation.",
        "keywords": ["sites", "locations", "list", "buildings", "facilities", "campus"]
    },
    "create_site": {
        "category": "sites",
        "description": "Create a new site. Add a new physical location with address, city, state, and country information.",
        "keywords": ["create", "site", "location", "new", "add", "building"]
    },
    "update_site": {
        "category": "sites",
        "description": "Update an existing site. Modify site information like address, name, or location details.",
        "keywords": ["update", "site", "location", "modify", "change", "edit"]
    },
    "delete_site": {
        "category": "sites",
        "description": "Delete a site. Remove a site location from the system.",
        "keywords": ["delete", "site", "location", "remove", "erase"]
    },
    "associate_devices_to_site": {
        "category": "sites",
        "description": "Associate devices to a site. Link devices to a physical location for organization and management.",
        "keywords": ["associate", "device", "site", "assign", "link", "location"]
    },
    "unassociate_devices_from_site": {
        "category": "sites",
        "description": "Unassociate devices from a site. Remove device association from a physical location.",
        "keywords": ["unassociate", "device", "site", "remove", "unlink", "location"]
    },
    
    # Topology (6 tools)
    "get_topology_site": {
        "category": "topology",
        "description": "Get network topology for a site. Returns device connections and network layout for a physical location.",
        "keywords": ["topology", "site", "network", "layout", "connections", "map"]
    },
    "get_topology_devices": {
        "category": "topology",
        "description": "Get topology for specific devices. Shows network connections and neighbors for selected devices.",
        "keywords": ["topology", "devices", "network", "connections", "neighbors"]
    },
    "get_topology_edges": {
        "category": "topology",
        "description": "Get topology edges (connections). Returns network links and connections between devices.",
        "keywords": ["topology", "edges", "connections", "links", "network", "wiring"]
    },
    "get_topology_uplinks": {
        "category": "topology",
        "description": "Get topology uplinks. Shows uplink connections from access points to switches or gateways.",
        "keywords": ["topology", "uplinks", "connections", "AP", "switch", "gateway"]
    },
    "get_topology_tunnels": {
        "category": "topology",
        "description": "Get topology tunnels. Returns VPN and overlay tunnel connections in the network.",
        "keywords": ["topology", "tunnels", "VPN", "overlay", "connections"]
    },
    "get_topology_ap_lldp_neighbors": {
        "category": "topology",
        "description": "Get LLDP neighbors for access points. Returns Link Layer Discovery Protocol neighbor information for APs.",
        "keywords": ["topology", "LLDP", "neighbors", "access point", "AP", "discovery"]
    },
    
    # RAPIDS/WIDS Security (7 tools)
    "get_rogue_aps": {
        "category": "security",
        "description": "Get detected rogue access points. Returns unauthorized APs detected by the wireless intrusion detection system.",
        "keywords": ["rogue", "access point", "AP", "security", "threat", "unauthorized", "WIDS"]
    },
    "get_interfering_aps": {
        "category": "security",
        "description": "Get interfering access points. Returns APs causing interference on wireless channels.",
        "keywords": ["interfering", "access point", "AP", "interference", "noise", "wireless"]
    },
    "get_suspect_aps": {
        "category": "security",
        "description": "Get suspect access points. Returns APs flagged as potentially malicious by the security system.",
        "keywords": ["suspect", "access point", "AP", "security", "threat", "suspicious"]
    },
    "get_neighbor_aps": {
        "category": "security",
        "description": "Get neighbor access points. Returns nearby APs detected but not part of the network.",
        "keywords": ["neighbor", "access point", "AP", "nearby", "detected", "external"]
    },
    "get_wids_infrastructure_attacks": {
        "category": "security",
        "description": "Get wireless infrastructure attacks. Returns detected attacks targeting network infrastructure.",
        "keywords": ["WIDS", "infrastructure", "attacks", "security", "threats", "wireless"]
    },
    "get_wids_client_attacks": {
        "category": "security",
        "description": "Get wireless client attacks. Returns detected attacks targeting wireless clients.",
        "keywords": ["WIDS", "client", "attacks", "security", "threats", "wireless"]
    },
    "get_wids_events": {
        "category": "security",
        "description": "Get wireless intrusion detection events. Returns all WIDS events including attacks and anomalies.",
        "keywords": ["WIDS", "events", "security", "intrusion", "detection", "wireless"]
    },
    
    # Audit Logs (3 tools)
    "get_audit_trail_logs": {
        "category": "audit",
        "description": "Get audit trail logs. Returns administrative activity logs including user actions and configuration changes.",
        "keywords": ["audit", "trail", "logs", "activity", "changes", "history", "admin"]
    },
    "get_event_logs": {
        "category": "audit",
        "description": "Get system event logs. Returns general system events, alerts, and operational logs.",
        "keywords": ["event", "logs", "system", "alerts", "notifications", "history"]
    },
    "get_event_details": {
        "category": "audit",
        "description": "Get details for a specific event. Returns detailed information about a particular event log entry.",
        "keywords": ["event", "details", "log", "information", "specific"]
    },
    
    # VisualRF (8 tools)
    "get_visualrf_campus_list": {
        "category": "visualrf",
        "description": "Get list of VisualRF campuses. Returns campus floor plan locations configured in VisualRF.",
        "keywords": ["visualrf", "campus", "list", "floor plans", "maps", "locations"]
    },
    "get_visualrf_campus_info": {
        "category": "visualrf",
        "description": "Get information about a specific campus. Returns campus details and associated buildings.",
        "keywords": ["visualrf", "campus", "info", "details", "buildings"]
    },
    "get_visualrf_building_info": {
        "category": "visualrf",
        "description": "Get information about a building. Returns building details and floor plans.",
        "keywords": ["visualrf", "building", "info", "details", "floors"]
    },
    "get_visualrf_floor_info": {
        "category": "visualrf",
        "description": "Get floor plan information. Returns details about a specific floor including dimensions and image.",
        "keywords": ["visualrf", "floor", "plan", "info", "map", "layout"]
    },
    "get_visualrf_floor_aps": {
        "category": "visualrf",
        "description": "Get access points on a floor plan. Returns AP locations and placements on the floor map.",
        "keywords": ["visualrf", "floor", "access points", "AP", "locations", "placement"]
    },
    "get_visualrf_floor_clients": {
        "category": "visualrf",
        "description": "Get client locations on a floor plan. Returns wireless client positions on the floor map.",
        "keywords": ["visualrf", "floor", "clients", "locations", "positioning", "map"]
    },
    "get_visualrf_client_location": {
        "category": "visualrf",
        "description": "Get specific client location. Returns precise location coordinates for a wireless client.",
        "keywords": ["visualrf", "client", "location", "position", "coordinates", "tracking"]
    },
    "get_visualrf_rogue_location": {
        "category": "visualrf",
        "description": "Get rogue AP location on floor plan. Returns location of detected rogue access point.",
        "keywords": ["visualrf", "rogue", "location", "AP", "threat", "position"]
    },
    
    # User Management (6 tools)
    "list_users": {
        "category": "users",
        "description": "List all users in the system. Returns user accounts with roles and permissions.",
        "keywords": ["users", "list", "accounts", "administrators", "management"]
    },
    "get_user": {
        "category": "users",
        "description": "Get details for a specific user. Returns user information including role and permissions.",
        "keywords": ["user", "get", "details", "account", "info"]
    },
    "create_user": {
        "category": "users",
        "description": "Create a new user account. Add a new user with username, password, role, and permissions.",
        "keywords": ["create", "user", "account", "new", "add", "administrator"]
    },
    "update_user": {
        "category": "users",
        "description": "Update an existing user account. Modify user details, role, or permissions.",
        "keywords": ["update", "user", "account", "modify", "change", "edit"]
    },
    "delete_user": {
        "category": "users",
        "description": "Delete a user account. Remove a user from the system.",
        "keywords": ["delete", "user", "account", "remove", "erase"]
    },
    "get_roles": {
        "category": "users",
        "description": "Get available user roles. Returns list of roles and their permission levels.",
        "keywords": ["roles", "permissions", "list", "access", "privileges"]
    },
    
    # MSP (5 tools)
    "get_msp_customers": {
        "category": "msp",
        "description": "Get list of MSP customers. Returns managed service provider customer accounts.",
        "keywords": ["MSP", "customers", "list", "managed", "service", "tenants"]
    },
    "create_msp_customer": {
        "category": "msp",
        "description": "Create a new MSP customer. Add a new managed customer account with details.",
        "keywords": ["create", "MSP", "customer", "new", "add", "tenant"]
    },
    "get_msp_country_codes": {
        "category": "msp",
        "description": "Get country codes for MSP customers. Returns list of valid country codes for customer creation.",
        "keywords": ["MSP", "country", "codes", "list", "locations"]
    },
    "get_msp_devices": {
        "category": "msp",
        "description": "Get devices for an MSP customer. Returns device inventory for a specific managed customer.",
        "keywords": ["MSP", "devices", "customer", "inventory", "list"]
    },
    "get_msp_groups": {
        "category": "msp",
        "description": "Get groups for an MSP customer. Returns configuration groups for a specific managed customer.",
        "keywords": ["MSP", "groups", "customer", "configuration", "list"]
    },
    
    # Telemetry (1 tool)
    "get_all_reporting_radios": {
        "category": "telemetry",
        "description": "Get telemetry reporting radios. Returns radio information for devices reporting telemetry data.",
        "keywords": ["telemetry", "radios", "reporting", "monitoring", "data", "wireless"]
    }
}


def get_tool_categories():
    """Get unique categories from the tool registry."""
    return sorted(set(tool["category"] for tool in TOOL_REGISTRY.values()))


def get_tools_by_category(category):
    """Get all tool names for a specific category."""
    return [name for name, metadata in TOOL_REGISTRY.items() if metadata["category"] == category]


def get_tool_count_by_category():
    """Get count of tools per category."""
    from collections import Counter
    categories = [tool["category"] for tool in TOOL_REGISTRY.values()]
    return dict(Counter(categories))


if __name__ == "__main__":
    print("Aruba Central MCP Server Tool Registry")
    print("=" * 60)
    print(f"\nTotal tools: {len(TOOL_REGISTRY)}")
    print(f"Total categories: {len(get_tool_categories())}")
    
    print("\nTools per category:")
    for category, count in sorted(get_tool_count_by_category().items()):
        print(f"  {category:20s}: {count:2d} tools")
    
    print("\nSample tool metadata:")
    sample_tool = "get_wlan"
    metadata = TOOL_REGISTRY[sample_tool]
    print(f"\nTool: {sample_tool}")
    print(f"Category: {metadata['category']}")
    print(f"Description: {metadata['description']}")
    print(f"Keywords: {', '.join(metadata['keywords'])}")

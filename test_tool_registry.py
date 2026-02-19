#!/usr/bin/env python3
"""
Test script for the tool registry and basic functionality.
This tests the core logic without requiring external model downloads.
"""

import sys
from tool_registry import (
    TOOL_REGISTRY,
    get_tool_categories,
    get_tools_by_category,
    get_tool_count_by_category
)


def test_tool_registry():
    """Test the tool registry structure and contents."""
    print("Testing Tool Registry...")
    
    # Test 1: Verify we have 90 tools (calculated from expected counts)
    expected_total = sum([1, 5, 7, 3, 6, 4, 5, 4, 8, 5, 6, 6, 7, 3, 8, 6, 5, 1])  # Sum of all category counts
    assert len(TOOL_REGISTRY) == expected_total, f"Expected {expected_total} tools, got {len(TOOL_REGISTRY)}"
    print(f"  ✓ Registry contains {expected_total} tools")
    
    # Test 2: Verify all tools have required fields
    required_fields = {'category', 'description', 'keywords'}
    for tool_name, metadata in TOOL_REGISTRY.items():
        assert isinstance(metadata, dict), f"Tool {tool_name} metadata is not a dict"
        assert required_fields.issubset(metadata.keys()), \
            f"Tool {tool_name} missing required fields: {required_fields - set(metadata.keys())}"
        assert isinstance(metadata['keywords'], list), \
            f"Tool {tool_name} keywords is not a list"
        assert len(metadata['description']) > 0, \
            f"Tool {tool_name} has empty description"
    print("  ✓ All tools have required fields (category, description, keywords)")
    
    # Test 3: Verify expected categories exist
    expected_categories = {
        'oauth', 'groups', 'devices', 'templates', 'variables', 'ap', 'wlans',
        'inventory', 'licensing', 'firmware', 'sites', 'topology', 'security',
        'audit', 'visualrf', 'users', 'msp', 'telemetry'
    }
    actual_categories = set(get_tool_categories())
    assert expected_categories == actual_categories, \
        f"Category mismatch. Missing: {expected_categories - actual_categories}, Extra: {actual_categories - expected_categories}"
    print(f"  ✓ All 18 expected categories present")
    
    # Test 4: Verify tool counts per category match spec
    expected_counts = {
        'oauth': 1,
        'groups': 5,
        'devices': 7,
        'templates': 3,
        'variables': 6,
        'ap': 4,  # 2 ap_settings + 2 ap_cli_config
        'wlans': 5,
        'inventory': 4,
        'licensing': 8,
        'firmware': 5,
        'sites': 6,
        'topology': 6,
        'security': 7,
        'audit': 3,
        'visualrf': 8,
        'users': 6,
        'msp': 5,
        'telemetry': 1
    }
    
    actual_counts = get_tool_count_by_category()
    for category, expected_count in expected_counts.items():
        actual_count = actual_counts.get(category, 0)
        assert actual_count == expected_count, \
            f"Category '{category}' has {actual_count} tools, expected {expected_count}"
    print("  ✓ Tool counts per category match specification")
    
    # Test 5: Verify specific tools exist
    required_tools = [
        'refresh_api_token',
        'get_groups', 'create_group',
        'get_device_configuration',
        'get_wlan', 'create_wlan',
        'get_sites', 'create_site',
        'get_firmware_versions',
        'list_users'
    ]
    for tool_name in required_tools:
        assert tool_name in TOOL_REGISTRY, f"Required tool '{tool_name}' not found"
    print(f"  ✓ All {len(required_tools)} sampled required tools present")
    
    # Test 6: Test helper functions
    oauth_tools = get_tools_by_category('oauth')
    assert len(oauth_tools) == 1, "OAuth category should have 1 tool"
    assert 'refresh_api_token' in oauth_tools, "OAuth tool not found"
    print("  ✓ Helper functions work correctly")
    
    print("\n✅ All tool registry tests passed!\n")
    return True


def test_sample_queries():
    """Test that we can match tools to sample queries (basic keyword matching)."""
    print("Testing Sample Query Matching (Basic)...")
    
    # Test queries and expected tool categories
    test_cases = [
        ("wireless networks", {"wlans", "ap"}),
        ("firmware upgrade", {"firmware"}),
        ("create site", {"sites"}),
        ("license", {"licensing"}),
        ("rogue access point", {"security"}),
    ]
    
    for query, expected_categories in test_cases:
        query_lower = query.lower()
        matched_tools = []
        
        # Simple keyword matching to verify tool descriptions are relevant
        for tool_name, metadata in TOOL_REGISTRY.items():
            description_lower = metadata['description'].lower()
            keywords_lower = ' '.join(metadata['keywords']).lower()
            
            if any(word in description_lower or word in keywords_lower 
                   for word in query_lower.split()):
                matched_tools.append((tool_name, metadata['category']))
        
        # Check that at least one tool from expected categories was matched
        matched_categories = {cat for _, cat in matched_tools}
        assert len(matched_categories & expected_categories) > 0, \
            f"Query '{query}' didn't match expected categories. Got: {matched_categories}, Expected: {expected_categories}"
        print(f"  ✓ Query '{query}' matched {len(matched_tools)} tools")
    
    print("\n✅ All query matching tests passed!\n")
    return True


def main():
    """Run all tests."""
    print("=" * 80)
    print("Tool Registry Test Suite")
    print("=" * 80)
    print()
    
    try:
        test_tool_registry()
        test_sample_queries()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Tests for scitex_capture._mcp.tool_schemas."""

import pytest


class TestToolSchemas:
    def test_module_importable_hasattr_tool_schemas_get_tool_schemas(self):
        # Arrange
        pytest.importorskip("mcp")
        # Act
        from scitex_capture._mcp import tool_schemas

        # Assert
        assert hasattr(tool_schemas, "get_tool_schemas")

    def test_get_tool_schemas_returns_list_schemas_is_list(self):
        # Arrange
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas
        # Act
        schemas = get_tool_schemas()
        # Act
        # Assert
        # Assert
        assert isinstance(schemas, list)

    def test_get_tool_schemas_returns_list_len_schemas_0(self):
        # Arrange
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas
        # Act
        schemas = get_tool_schemas()
        # Act
        # Assert
        # Assert
        assert len(schemas) > 0


    def test_each_schema_has_required_fields(self):
        # Arrange
        # Act
        # Assert
        mcp_types = pytest.importorskip("mcp.types")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas

        for tool in get_tool_schemas():
            assert isinstance(tool, mcp_types.Tool)
            assert tool.name
            assert tool.description
            assert tool.inputSchema is not None


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])

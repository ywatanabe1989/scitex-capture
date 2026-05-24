#!/usr/bin/env python3
"""Tests for scitex_capture._mcp.tool_schemas."""

import pytest


class TestToolSchemas:
    def test_module_exposes_get_tool_schemas(self):
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp import tool_schemas

        # Act
        has_factory = hasattr(tool_schemas, "get_tool_schemas")
        # Assert
        assert has_factory

    def test_get_tool_schemas_returns_a_list(self):
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas

        # Act
        schemas = get_tool_schemas()
        # Assert
        assert isinstance(schemas, list)

    def test_get_tool_schemas_returns_non_empty_list(self):
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas

        # Act
        schemas = get_tool_schemas()
        # Assert
        assert len(schemas) > 0

    def test_every_schema_is_an_mcp_tool_instance(self):
        # Arrange
        mcp_types = pytest.importorskip("mcp.types")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas

        # Act
        schemas = get_tool_schemas()
        # Assert
        assert all(isinstance(tool, mcp_types.Tool) for tool in schemas)

    def test_every_schema_has_a_non_empty_name(self):
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas

        # Act
        schemas = get_tool_schemas()
        # Assert
        assert all(tool.name for tool in schemas)

    def test_every_schema_has_a_non_empty_description(self):
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas

        # Act
        schemas = get_tool_schemas()
        # Assert
        assert all(tool.description for tool in schemas)

    def test_every_schema_declares_an_input_schema(self):
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp.tool_schemas import get_tool_schemas

        # Act
        schemas = get_tool_schemas()
        # Assert
        assert all(tool.inputSchema is not None for tool in schemas)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])

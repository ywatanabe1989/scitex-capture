#!/usr/bin/env python3
"""Smoke tests for scitex_capture._mcp.handlers."""

import pytest


class TestHandlersModule:
    def test_module_importable_handlers_is_not_none(self):
        # Arrange
        pytest.importorskip("mcp")
        # Act
        from scitex_capture._mcp import handlers

        # Assert
        assert handlers is not None

    def test_module_has_callables(self):
        # Arrange
        pytest.importorskip("mcp")
        from scitex_capture._mcp import handlers

        # Act
        callables = [
            name
            for name in dir(handlers)
            if not name.startswith("_") and callable(getattr(handlers, name))
        ]
        # Assert
        assert callables, "expected at least one public callable in handlers"


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])

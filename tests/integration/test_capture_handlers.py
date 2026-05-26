#!/usr/bin/env python3
"""Tests for capture MCP handlers."""

import pytest


class TestCaptureScreenshotHandler:
    """Tests for capture_screenshot_handler."""

    @pytest.mark.asyncio
    async def test_capture_screenshot_returns_dict_result_is_dict(self):
        # Arrange
        from scitex_capture._mcp.handlers import capture_screenshot_handler
        # Act
        result = await capture_screenshot_handler(return_base64=False)
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_capture_screenshot_returns_dict_success_in_result(self):
        # Arrange
        from scitex_capture._mcp.handlers import capture_screenshot_handler
        # Act
        result = await capture_screenshot_handler(return_base64=False)
        # Assert
        assert "success" in result


    @pytest.mark.asyncio
    async def test_capture_screenshot_with_base64_result_is_dict(self):
        # Arrange
        from scitex_capture._mcp.handlers import capture_screenshot_handler
        # Act
        result = await capture_screenshot_handler(return_base64=True)
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_capture_screenshot_with_base64_success_in_result(self):
        # Arrange
        from scitex_capture._mcp.handlers import capture_screenshot_handler
        # Act
        result = await capture_screenshot_handler(return_base64=True)
        # Assert
        assert "success" in result



class TestMonitoringHandlers:
    """Tests for monitoring-related handlers."""

    @pytest.mark.asyncio
    async def test_get_monitoring_status_result_is_dict(self):
        # Arrange
        from scitex_capture._mcp.handlers import get_monitoring_status_handler
        # Act
        result = await get_monitoring_status_handler()
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_monitoring_status_success_in_result(self):
        # Arrange
        from scitex_capture._mcp.handlers import get_monitoring_status_handler
        # Act
        result = await get_monitoring_status_handler()
        # Assert
        assert "success" in result


    @pytest.mark.asyncio
    async def test_stop_monitoring_when_not_running(self):
        """Test stop monitoring when not running."""
        # Arrange
        from scitex_capture._mcp.handlers import stop_monitoring_handler

        # Act
        result = await stop_monitoring_handler()
        # Assert
        assert isinstance(result, dict)


class TestListRecentScreenshotsHandler:
    """Tests for list_recent_screenshots_handler."""

    @pytest.mark.asyncio
    async def test_list_recent_screenshots_default_result_is_dict(self):
        # Arrange
        from scitex_capture._mcp.handlers import list_recent_screenshots_handler
        # Act
        result = await list_recent_screenshots_handler()
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_list_recent_screenshots_default_success_in_result(self):
        # Arrange
        from scitex_capture._mcp.handlers import list_recent_screenshots_handler
        # Act
        result = await list_recent_screenshots_handler()
        # Assert
        assert "success" in result


    @pytest.mark.asyncio
    async def test_list_recent_screenshots_with_limit_result_is_dict(self):
        # Arrange
        from scitex_capture._mcp.handlers import list_recent_screenshots_handler
        # Act
        result = await list_recent_screenshots_handler(limit=5)
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_list_recent_screenshots_with_limit_success_in_result(self):
        # Arrange
        from scitex_capture._mcp.handlers import list_recent_screenshots_handler
        # Act
        result = await list_recent_screenshots_handler(limit=5)
        # Assert
        assert "success" in result



class TestListSessionsHandler:
    """Tests for list_sessions_handler."""

    @pytest.mark.asyncio
    async def test_list_sessions_result_is_dict(self):
        # Arrange
        from scitex_capture._mcp.handlers import list_sessions_handler
        # Act
        result = await list_sessions_handler(limit=10)
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_list_sessions_success_in_result(self):
        # Arrange
        from scitex_capture._mcp.handlers import list_sessions_handler
        # Act
        result = await list_sessions_handler(limit=10)
        # Assert
        assert "success" in result



class TestGetInfoHandler:
    """Tests for get_info_handler."""

    @pytest.mark.asyncio
    async def test_get_info_result_is_dict(self):
        # Arrange
        from scitex_capture._mcp.handlers import get_info_handler
        # Act
        result = await get_info_handler()
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_info_success_in_result(self):
        # Arrange
        from scitex_capture._mcp.handlers import get_info_handler
        # Act
        result = await get_info_handler()
        # Assert
        assert "success" in result



if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

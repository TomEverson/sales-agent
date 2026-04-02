"""Tests for salebot/mcp_tools.py — Payment flow tools (TB-34)."""

import pytest

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tools import (
    TOOLS,
    execute_initiate_payment,
    execute_confirm_payment,
    execute_check_payment_status,
    execute_tool,
)


class TestPaymentToolDefinitions:
    def _get_tool(self, name):
        return next(t for t in TOOLS if t["name"] == name)

    def test_initiate_payment_tool_exists(self):
        """TB-34: initiate_payment tool exists in TOOLS list."""
        names = [t["name"] for t in TOOLS]
        assert "initiate_payment" in names

    def test_confirm_payment_tool_exists(self):
        """TB-34: confirm_payment tool exists in TOOLS list."""
        names = [t["name"] for t in TOOLS]
        assert "confirm_payment" in names

    def test_check_payment_status_tool_exists(self):
        """TB-34: check_payment_status tool exists in TOOLS list."""
        names = [t["name"] for t in TOOLS]
        assert "check_payment_status" in names

    def test_initiate_payment_tool_valid_format(self):
        """TB-34: initiate_payment_tool has name, description, and input_schema."""
        tool = self._get_tool("initiate_payment")
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_initiate_payment_amount_required(self):
        """TB-34: amount is the required field for initiate_payment."""
        tool = self._get_tool("initiate_payment")
        assert "amount" in tool["input_schema"]["required"]

    def test_confirm_payment_booking_reference_required(self):
        """TB-34: booking_reference is required for confirm_payment."""
        tool = self._get_tool("confirm_payment")
        assert "booking_reference" in tool["input_schema"]["required"]

    def test_check_payment_status_booking_reference_required(self):
        """TB-34: booking_reference is required for check_payment_status."""
        tool = self._get_tool("check_payment_status")
        assert "booking_reference" in tool["input_schema"]["required"]


class TestPaymentExecutorFunctions:
    @pytest.mark.asyncio
    async def test_execute_initiate_payment_requires_amount(self):
        """TB-34: execute_initiate_payment returns error when amount is missing."""
        result = await execute_initiate_payment({})
        assert "amount is required" in result

    @pytest.mark.asyncio
    async def test_execute_confirm_payment_requires_booking_reference(self):
        """TB-34: execute_confirm_payment returns error when booking_reference is missing."""
        result = await execute_confirm_payment({})
        assert "booking_reference is required" in result

    @pytest.mark.asyncio
    async def test_execute_check_payment_status_requires_booking_reference(self):
        """TB-34: execute_check_payment_status returns error when booking_reference is missing."""
        result = await execute_check_payment_status({})
        assert "booking_reference is required" in result

    @pytest.mark.asyncio
    async def test_execute_tool_dispatches_payment_tools(self):
        """TB-34: execute_tool dispatcher handles new payment tools."""
        result = await execute_tool("initiate_payment", {"amount": 100.0})
        assert "unavailable" in result or "Payment initiated" in result

        result = await execute_tool(
            "confirm_payment", {"booking_reference": "TEST-123"}
        )
        assert "not found" in result or "confirmed" in result or "unavailable" in result

        result = await execute_tool(
            "check_payment_status", {"booking_reference": "TEST-123"}
        )
        assert "not found" in result or "Status" in result or "unavailable" in result

    @pytest.mark.asyncio
    async def test_execute_tool_unknown_tool_returns_error(self):
        """TB-34: execute_tool returns error for unknown tool."""
        result = await execute_tool("nonexistent_tool", {})
        assert "Unknown tool" in result

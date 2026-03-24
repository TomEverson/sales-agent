"""Tests for salebot/package_builder.py — FR-7: Package Builder."""

import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from package_builder import (
    PackageActivity,
    TourPackage,
    format_stars,
    format_price,
    calculate_total,
    format_package,
    format_tweak_invitation,
)


# ---------------------------------------------------------------------------
# TestFormatStars
# ---------------------------------------------------------------------------


class TestFormatStars:
    def test_four_stars(self):
        """FR-7: 4 stars returns 4 star emoji per spec."""
        assert format_stars(4) == "⭐⭐⭐⭐"

    def test_five_stars(self):
        """FR-7: 5 stars returns 5 star emoji per spec."""
        assert format_stars(5) == "⭐⭐⭐⭐⭐"

    def test_one_star(self):
        """FR-7: 1 star returns 1 star emoji per spec."""
        assert format_stars(1) == "⭐"

    def test_zero_stars_returns_one(self):
        """FR-7: 0 or below returns minimum 1 star per spec."""
        assert format_stars(0) == "⭐"

    def test_negative_stars_returns_one(self):
        """FR-7: negative value returns minimum 1 star per spec."""
        assert format_stars(-3) == "⭐"

    def test_six_stars_capped_at_five(self):
        """FR-7: above 5 is capped at 5 stars per spec."""
        assert format_stars(6) == "⭐⭐⭐⭐⭐"


# ---------------------------------------------------------------------------
# TestFormatPrice
# ---------------------------------------------------------------------------


class TestFormatPrice:
    def test_whole_number(self):
        """FR-7: whole number shows two decimal places per spec."""
        assert format_price(85.0) == "$85.00"

    def test_decimal_number(self):
        """FR-7: decimal price is formatted correctly per spec."""
        assert format_price(1200.5) == "$1200.50"

    def test_starts_with_dollar_sign(self):
        """FR-7: price always starts with dollar sign per spec."""
        assert format_price(42.0).startswith("$")

    def test_large_price(self):
        """FR-7: large price formats correctly per spec."""
        assert format_price(9999.99) == "$9999.99"

    def test_zero_price(self):
        """FR-7: zero formats as $0.00 per spec."""
        assert format_price(0) == "$0.00"


# ---------------------------------------------------------------------------
# TestCalculateTotal
# ---------------------------------------------------------------------------


class TestCalculateTotal:
    def test_sums_flight_hotel_activities(self, sample_package_no_transport):
        """FR-7: total includes flight, hotel nights, and all activities per spec."""
        # flight=85, hotel=120*2=240, activities=25+35=60 → 385
        assert calculate_total(sample_package_no_transport) == 385.0

    def test_adds_transport_when_present(self, sample_package_with_transport):
        """FR-7: transport price is added when not None per spec."""
        # 385 + transport=30 → 415
        assert calculate_total(sample_package_with_transport) == 415.0

    def test_excludes_transport_when_none(self, sample_package_no_transport):
        """FR-7: transport is not counted when None per spec."""
        assert calculate_total(sample_package_no_transport) == 385.0

    def test_hotel_multiplied_by_nights(self, sample_flight, sample_hotel):
        """FR-7: hotel cost is price_per_night multiplied by nights per spec."""
        pkg = TourPackage(
            flight=sample_flight,
            hotel=sample_hotel,
            activities=[],
            budget=1000.0,
        )
        # flight=85, hotel=120*2=240, activities=0
        assert calculate_total(pkg) == 325.0

    def test_multiple_activities_summed(self, sample_package_no_transport):
        """FR-7: all activity prices are summed per spec."""
        # activities: 25 + 35 = 60
        total = calculate_total(sample_package_no_transport)
        assert total == 385.0  # 85 + 240 + 60

    def test_rounds_to_two_decimal_places(self, sample_flight, sample_hotel):
        """FR-7: total is rounded to 2 decimal places per spec."""
        pkg = TourPackage(
            flight=sample_flight,
            hotel=sample_hotel,
            activities=[PackageActivity(name="X", price=0.001, duration_hours=1.0)],
            budget=1000.0,
        )
        total = calculate_total(pkg)
        assert total == round(total, 2)

    def test_zero_activities(self, sample_flight, sample_hotel):
        """FR-7: package with no activities calculates correctly per spec."""
        pkg = TourPackage(
            flight=sample_flight,
            hotel=sample_hotel,
            activities=[],
            budget=1000.0,
        )
        assert calculate_total(pkg) == 325.0  # 85 + 240


# ---------------------------------------------------------------------------
# TestFormatPackage
# ---------------------------------------------------------------------------


class TestFormatPackage:
    def test_contains_flight_section(self, sample_package_no_transport):
        """FR-7: output contains flight emoji and header per spec."""
        output = format_package(sample_package_no_transport)
        assert "✈️" in output
        assert "*Flight*" in output

    def test_contains_hotel_section(self, sample_package_no_transport):
        """FR-7: output contains hotel emoji and header per spec."""
        output = format_package(sample_package_no_transport)
        assert "🏨" in output
        assert "*Hotel*" in output

    def test_contains_activities_section(self, sample_package_no_transport):
        """FR-7: output contains activities emoji and header per spec."""
        output = format_package(sample_package_no_transport)
        assert "🎯" in output
        assert "*Activities*" in output

    def test_transport_section_included_when_present(self, sample_package_with_transport):
        """FR-7: transport section appears when transport is not None per spec."""
        output = format_package(sample_package_with_transport)
        assert "🚗" in output
        assert "*Transport*" in output

    def test_transport_section_omitted_when_none(self, sample_package_no_transport):
        """FR-7: entire transport block omitted when transport is None per spec."""
        output = format_package(sample_package_no_transport)
        assert "🚗" not in output
        assert "Transport" not in output

    def test_contains_total_line(self, sample_package_no_transport):
        """FR-7: output contains total estimate line per spec."""
        output = format_package(sample_package_no_transport)
        assert "Total Estimate" in output

    def test_contains_budget_remaining_line(self, sample_package_no_transport):
        """FR-7: output contains budget remaining line per spec."""
        output = format_package(sample_package_no_transport)
        assert "Budget remaining" in output

    def test_budget_remaining_negative_when_over_budget(
        self, sample_flight, sample_hotel, sample_activities
    ):
        """FR-7: budget remaining shown as negative when over budget per spec."""
        pkg = TourPackage(
            flight=sample_flight,
            hotel=sample_hotel,
            activities=sample_activities,
            budget=100.0,  # much less than 385 total
        )
        output = format_package(pkg)
        assert "$-" in output

    def test_activities_are_numbered(self, sample_package_no_transport):
        """FR-7: activities start with 1. 2. numbering per spec."""
        output = format_package(sample_package_no_transport)
        assert "1." in output
        assert "2." in output

    def test_duration_whole_number_no_decimal(self, sample_package_no_transport):
        """FR-7: whole hour duration shows as integer not float per spec."""
        # sample_activities has duration_hours=3.0 and 2.0
        output = format_package(sample_package_no_transport)
        assert "3hrs" in output
        assert "3.0hrs" not in output

    def test_duration_decimal_shown_as_decimal(self, sample_flight, sample_hotel):
        """FR-7: fractional hour duration shows decimal per spec."""
        pkg = TourPackage(
            flight=sample_flight,
            hotel=sample_hotel,
            activities=[PackageActivity(name="Dive", price=50.0, duration_hours=1.5)],
            budget=1000.0,
        )
        output = format_package(pkg)
        assert "1.5hrs" in output

    def test_uses_telegram_bold_for_headers(self, sample_package_no_transport):
        """FR-7: section headers wrapped in asterisks for Telegram bold per spec."""
        output = format_package(sample_package_no_transport)
        assert "*Flight*" in output
        assert "*Hotel*" in output
        assert "*Activities*" in output

    def test_budget_remaining_uses_italic(self, sample_package_no_transport):
        """FR-7: budget remaining line wrapped in underscores for Telegram italic per spec."""
        output = format_package(sample_package_no_transport)
        assert "_(Budget remaining:" in output


# ---------------------------------------------------------------------------
# TestFormatTweakInvitation
# ---------------------------------------------------------------------------


class TestFormatTweakInvitation:
    def test_returns_string(self):
        """FR-7: format_tweak_invitation returns a string per spec."""
        result = format_tweak_invitation()
        assert isinstance(result, str)

    def test_contains_flight_option(self):
        """FR-7: tweak invitation mentions flight option per spec."""
        result = format_tweak_invitation()
        assert "flight" in result.lower()

    def test_contains_hotel_option(self):
        """FR-7: tweak invitation mentions hotel option per spec."""
        result = format_tweak_invitation()
        assert "hotel" in result.lower()

    def test_contains_activities_option(self):
        """FR-7: tweak invitation mentions activities option per spec."""
        result = format_tweak_invitation()
        assert "activit" in result.lower()

    def test_contains_transport_option(self):
        """FR-7: tweak invitation mentions transport option per spec."""
        result = format_tweak_invitation()
        assert "transport" in result.lower()

"""TB-24: Server activities API tests."""

import pytest
from sqlmodel import Session, select

from models.activity import Activity
from tests.conftest import test_engine


@pytest.fixture
def sample_activity():
    with Session(test_engine) as session:
        activity = Activity(
            name="Gardens by the Bay Tour",
            city="Singapore",
            description="Beautiful nature tour",
            duration_hours=3.0,
            price=25.0,
            category="nature",
            availability="daily",
        )
        session.add(activity)
        session.commit()
        session.refresh(activity)
        activity_id = activity.id
    with Session(test_engine) as session:
        return session.get(Activity, activity_id)


class TestSearchActivities:
    def test_returns_activities_list(self, client, sample_activity):
        """TB-24: GET /activities returns activities list."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filters_by_city(self, client, sample_activity):
        """TB-24: city param filters activities."""
        response = client.get("/activities?city=Singapore")
        assert response.status_code == 200
        data = response.json()
        assert all(a["city"] == "Singapore" for a in data)

    def test_filters_by_category(self, client, sample_activity):
        """TB-24: category param filters activities."""
        response = client.get("/activities?category=nature")
        assert response.status_code == 200
        data = response.json()
        assert all(a["category"] == "nature" for a in data)


class TestGetActivity:
    def test_returns_activity_by_id(self, client, sample_activity):
        """TB-24: GET /activities/{id} returns the correct activity."""
        response = client.get(f"/activities/{sample_activity.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_activity.id
        assert data["name"] == "Gardens by the Bay Tour"

    def test_returns_404_for_unknown_activity(self, client):
        """TB-24: unknown activity_id returns 404."""
        response = client.get("/activities/99999")
        assert response.status_code == 404

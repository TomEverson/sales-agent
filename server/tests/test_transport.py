"""TB-24: Server transport API tests."""

import pytest
from sqlmodel import Session, select

from models.transport import Transport
from tests.conftest import test_engine
from datetime import datetime


@pytest.fixture
def sample_transport():
    with Session(test_engine) as session:
        transport = Transport(
            type="car",
            origin="Singapore Airport",
            destination="Singapore City",
            departure_time=datetime(2026, 3, 28, 10, 0, 0),
            arrival_time=datetime(2026, 3, 28, 10, 45, 0),
            price=30.0,
            capacity=4,
        )
        session.add(transport)
        session.commit()
        session.refresh(transport)
        transport_id = transport.id
    with Session(test_engine) as session:
        return session.get(Transport, transport_id)


class TestSearchTransport:
    def test_returns_transport_list(self, client, sample_transport):
        """TB-24: GET /transport returns transport list."""
        response = client.get("/transport")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filters_by_origin(self, client, sample_transport):
        """TB-24: origin param filters transport."""
        response = client.get("/transport?origin=Singapore Airport")
        assert response.status_code == 200
        data = response.json()
        assert all(t["origin"] == "Singapore Airport" for t in data)

    def test_filters_by_destination(self, client, sample_transport):
        """TB-24: destination param filters transport."""
        response = client.get("/transport?destination=Singapore City")
        assert response.status_code == 200
        data = response.json()
        assert all(t["destination"] == "Singapore City" for t in data)

    def test_filters_by_type(self, client, sample_transport):
        """TB-24: type param filters transport."""
        response = client.get("/transport?type=car")
        assert response.status_code == 200
        data = response.json()
        assert all(t["type"] == "car" for t in data)


class TestGetTransport:
    def test_returns_transport_by_id(self, client, sample_transport):
        """TB-24: GET /transport/{id} returns the correct transport."""
        response = client.get(f"/transport/{sample_transport.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_transport.id
        assert data["type"] == "car"

    def test_returns_404_for_unknown_transport(self, client):
        """TB-24: unknown transport_id returns 404."""
        response = client.get("/transport/99999")
        assert response.status_code == 404

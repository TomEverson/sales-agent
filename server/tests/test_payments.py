"""TB-33: Payment API tests."""


class TestCreatePayment:
    def test_creates_pending_payment(self, client):
        """TB-33: POST /payments creates a pending payment."""
        response = client.post("/payments", json={"amount": 150.0})
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 150.0
        assert data["status"] == "pending"
        assert data["payment_method"] == "qr"
        assert "booking_reference" in data
        assert data["booking_reference"].startswith("PAY-")


class TestGetPayment:
    def test_returns_payment_by_reference(self, client):
        """TB-33: GET /payments/{ref} returns payment status."""
        create_response = client.post("/payments", json={"amount": 200.0})
        ref = create_response.json()["booking_reference"]

        response = client.get(f"/payments/{ref}")
        assert response.status_code == 200
        data = response.json()
        assert data["booking_reference"] == ref
        assert data["amount"] == 200.0

    def test_returns_404_for_unknown_reference(self, client):
        """TB-33: unknown booking_reference returns 404."""
        response = client.get("/payments/PAY-INVALID123")
        assert response.status_code == 404


class TestConfirmPayment:
    def test_marks_payment_as_paid(self, client):
        """TB-33: PUT /payments/{ref}/confirm marks payment as paid."""
        create_response = client.post("/payments", json={"amount": 100.0})
        ref = create_response.json()["booking_reference"]

        response = client.put(f"/payments/{ref}/confirm")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
        assert data["paid_at"] is not None

    def test_cannot_confirm_already_paid(self, client):
        """TB-33: confirming already paid payment returns error."""
        create_response = client.post("/payments", json={"amount": 50.0})
        ref = create_response.json()["booking_reference"]

        client.put(f"/payments/{ref}/confirm")
        response = client.put(f"/payments/{ref}/confirm")
        assert response.status_code == 400

    def test_returns_404_for_unknown_payment(self, client):
        """TB-33: confirming unknown payment returns 404."""
        response = client.put("/payments/PAY-INVALID123/confirm")
        assert response.status_code == 404

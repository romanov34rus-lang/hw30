from datetime import UTC, datetime, timedelta

import pytest
from parking_app import create_app
from parking_app import db as _db
from parking_app.models import Client, ClientParking, Parking


@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    with app.app_context():
        _db.create_all()

        client = Client(
            name="Иван",
            surname="Иванов",
            credit_card="1234-5678-9012-3456",
            car_number="A123BC",
        )
        parking = Parking(
            address="ул. Ленина, 10",
            opened=True,
            count_places=10,
            count_available_places=10,
        )
        _db.session.add_all([client, parking])
        _db.session.commit()

        log_entry = ClientParking(
            client_id=client.id,
            parking_id=parking.id,
            time_in=datetime.now(UTC) - timedelta(hours=2),
            time_out=datetime.now(UTC) - timedelta(hours=1),
        )
        _db.session.add(log_entry)
        _db.session.commit()

        yield app

        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db

from datetime import UTC, datetime, timedelta
from typing import Any, Generator, Tuple

import pytest
from parking_app import create_app
from parking_app import db as _db


@pytest.fixture(scope="session")
def app() -> Any:
    app = create_app(testing=True)
    with app.app_context():
        from parking_app.models import Client, ClientParking, Parking

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


@pytest.fixture(scope="session")
def db(app: Any) -> Generator[Any, None, None]:
    with app.app_context():
        yield _db


@pytest.fixture
def client(app: Any) -> Any:
    return app.test_client()


@pytest.fixture(scope="session")
def models() -> Tuple[Any, Any, Any]:
    from parking_app.models import Client, ClientParking, Parking

    return Client, ClientParking, Parking


@pytest.fixture(scope="module")
def factories(db: Any, models: Tuple[Any, Any, Any]) -> Tuple[Any, Any]:
    from tests.factories import BaseClientFactory, BaseParkingFactory

    Client, _, Parking = models

    class ClientFactory(BaseClientFactory):
        class Meta:
            model = Client
            sqlalchemy_session = db.session

    class ParkingFactory(BaseParkingFactory):
        class Meta:
            model = Parking
            sqlalchemy_session = db.session

    return ClientFactory, ParkingFactory

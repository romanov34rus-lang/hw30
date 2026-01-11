from datetime import UTC, datetime

import pytest
from parking_app.models import Client, ClientParking, Parking
from tests.factories import ClientFactory, ParkingFactory


@pytest.mark.parametrize("url", ["/clients", "/clients/1"])
def test_get_endpoints_return_200(client, url):
    response = client.get(url)
    assert response.status_code == 200


def test_create_client(client, db):
    new_client_data = {
        "name": "Петр",
        "surname": "Петров",
        "credit_card": "9876-5432-1098-7654",
        "car_number": "B456DE",
    }
    response = client.post("/clients", json=new_client_data)
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data

    # Проверяем, что клиент действительно создан
    created = db.session.get(Client, data["id"])
    assert created is not None
    assert created.name == "Петр"


def test_create_parking(client, db):
    parking_data = {"address": "ул. Гагарина, 5", "count_places": 5}
    response = client.post("/parkings", json=parking_data)
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data

    created = db.session.get(Parking, data["id"])
    assert created is not None
    assert created.count_available_places == 5


@pytest.mark.parking
def test_enter_parking(client, db):
    # Создадим нового клиента и парковку
    client_obj = Client(
        name="Анна",
        surname="Сидорова",
        credit_card="1111-2222-3333-4444",
        car_number="C789FG",
    )
    parking_obj = Parking(
        address="ул. Пушкина, 15",
        opened=True,
        count_places=1,
        count_available_places=1
    )
    db.session.add_all([client_obj, parking_obj])
    db.session.commit()

    # Заезд
    response = client.post(
        "/client_parkings",
        json={"client_id": client_obj.id, "parking_id": parking_obj.id},
    )
    assert response.status_code == 201

    # Проверяем, что место занято
    updated_parking = db.session.get(Parking, parking_obj.id)
    assert updated_parking.count_available_places == 0

    # Проверяем запись в лог
    log = (
        db.session.query(ClientParking)
        .filter_by(client_id=client_obj.id, parking_id=parking_obj.id)
        .first()
    )
    assert log is not None
    assert log.time_in is not None
    assert log.time_out is None


@pytest.mark.parking
def test_exit_parking(client, db):
    client_obj = Client(
        name="Елена",
        surname="Кузнецова",
        credit_card="5555-6666-7777-8888",
        car_number="D012HI",
    )
    parking_obj = Parking(
        address="ул. Чехова, 20",
        opened=True,
        count_places=1,
        count_available_places=0,  # занято!
    )
    db.session.add_all([client_obj, parking_obj])
    db.session.commit()

    log_entry = ClientParking(
        client_id=client_obj.id,
        parking_id=parking_obj.id,
        time_in=datetime.now(UTC)
    )
    db.session.add(log_entry)
    db.session.commit()

    # Выезд
    response = client.delete(
        "/client_parkings",
        json={"client_id": client_obj.id, "parking_id": parking_obj.id},
    )
    assert response.status_code == 200

    # Проверки
    updated_parking = db.session.get(Parking, parking_obj.id)
    assert updated_parking.count_available_places == 1

    updated_log = db.session.get(ClientParking, log_entry.id)
    assert updated_log.time_out is not None
    assert updated_log.time_out >= updated_log.time_in

    # Проверяем, что карта была обязательна
    no_card_client = Client(
        name="Без", surname="Карты", credit_card=None, car_number="X999XX"
    )
    db.session.add(no_card_client)
    db.session.commit()

    parking2 = Parking(
        address="Test", opened=True, count_places=1, count_available_places=1
    )
    db.session.add(parking2)
    db.session.commit()

    client.post(
        "/client_parkings",
        json={"client_id": no_card_client.id, "parking_id": parking2.id},
    )

    resp = client.delete(
        "/client_parkings",
        json={"client_id": no_card_client.id, "parking_id": parking2.id},
    )
    assert resp.status_code == 400
    assert "credit card" in resp.get_json()["error"].lower()


def test_enter_closed_parking(client, db):
    client_obj = Client(
        name="Test", surname="User", credit_card="1234", car_number="T123ST"
    )
    parking_obj = Parking(
        address="Closed lot",
        opened=False,
        count_places=1,
        count_available_places=1
    )
    db.session.add_all([client_obj, parking_obj])
    db.session.commit()

    resp = client.post(
        "/client_parkings",
        json={"client_id": client_obj.id, "parking_id": parking_obj.id},
    )
    assert resp.status_code == 400
    assert "closed" in resp.get_json()["error"]


def test_enter_full_parking(client, db):
    client_obj = Client(
        name="Full", surname="User", credit_card="5678", car_number="F456LL"
    )
    parking_obj = Parking(
        address="Full lot",
        opened=True,
        count_places=1,
        count_available_places=0
    )
    db.session.add_all([client_obj, parking_obj])
    db.session.commit()

    resp = client.post(
        "/client_parkings",
        json={"client_id": client_obj.id, "parking_id": parking_obj.id},
    )
    assert resp.status_code == 400
    assert "available places" in resp.get_json()["error"]


def test_factory_create_client(client, db):
    fake_client = ClientFactory.build()

    client_data = {
        "name": fake_client.name,
        "surname": fake_client.surname,
        "credit_card": fake_client.credit_card,
        "car_number": fake_client.car_number,
    }

    response = client.post("/clients", json=client_data)
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data

    # Проверяем, что запись создана
    created = db.session.get(Client, data["id"])
    assert created is not None
    assert created.name == fake_client.name


def test_factory_create_parking(client, db):
    fake_parking = ParkingFactory.build()

    parking_data = {
        "address": fake_parking.address,
        "count_places": fake_parking.count_places,
        "opened": fake_parking.opened,
    }

    response = client.post("/parkings", json=parking_data)
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data

    created = db.session.get(Parking, data["id"])
    assert created is not None
    assert created.count_places == fake_parking.count_places
    assert created.count_available_places == fake_parking.count_places

from datetime import UTC, datetime

from flask import Blueprint, jsonify, request

from . import db
from .models import Client, ClientParking, Parking

api = Blueprint("api", __name__)


@api.route("/clients", methods=["GET"])
def get_clients():
    clients = Client.query.all()
    return (
        jsonify(
            [
                {
                    "id": c.id,
                    "name": c.name,
                    "surname": c.surname,
                    "credit_card": c.credit_card,
                    "car_number": c.car_number,
                }
                for c in clients
            ]
        ),
        200,
    )


@api.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    client = db.session.get(Client, client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return (
        jsonify(
            {
                "id": client.id,
                "name": client.name,
                "surname": client.surname,
                "credit_card": client.credit_card,
                "car_number": client.car_number,
            }
        ),
        200,
    )


@api.route("/clients", methods=["POST"])
def create_client():
    data = request.get_json()
    required = ["name", "surname", "credit_card", "car_number"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    new_client = Client(
        name=data["name"],
        surname=data["surname"],
        credit_card=data["credit_card"],
        car_number=data["car_number"],
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"id": new_client.id}), 201


@api.route("/parkings", methods=["POST"])
def create_parking():
    data = request.get_json()
    required = ["address", "count_places"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    count_places = data["count_places"]
    if count_places <= 0:
        return jsonify({"error": "count_places must be positive"}), 400

    new_parking = Parking(
        address=data["address"],
        opened=data.get("opened", True),
        count_places=count_places,
        count_available_places=count_places,  # изначально все места свободны
    )
    db.session.add(new_parking)
    db.session.commit()
    return jsonify({"id": new_parking.id}), 201


@api.route("/client_parkings", methods=["POST"])
def enter_parking():
    data = request.get_json()
    client_id = data.get("client_id")
    parking_id = data.get("parking_id")

    if not client_id or not parking_id:
        return jsonify({"error": "client_id and parking_id are required"}), 400

    client = db.session.get(Client, client_id)
    parking = db.session.get(Parking, parking_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404
    if not parking:
        return jsonify({"error": "Parking not found"}), 404

    if not parking.opened:
        return jsonify({"error": "Parking is closed"}), 400

    if parking.count_available_places <= 0:
        return jsonify({"error": "No available places"}), 400

    # Проверяем, не находится ли клиент уже на этой парковке
    existing = ClientParking.query.filter_by(
        client_id=client_id, parking_id=parking_id, time_out=None
    ).first()
    if existing:
        return jsonify({"error": "Client is already parked here"}), 400

    # Уменьшаем количество свободных мест
    parking.count_available_places -= 1

    # Фиксируем заезд
    entry = ClientParking(
        client_id=client_id, parking_id=parking_id, time_in=datetime.now(UTC)
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Successfully entered parking"}), 201


@api.route("/client_parkings", methods=["DELETE"])
def exit_parking():
    data = request.get_json()
    client_id = data.get("client_id")
    parking_id = data.get("parking_id")

    if not client_id or not parking_id:
        return jsonify({"error": "client_id and parking_id are required"}), 400

    entry = ClientParking.query.filter_by(
        client_id=client_id, parking_id=parking_id, time_out=None
    ).first()

    if not entry:
        return jsonify({"error": "Active parking session not found"}), 404

    # Проверяем, что у клиента есть карта
    client = db.session.get(Client, client_id)
    if not client or not client.credit_card:
        return jsonify({"error": "Client has no credit card for payment"}), 400

    # Увеличиваем свободные места
    parking = db.session.get(Parking, parking_id)
    parking.count_available_places += 1

    # Фиксируем время выезда
    entry.time_out = datetime.now(UTC)
    db.session.commit()

    return jsonify({"message": "Successfully exited parking"}), 200

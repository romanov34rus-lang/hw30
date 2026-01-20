from datetime import UTC, datetime

from parking_app import db


class Client(db.Model):
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))

    def __repr__(self) -> str:
        return f"<Client {self.name} {self.surname}>"


class Parking(db.Model):
    __tablename__ = "parking"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Parking {self.address}>"


class ClientParking(db.Model):
    __tablename__ = "client_parking"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("client.id"), nullable=False
    )
    parking_id = db.Column(
        db.Integer, db.ForeignKey("parking.id"), nullable=False
    )
    time_in = db.Column(db.DateTime, default=datetime.now(UTC))
    time_out = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint(
            "client_id", "parking_id", name="unique_client_parking"
        ),
    )

    client = db.relationship("Client", backref="parking_logs")
    parking = db.relationship("Parking", backref="client_logs")

    def __repr__(self) -> str:
        return (
            f"<ClientParking client={self.client_id},"
            f"parking={self.parking_id}>"
        )

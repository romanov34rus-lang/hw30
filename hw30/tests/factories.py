import random
from typing import Any

from factory import Faker as FactoryFaker
from factory import Maybe, lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory
from parking_app import db
from parking_app.models import Client, Parking


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = FactoryFaker("first_name")
    surname = FactoryFaker("last_name")
    credit_card = Maybe(
        FactoryFaker("boolean"),
        yes_declaration=FactoryFaker("credit_card_number"),
        no_declaration=None,
    )
    car_number = FactoryFaker("bothify", text="???###", letters="ABEKMHOPCTYX")


class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    address = FactoryFaker("address")
    opened = FactoryFaker("boolean")
    count_places = FactoryFaker("random_int", min=1, max=100)

    @lazy_attribute
    def count_available_places(self) -> int:
        # self.count_places уже вычислен как int на момент вызова
        return random.randint(0, self.count_places)

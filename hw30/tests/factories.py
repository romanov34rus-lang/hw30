import random

from factory import Faker as FactoryFaker
from factory import Maybe, lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory


class BaseClientFactory(SQLAlchemyModelFactory):

    class Meta:
        abstract = True

    name = FactoryFaker("first_name")
    surname = FactoryFaker("last_name")
    credit_card = Maybe(
        FactoryFaker("boolean"),
        yes_declaration=FactoryFaker("credit_card_number"),
        no_declaration=None,
    )
    car_number = FactoryFaker("bothify", text="???###", letters="ABEKMHOPCTYX")


class BaseParkingFactory(SQLAlchemyModelFactory):

    class Meta:
        abstract = True

    address = FactoryFaker("address")
    opened = FactoryFaker("boolean")

    @lazy_attribute
    def count_places(self) -> int:
        return random.randint(1, 100)

    @lazy_attribute
    def count_available_places(self) -> int:
        return random.randint(0, self.count_places)

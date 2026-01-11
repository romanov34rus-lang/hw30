import factory
from faker import Faker
from parking_app import db
from parking_app.models import Client, Parking

fake = Faker()


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.Maybe(
        factory.Faker("boolean"),
        yes_declaration=factory.Faker("credit_card_number"),
        no_declaration=None,
    )
    car_number = factory.Faker(
        "bothify",
        text="???###",
        letters="ABEKMHOPCTYX"
    )


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    address = factory.Faker("address")
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int", min=1, max=100)

    @factory.lazy_attribute
    def count_available_places(self):
        return fake.random_int(min=0, max=self.count_places)

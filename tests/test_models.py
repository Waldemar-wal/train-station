from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Journey,
    Order,
    Ticket,
)

User = get_user_model()


class StationModelTest(TestCase):
    def test_create_station(self):
        station = Station.objects.create(
            name="Kyiv", latitude=50.45, longitude=30.52
        )
        self.assertEqual(str(station), "Kyiv")


class RouteModelTest(TestCase):
    def test_create_route(self):
        source = Station.objects.create(
            name="Lviv", latitude=49.84, longitude=24.03
        )
        destination = Station.objects.create(
            name="Odessa", latitude=46.48, longitude=30.73
        )
        route = Route.objects.create(
            source=source, destination=destination, distance=500
        )
        self.assertEqual(str(route), "Lviv-Odessa")


class TrainTypeModelTest(TestCase):
    def test_create_train_type(self):
        ttype = TrainType.objects.create(name="Cargo")
        self.assertEqual(str(ttype), "Cargo")


class TrainModelTest(TestCase):
    def test_create_train(self):
        ttype = TrainType.objects.create(name="Express")
        train = Train.objects.create(
            name="Skorost", cargo=10, seats_in_cargo=20, train_type=ttype
        )
        self.assertEqual(str(train), "Skorost")
        self.assertEqual(train.capacity, 200)


class CrewModelTest(TestCase):
    def test_create_crew(self):
        crew = Crew.objects.create(first_name="Ivan", last_name="Petrov")
        self.assertEqual(str(crew), "Ivan Petrov")
        self.assertEqual(crew.full_name, "Ivan Petrov")


class JourneyModelTest(TestCase):
    def test_create_journey(self):
        station_a = Station.objects.create(
            name="Dnipro", latitude=48.45, longitude=34.98
        )
        station_b = Station.objects.create(
            name="Kharkiv", latitude=49.99, longitude=36.23
        )
        route = Route.objects.create(
            source=station_a, destination=station_b, distance=400
        )
        ttype = TrainType.objects.create(name="Local")
        train = Train.objects.create(
            name="Fast", cargo=5, seats_in_cargo=10, train_type=ttype
        )
        journey = Journey.objects.create(
            route=route,
            train=train,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=4),
        )
        self.assertIn(str(route), str(journey))


class OrderModelTest(TestCase):
    def test_create_order(self):
        user = User.objects.create_user(username="user1", password="pass123")
        order = Order.objects.create(user=user)
        self.assertIn(str(order.created_at.date()), str(order))


class TicketModelTest(TestCase):
    def test_create_valid_ticket(self):
        station1 = Station.objects.create(name="A", latitude=1, longitude=1)
        station2 = Station.objects.create(name="B", latitude=2, longitude=2)
        route = Route.objects.create(
            source=station1, destination=station2, distance=300
        )
        train_type = TrainType.objects.create(name="TypeX")
        train = Train.objects.create(
            name="TrainX", cargo=3, seats_in_cargo=4, train_type=train_type
        )
        journey = Journey.objects.create(
            route=route,
            train=train,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
        )
        user = User.objects.create_user(username="user2", password="pass456")
        order = Order.objects.create(user=user)
        ticket = Ticket.objects.create(
            journey=journey, order=order, cargo=2, seat=3
        )
        self.assertIn("cargo: 2", str(ticket))

    def test_invalid_ticket_validation(self):
        station = Station.objects.create(name="C", latitude=3, longitude=3)
        route = Route.objects.create(
            source=station, destination=station, distance=100
        )
        ttype = TrainType.objects.create(name="Test")
        train = Train.objects.create(
            name="T", cargo=2, seats_in_cargo=2, train_type=ttype
        )
        journey = Journey.objects.create(
            route=route,
            train=train,
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
        )
        user = User.objects.create_user(username="user3", password="pass789")
        order = Order.objects.create(user=user)

        ticket = Ticket(journey=journey, order=order, cargo=5, seat=1)
        with self.assertRaises(ValidationError):
            ticket.full_clean()

from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
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


class StationViewSetTest(APITestCase):
    def setUp(self):
        self.station = Station.objects.create(
            name="Kyiv", latitude=50.45, longitude=30.52
        )

    def test_list_stations(self):
        url = reverse("station-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_station(self):
        url = reverse("station-detail", args=[self.station.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RouteViewSetTest(APITestCase):
    def setUp(self):
        self.a = Station.objects.create(name="A", latitude=1, longitude=1)
        self.b = Station.objects.create(name="B", latitude=2, longitude=2)
        self.route = Route.objects.create(
            source=self.a, destination=self.b, distance=200
        )

    def test_list_routes(self):
        url = reverse("route-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_route(self):
        url = reverse("route-detail", args=[self.route.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TrainTypeViewSetTest(APITestCase):
    def setUp(self):
        self.ttype = TrainType.objects.create(name="Express")

    def test_list_train_types(self):
        url = reverse("traintype-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_train_type(self):
        url = reverse("traintype-detail", args=[self.ttype.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TrainViewSetTest(APITestCase):
    def setUp(self):
        self.ttype = TrainType.objects.create(name="Cargo")
        self.train = Train.objects.create(
            name="C-100", cargo=5, seats_in_cargo=10, train_type=self.ttype
        )

    def test_list_trains(self):
        url = reverse("train-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_train(self):
        url = reverse("train-detail", args=[self.train.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class CrewViewSetTest(APITestCase):
    def setUp(self):
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")

    def test_list_crew(self):
        url = reverse("crew-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_crew(self):
        url = reverse("crew-detail", args=[self.crew.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class JourneyViewSetTest(APITestCase):
    def setUp(self):
        self.a = Station.objects.create(name="Start", latitude=0, longitude=0)
        self.b = Station.objects.create(name="End", latitude=1, longitude=1)
        self.route = Route.objects.create(
            source=self.a, destination=self.b, distance=100
        )
        self.ttype = TrainType.objects.create(name="Fast")
        self.train = Train.objects.create(
            name="F-1", cargo=2, seats_in_cargo=2, train_type=self.ttype
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=1),
        )

    def test_list_journeys(self):
        url = reverse("journey-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_journey(self):
        url = reverse("journey-detail", args=[self.journey.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class OrderViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="123"
        )
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(user=self.user)

    def test_list_orders(self):
        url = reverse("order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_order(self):
        url = reverse("order-detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TicketViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="123"
        )
        self.client.force_authenticate(user=self.user)

        self.station1 = Station.objects.create(
            name="One", latitude=1, longitude=1
        )
        self.station2 = Station.objects.create(
            name="Two", latitude=2, longitude=2
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=300
        )
        self.train_type = TrainType.objects.create(name="Local")
        self.train = Train.objects.create(
            name="L-Train",
            cargo=3,
            seats_in_cargo=3,
            train_type=self.train_type
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=1),
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            journey=self.journey, order=self.order, cargo=1, seat=1
        )

    def test_list_tickets(self):
        url = reverse("ticket-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_ticket(self):
        url = reverse("ticket-detail", args=[self.ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

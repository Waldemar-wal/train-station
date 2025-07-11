from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from station.models import (
    Station,
    Journey,
    Route,
    TrainType,
    Train,
    Crew,
    Order,
)
from station.permissions import IsAdminOrIfAuthenticatedReadOnly

from station.serializers import (
    TrainTypeSerializer,
    StationSerializer,
    CrewSerializer,
    TrainSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    OrderSerializer,
    OrderListSerializer,
    JourneyDetailSerializer,
    TrainListSerializer,
)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Train.objects.prefetch_related("train_type")
    serializer_class = TrainSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        return TrainSerializer


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.prefetch_related("source", "destination")
    serializer_class = RouteSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            source_id = self._params_to_ints(source)
            queryset = queryset.filter(source__id__in=source_id)

        if destination:
            destination_id = self._params_to_ints(destination)
            queryset = queryset.filter(destination__id__in=destination_id)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by source id (ex. ?source=2,5)",
            ),
            OpenApiParameter(
                "destination",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by destination id (ex. ?destination=2,5)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
         return super().list(request, *args, **kwargs)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.all()
        .select_related("route", "train").prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("train__cargo") * F("train__seats_in_cargo")
                - Count("tickets")
            )
        )
    )
    serializer_class = JourneySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        date = self.request.query_params.get("date")
        route_id_str = self.request.query_params.get("route")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if route_id_str:
            queryset = queryset.filter(route_id=int(route_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=OpenApiTypes.INT,
                description="Filter by route id (ex. ?route=2)",
            ),
            OpenApiParameter(
                "date",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by datetime of Journey "
                    "(ex. ?date=2022-10-23)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route",
        "tickets__journey__train",
        "tickets__journey__crew"
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


from django.urls import path, include
from rest_framework import routers

from station.views import (
    TrainTypeViewSet,
    TrainViewSet,
    StationViewSet,
    JourneyViewSet,
    RouteViewSet,
    CrewViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("train-type", TrainTypeViewSet)
router.register("station", StationViewSet)
router.register(
    "trains",
    TrainViewSet,
)
router.register("journey", JourneyViewSet)
router.register("route", RouteViewSet)
router.register("crew", CrewViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "station"

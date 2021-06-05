import requests
from django.db.models import Avg, Count
from django.http import Http404
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from .external_api import external_api_call
from .models import Car, Rate
from .serializers import CarSerializer, RateSerializer


class ListCarGenerics(generics.ListCreateAPIView):
    """Post and Get handle for /cars/ endpoint."""

    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def list(self, request: Request) -> Response:
        """Overridden list method.

            Uses custom queryset, serializer with additional fields and return data ordered by avg_rating value.
        Args:
            request (Request): Input data

        Returns:
            Response: Response with car object list.
        """
        queryset = Car.objects.annotate(avg_rating=Avg("rate__rating")).order_by("-avg_rating")
        serializer = CarSerializer(queryset, fields=("id", "make", "model", "avg_rating"), many=True)
        return Response(serializer.data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Overriden create method.

        Args:
            request (Request): Input data

        Returns:
            Response: Response data varies on validation and external api communication status.
        """
        serializer = CarSerializer(data=request.data, fields=("make", "model"))
        serializer.is_valid(raise_exception=True)

        car_make = serializer.validated_data.get("make", "")
        car_model = serializer.validated_data.get("model", "")

        try:
            # We don't need a data from external api, but external api call is designed to return received data
            external_api_call(request, car_model, car_make)
        # Both exceptions point to error on external api side. I've used general 500 code, but it could be changed
        # to be more specific (500 for the first exception, and 503 for the second one ?)
        except (requests.exceptions.RequestException, ConnectionError) as e:
            return Response(data={"external_api_error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AttributeError as e:
            return Response(data={"external_api_error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response(data={"external_api_error": f"{e}"}, status=status.HTTP_404_NOT_FOUND)

        self.perform_create(serializer)
        return Response(serializer.data)


class DetailCarGenerics(generics.DestroyAPIView):
    """Delete handle for /cars/<pk>/ endpoint."""

    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Overriden destroy method.

            Adds custom response data
        Args:
            request (Request): Input data

        Returns:
            Response: Response data varies on destroy method status.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            return Response(data={"validation_error": "Record doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data={"message": "Record deleted"}, status=status.HTTP_204_NO_CONTENT)


class PopularCarGenerics(generics.ListAPIView):
    """Get handle for /popular/ endpoint."""

    queryset = Car.objects.annotate(rates_number=Count("rate")).order_by("-rates_number")
    serializer_class = CarSerializer

    def list(self, request: Request) -> Response:
        """Overridden list method.

            Uses serializer with additional field and return data ordered by rate number.
        Args:
            request (Request): Input data

        Returns:
            Response: Response with car object list, ordered by avg_rating
        """
        queryset = self.get_queryset()
        serializer = CarSerializer(queryset, fields=("id", "make", "model", "rates_number"), many=True)
        return Response(serializer.data)


class CreateRateGenerics(generics.CreateAPIView):
    """Post handle for /rate/ endpoint."""

    queryset = Rate.objects.all()
    serializer_class = RateSerializer

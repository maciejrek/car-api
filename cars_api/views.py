from rest_framework import generics
from django.http import Http404
from .models import Car, Rate
from .serializers import CarSerializer, RateSerializer
from .external_api import external_api_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Count, Avg


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

        car_make = serializer.validated_data.get("make")
        car_model = serializer.validated_data.get("model")

        if external_api_view(request, car_model, car_make):
            self.perform_create(serializer)
            return Response(serializer.data)
        else:
            return Response(
                data={
                    "external_api_error": f"No matching result in external api for {car_make} {car_model}, or API unavailable."
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class DetailCarGenerics(generics.DestroyAPIView):
    """Delete handle for /cars/<pk> endpoint."""

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
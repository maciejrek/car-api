from rest_framework import generics
from django.http import Http404
from .models import Car, Rate
from .serializers import CarSerializer, RateSerializer
from .external_api import external_api_view
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Count, Avg


class ListCarGenerics(generics.ListCreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def list(self, request):
        queryset = Car.objects.annotate(avg_rating=Avg("rate__rating")).order_by("-avg_rating")
        serializer = CarSerializer(queryset, fields=("make", "model", "avg_rating"), many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CarSerializer(data=request.data, fields=("make", "model"))
        if not serializer.is_valid():
            return Response(data={"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        car_make = serializer.validated_data.get("make")
        car_model = serializer.validated_data.get("model")

        if external_api_view(request, car_model, car_make):
            self.perform_create(serializer)
            return Response(serializer.data)
        else:
            return Response(
                data={"message": f"No matching result in external api for {car_make} {car_model}, or API unavailable."},
                status=status.HTTP_404_NOT_FOUND,
            )


class DetailCarGenerics(generics.DestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            return Response(data={"message": "Record doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data={"message": "Record deleted"}, status=status.HTTP_204_NO_CONTENT)


class PopularCarGenerics(generics.ListAPIView):
    queryset = Car.objects.annotate(rates_number=Count("rate")).order_by("-rates_number")
    serializer_class = CarSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CarSerializer(queryset, fields=("make", "model", "rates_number"), many=True)
        return Response(serializer.data)


class CreateRateGenerics(generics.CreateAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(data={"message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data)

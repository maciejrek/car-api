import requests
from django.db.models import Avg, Count
from django.http import Http404
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from .external_api import external_api_call
from .models import Game, GameRate
from .serializers import GameSerializer, GameRateSerializer


class ListGameGenerics(generics.ListCreateAPIView):
    """Post and Get handle for /games/ endpoint."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def list(self, request: Request) -> Response:
        """Overridden list method.

            Uses custom queryset, serializer with additional fields and return data ordered by avg_rating value.
        Args:
            request (Request): Input data

        Returns:
            Response: Response with game object list.
        """
        queryset = Game.objects.annotate(avg_rating=Avg("gamerate__rating")).order_by("-avg_rating")
        serializer = GameSerializer(queryset, fields=("id", "platform", "name", "avg_rating"), many=True)
        return Response(serializer.data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Overriden create method.

        Args:
            request (Request): Input data

        Returns:
            Response: Response data varies on validation and external api communication status.
        """
        serializer = GameSerializer(data=request.data, fields=("platform", "name"))
        serializer.is_valid(raise_exception=True)

        game_platform = serializer.validated_data.get("platform", "")
        game_name = serializer.validated_data.get("name", "")

        try:
            # We don't need a data from external api, but external api call is designed to return received data
            external_api_call(request, game_platform, game_name)
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


class DestroyGameGenerics(generics.DestroyAPIView):
    """Delete handle for /games/<pk>/ endpoint."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer

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
        return Response(data={"message": "Record deleted"}, status=status.HTTP_200_OK)


class PopularGameGenerics(generics.ListAPIView):
    """Get handle for /games_popular/ endpoint."""

    queryset = Game.objects.annotate(rates_number=Count("gamerate")).order_by("-rates_number")
    serializer_class = GameSerializer

    def list(self, request: Request) -> Response:
        """Overridden list method.

            Uses serializer with additional field and return data ordered by rate number.
        Args:
            request (Request): Input data

        Returns:
            Response: Response with game object list, ordered by avg_rating
        """
        queryset = self.get_queryset()
        serializer = GameSerializer(queryset, fields=("id", "platform", "name", "rates_number"), many=True)
        return Response(serializer.data)


class CreateGameRateGenerics(generics.CreateAPIView):
    """Post handle for /games_rate/ endpoint."""

    queryset = GameRate.objects.all()
    serializer_class = GameRateSerializer

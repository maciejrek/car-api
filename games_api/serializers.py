from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Game, GameRate


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that controls which fields should be displayed.

    Taken from: https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
    It gives us possibility to use serializer with dynamic field
    """

    def __init__(self, *args, **kwargs):
        """Init method."""
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class GameSerializer(DynamicFieldsModelSerializer):
    """Serializer for Game model."""

    rates_number = serializers.IntegerField()
    avg_rating = serializers.FloatField()

    class Meta:
        """Meta class of GameSerializer.

        Specify model and fields to serialize.
        """

        model = Game
        fields = ["id", "platform", "name", "rates_number", "avg_rating"]
        validators = [UniqueTogetherValidator(queryset=Game.objects.all(), fields=["platform", "name"])]


class GameRateSerializer(serializers.ModelSerializer):
    """Serializer for GameRate model."""

    class Meta:
        """Meta class of GameRateSerializer.

        Specify model and fields to serialize, adds custom error messages.
        Error messages are changed to hide record details (<pk> for game id), and make message clean for value errors.
        """

        model = GameRate
        fields = ["game_id", "rating"]
        extra_kwargs = {
            "rating": {
                "error_messages": {
                    "max_value": "Rating has to be between 1 and 5.",
                    "min_value": "Rating has to be between 1 and 5.",
                }
            },
            "game_id": {"error_messages": {"does_not_exist": "Game record does not exist."}},
        }

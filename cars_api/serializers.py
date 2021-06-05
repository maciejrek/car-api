from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Car, Rate


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that controls which fields should be displayed.

    Taken from: https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
    It gives us possibility to use serializer with dynamic field (usefull for car model)
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


class CarSerializer(DynamicFieldsModelSerializer):
    """Serializer for Car model."""

    rates_number = serializers.IntegerField()
    avg_rating = serializers.FloatField()

    class Meta:
        """Meta class of CarSerializer.

        Specify model and fields to serialize.
        """

        model = Car
        fields = ["id", "make", "model", "rates_number", "avg_rating"]
        validators = [UniqueTogetherValidator(queryset=Car.objects.all(), fields=["make", "model"])]


class RateSerializer(serializers.ModelSerializer):
    """Serializer for Rate model."""

    class Meta:
        """Meta class of RateSerializer.

        Specify model and fields to serialize, adds custom error messages.
        Error messages are changed to hide record details (<pk> for car id), and make message clean for value errors.
        """

        model = Rate
        fields = ["car_id", "rating"]
        extra_kwargs = {
            "rating": {
                "error_messages": {
                    "max_value": "Rating has to be between 1 and 5.",
                    "min_value": "Rating has to be between 1 and 5.",
                }
            },
            "car_id": {"error_messages": {"does_not_exist": "Car record does not exist."}},
        }

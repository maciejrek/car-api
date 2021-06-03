from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Car, Rate


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that controls which fields should be displayed.

    Taken from: https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
    """

    def __init__(self, *args, **kwargs):
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
    rates_number = serializers.IntegerField()
    avg_rating = serializers.IntegerField()

    class Meta:
        model = Car
        fields = ["make", "model", "rates_number", "avg_rating"]
        validators = [UniqueTogetherValidator(queryset=Car.objects.all(), fields=["make", "model"])]


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ["car_id", "rating"]

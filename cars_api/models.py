from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from typing import Dict, Any


class TitleCharField(models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        """Init method of custom field class."""
        super(TitleCharField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value: str) -> str:
        """Aux method, to keep every string saved in field in 'title' format.

        Args:
            value (str): Input field data

        Returns:
            str: Formatted output data (capital letter for each word in string).
        """
        return str(value).title()


class Car(models.Model):
    make = TitleCharField(max_length=50)
    model = TitleCharField(max_length=50)

    def __str__(self) -> str:
        """Overridden method, with custom string representation.

        Returns:
            str: Formatted output data
        """
        return f"{self.model} {self.make}"

    def to_dict(self) -> Dict[str, str]:
        """Aux method, used to represent object data as dict.

        Returns:
            dict: Object data represented as dict.
        """
        return {"make": self.make, "model": self.model}


class Rate(models.Model):
    car_id = models.ForeignKey(Car, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self) -> str:
        """Overridden method, with custom string representation.

        Returns:
            str: Formatted output data
        """
        return f"{self.car_id}: {self.rating}"

    def to_dict(self) -> Dict[str, Any]:
        """Aux method, used to represent object data as dict.

        Returns:
            dict: Object data represented as dict.
        """
        return {"car": self.car_id.to_dict(), "rate": self.rating}

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class TitleCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(TitleCharField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).title()


class Car(models.Model):
    make = TitleCharField(max_length=50)
    model = TitleCharField(max_length=50)

    def __str__(self):
        return f"{self.make} {self.model}"

    def to_dict(self):
        return {"make": self.make, "model": self.model}


class Rate(models.Model):
    car_id = models.ForeignKey(Car, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.car_id}: {self.rating}"

    def to_dict(self):
        return {"car": self.car_id.to_dict(), "rate": self.rating}

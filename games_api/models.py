from typing import Any, Dict

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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


class Game(models.Model):
    platform = TitleCharField(max_length=50)
    name = TitleCharField(max_length=50)

    def __str__(self) -> str:
        """Overridden method, with custom string representation.

        Returns:
            str: Formatted output data
        """
        return f"{self.platform} {self.name}"

    def to_dict(self) -> Dict[str, str]:
        """Aux method, used to represent object data as dict.

        Returns:
            dict: Object data represented as dict.
        """
        return {"platform": self.platform, "name": self.name}


class GameRate(models.Model):
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self) -> str:
        """Overridden method, with custom string representation.

        Returns:
            str: Formatted output data
        """
        return f"{self.game_id}: {self.rating}"

    def to_dict(self) -> Dict[str, Any]:
        """Aux method, used to represent object data as dict.

        Returns:
            dict: Object data represented as dict.
        """
        return {"car": self.game_id.to_dict(), "rate": self.rating}

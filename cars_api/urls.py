from django.urls import path

from .views import (CreateRateGenerics, DetailCarGenerics, ListCarGenerics,
                    PopularCarGenerics)

urlpatterns = [
    path("cars/", ListCarGenerics.as_view()),
    path("cars/<int:pk>/", DetailCarGenerics.as_view()),
    path("rate/", CreateRateGenerics.as_view()),
    path("popular/", PopularCarGenerics.as_view()),
]

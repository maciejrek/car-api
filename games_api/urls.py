from django.urls import path

from .views import CreateGameRateGenerics, DestroyGameGenerics, ListGameGenerics, PopularGameGenerics

urlpatterns = [
    path("games/", ListGameGenerics.as_view()),
    path("games/<int:pk>/", DestroyGameGenerics.as_view()),
    path("games_rate/", CreateGameRateGenerics.as_view()),
    path("games_popular/", PopularGameGenerics.as_view()),
]

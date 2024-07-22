from django.urls import path

from .views import (
    HomeListView,
    HomeDetailView,
    HomeCreateView,
    WaterCheckerCreateView,
    WaterCheckerDetailView
)


urlpatterns = [
    path('homes/', HomeListView.as_view(), name='home-list'),
    path('homes/details/',
         HomeDetailView.as_view(),
         name='home-detail'
         ),
    path('homes/create/',
         HomeCreateView.as_view(),
         name='home-create'
         ),
    path('water-checkers/create',
         WaterCheckerCreateView.as_view(),
         name='water-checkers-create'
         ),
    path('water-checkers/details/',
         WaterCheckerDetailView.as_view(),
         name='water-checkers-details'
         ),
]

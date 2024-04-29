from django.urls import path
from .views import *

urlpatterns = [
    path('addpositions/', AddPosition.as_view(), name="addposition"),
]
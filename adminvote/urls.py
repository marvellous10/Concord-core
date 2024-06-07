from django.urls import path
from .views import *

urlpatterns = [
    path('addpositions/', AddPosition.as_view(), name="addposition"),
    path('overview/', Overview.as_view(), name="overview"),
    path('test/', TestDB.as_view(), name="testdb"),
    path('changesessionstatus/', ChangeSessionStatus.as_view(), name="changesessionstatus"),
]
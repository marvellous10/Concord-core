from django.urls import path
from .views import *


urlpatterns = [
    path('vote/', CandidateVote.as_view(), name='vote'),
]
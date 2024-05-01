from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminvote/', include('adminvote.urls')),
    path('candidatevote/', include('candidatevote.urls')),
]

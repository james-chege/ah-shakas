from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProfileAPIView

app_name = "profiles"

urlpatterns = [
    path('profiles/<username>/', ProfileAPIView.as_view(), name='user-profile')
]

urlpatterns = format_suffix_patterns(urlpatterns)
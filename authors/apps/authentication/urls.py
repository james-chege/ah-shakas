from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, VerifyAPIView, SocialSignUp
)

# Specify a namespace
app_name="authentication"

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(), name='user-registration'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path('verify/<str:token>', VerifyAPIView.as_view(), name='verify'),
    path('users/login/', LoginAPIView.as_view()),
    path('social_auth/', SocialSignUp.as_view(), name="social_sign_up"),
]

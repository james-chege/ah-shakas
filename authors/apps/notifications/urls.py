from django.urls import path
from .views import NotificationAPIView, SubscribeAPIView, UnSubscribeAPIView, IsSubscribedAPIView

app_name = 'notifications'

urlpatterns = [
    path('notifications/', NotificationAPIView.as_view(), name='notification'),
    path('notifications/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
    path('notifications/unsubscribe/', UnSubscribeAPIView.as_view(), name='unsubscribe'),
    path('notifications/is-subscribed/', IsSubscribedAPIView.as_view(), name='is_subscribed'),
]
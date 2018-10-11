from rest_framework import status
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from .models import Profile

# Create your views here.

class ProfileAPIView(APIView):
    #Allow any user to hit this endpoint
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ProfileJSONRenderer,)

    def get(self, request, username, format=None):
        try:
            profile =  Profile.objects.get(user__username=username)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {
                    'message': 'Profile not found'
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, request, username, format=None):
        try:
            serializer_data = request.data.get('user', {})
            serializer = ProfileSerializer(request.user.profile, data=serializer_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(
                    {
                        'message': 'Profile not found'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

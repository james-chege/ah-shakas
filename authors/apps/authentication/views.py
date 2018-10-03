from rest_framework import status, generics
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response



from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)

from .token import generate_token
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import jwt
from .models import User


class RegistrationAPIView(CreateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {} )

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        user_email = user['email']
        user_name = user['username']
        token = generate_token(user_name)
        current_domain = settings.DEFAULT_DOMAIN

        # send email to the user for verification
        url = current_domain + "/api/verify/" + str(token)
        send_mail(
                    'Verify your email',
                    'You will need to confirm your email to start using Author heaven - A Social platform for the creative at heart.' + url,
                    'chegemaimuna@gmail.com',
                    [user_email],
                    fail_silently=False,
                )
        return_message = {"Message":"Thank you for registering at Authors heaven. To start using authors heaven, go to your email and click the confirmation link which we haves sent to you :D"}
        serializer.save()
        return Response(return_message, status=status.HTTP_201_CREATED)

class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class VerifyAPIView(APIView):
    """
    A class to verify user using the token sent to the email
    """
    permission_classes = (AllowAny,)
    def get(self, request, token):
        username = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        user_in_db = User.objects.get(username = username['username'])
        try:
            user_in_db.is_active = True
            user_in_db.save()
            return Response(data = {"Message": "Congratulations! You have successfully activated your account."}, 
                            status=status.HTTP_200_OK)
        except:
            return Response(data={"Message": "Invalid link"},
                status=status.HTTP_400_BAD_REQUEST)
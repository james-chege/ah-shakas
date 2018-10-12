from rest_framework import status, generics
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response



from social_django.utils import load_backend, load_strategy
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import AuthAlreadyAssociated, MissingBackend

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, SocialSignUpSerializer
)

class RegistrationAPIView(CreateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class SocialSignUp(CreateAPIView):
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialSignUpSerializer
    #allow everyone to view without having to be authenticated
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        Override `create` instead of `perform_create` to access request
        request is necessary for `load_strategy`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.data['provider']

        # If this request was made with an authenticated user, try to associate this social 
        # account with it
        authed_user = request.user if not request.user.is_anonymous else None
        strategy = load_strategy(request)
        #Get the backend that is associated with the user provider i.e google,twitter and facebook
        backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)


        if isinstance(backend, BaseOAuth1):
           #cater for services that use OAuth1, an example is twitter
            token = {
                'oauth_token': serializer.data['access_token'],
                'oauth_token_secret': request.data['access_token_secret'],
            }
            
        elif isinstance(backend, BaseOAuth2):
            #we just need to pass access_token for OAuth2
            token = serializer.data['access_token']
            

        try:
            #check if the user exists, if exists,we just login but if not it creates a new user
            user = backend.do_auth(token, user=authed_user)
        except AuthAlreadyAssociated:
            # if the user already exists,throw the following error
            return Response({"error": "The email is already registered, please try another one"},
                            status=status.HTTP_400_BAD_REQUEST)

        if user and user.is_active:
            serializer = UserSerializer(user)
            # if the access token was set to an empty string, then save the access token 
            # from the request
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                # Facebook for example will return the access_token in its response to you. 
                auth_created.extra_data['access_token'] = token
                auth_created.save()
                serializer.save()

            
            serializer.instance = user
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, 
                            headers=headers)
        else:
            return Response({"error": "Something went wrong with the authentication, please try again"},
                                        status=status.HTTP_400_BAD_REQUEST)

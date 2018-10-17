from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse as API_Reverse
from django.core import mail
from django.urls import reverse

from authors.apps.authentication.models import User
from authors.apps.authentication.token import generate_token


class BaseTest(APITestCase):
    """This class provides a base for other tests"""

    def setUp(self):
        self.url = API_Reverse('articles:articles')
        self.client = APIClient()
        self.unauthorised_client = APIClient()
        self.signup_url = API_Reverse('authentication:user-registration')    
        self.login_url = API_Reverse('authentication:user_login')    
        
        self.user = {
            "user": {
                "username": "test_user",
                "password": "testing123",
                "email": "test@test.com"
            }
        }

        self.user2 = {
            "user": {
                "username": "test_user2",
                "password": "testing123",
                "email": "test2@test.com"
            }
        }

        self.article = {
            "article": {
                "title": "test article",
                "description": "This is test description",
                "body": "This is a test body"
            }
        }

        self.comment = {
            "comment": {
                "body": "This is a test comment body."
            }
        }

    def create_user(self):
        response = self.client.post(self.signup_url, self.user, format='json')
        return response
    def activate_user(self):
        """Activate user after login"""
        self.client.post(self.signup_url, self.user, format='json')
        user = self.user['user']
        token = generate_token(user['username'])
        self.client.get(reverse("authentication:verify", args=[token]))
    def login_user(self):
        """This will login an existing user"""
        response = self.client.post(self.login_url, self.user, format='json')
        token = response.data['token']
        return token

    def create_article(self):
        self.create_user()
        self.activate_user()
        token = self.login_user()
        response = self.client.post(self.url, self.article, format='json', HTTP_AUTHORIZATION=token)
        self.client.credentials(HTTP_AUTHORIZATION=token)
        slug = response.data['slug']

        return slug

    def single_article_details(self):
        slug = self.create_article()
        url = API_Reverse('articles:article-details', {slug: 'slug'})
        return url

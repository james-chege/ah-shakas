from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse as API_Reverse

class BaseTest(APITestCase):
    """This class provides a base for other tests"""

    def setUp(self):
        self.url = API_Reverse('articles:articles')
        
        self.signup_url = API_Reverse('authentication:user-registration')    
        
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

        self.client = APIClient()
        self.unauthorised_client = APIClient()


    def create_user(self, user=None):
        if not user:
            user = self.user
        response = self.client.post(self.signup_url, user, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=token)
        return token

    def create_article(self):
        token = self.create_user()
        response = self.client.post(self.url, self.article, format='json', HTTP_AUTHORIZATION=token)
        slug = response.data['slug']

        return slug

    def single_article_details(self):
        slug = self.create_article()
        url = API_Reverse('articles:article-details', {slug: 'slug'})
        return url

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as API_Reverse


class ArticlesBaseTest(APITestCase):
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

        self.article = {
            "article": {
                "title": "test article",
                "description": "This is test description",
                "body": "This is a test body"
            }
        }

    def create_user(self):
        response = self.client.post(self.signup_url, self.user, format='json')
        token = response.data['token']

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

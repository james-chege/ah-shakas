from rest_framework import serializers
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator

from authors import settings
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.articles.helpers import get_time_to_read_article
from authors.apps.profiles.models import Profile
from rest_framework.validators import UniqueTogetherValidator
from authors.apps.profiles.serializers import ProfileSerializer
from .models import ArticlesModel, Rating, Comment, Favourite


class ArticlesSerializers(serializers.ModelSerializer):
    title = serializers.CharField(
        required=True,
        max_length=128,
        error_messages={
            'required': 'Title is required',
            'max_length': 'Title cannot be more than 128'
        }
    )
    description = serializers.CharField(
        required=False,
        max_length=250,
        error_messages={
            'max_length': 'Description should not be more than 250'
        }
    )
    body = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Body is required'
        }
    )

    image_url = serializers.URLField(
        required=False
    )
    favourited = serializers.SerializerMethodField()
    def get_favourited(self, obj):
        try:
            favourite = Favourite.objects.get(user=self.context["request"].user.id, article=obj.id)
            return True
        except:
            return False

    author = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_author(self, obj):
        """This method gets the profile object for the article"""
        serializer = ProfileSerializer(instance=Profile.objects.get(user=obj.author))
        return serializer.data

    def get_rating(self, obj):
        """This method gets and returns the rating for the article"""

        # Get average rating
        avg_rating = Rating.objects.filter(article=obj.id).aggregate(Avg('rating'))

        # Check that this user is authenticated in order to include their rating,
        # if not, we return the default rating 
        user = self.context["request"].user
        if user.is_authenticated:
            try:
                rating = Rating.objects.get(user=user, article=obj.id).rating
            except Rating.DoesNotExist:
                rating = None

            return {
                'avg_rating': avg_rating['rating__avg'],
                'rating': rating
            }

        return {
            'avg_rating': avg_rating['rating__avg']
        }

    def to_representation(self,instance):
       """
       overide representatiom for custom output
       """
       representation = super(ArticlesSerializers, self).to_representation(instance)
       representation['time_to_read'] = get_time_to_read_article(instance)
       return representation
    
    class Meta:
        model = ArticlesModel
        fields = (
            'title',
            'description',
            'body',
            'slug',
            'image_url',
            'author',
            'rating',
            'created_at',
            'updated_at',
            'favourited'
        )

class FavouriteSerializer(serializers.ModelSerializer):
    '''serializer for favouriting'''
    class Meta:
        model = Favourite
        fields=('article', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Favourite.objects.all(),
                fields=('article', 'user'),
                message = "You have already favourited this article"
            )
        ]

class CommentsSerializers(serializers.ModelSerializer):
    body = serializers.CharField(
       max_length = 200,
       required = True,
       error_messages = {
           'required': 'Comments field cannot be blank'
       }
    )
    def format_date(self, date):
        return date.strftime('%d %b %Y %H:%M:%S')

    def to_representation(self,instance):
       """
       overide representation for custom output
       """
       threads = [
                    {

                    'id': thread.id,
                        'body': thread.body,
                        'author': thread.author.username,
                        'created_at': self.format_date(thread.created_at),
                        'replies': thread.threads.count(),
                        'updated_at': self.format_date(thread.updated_at)
                    }  for thread in instance.threads.all()
                ]
    
       representation = super(CommentsSerializers, self).to_representation(instance)
       representation['created_at'] = self.format_date(instance.created_at)
       representation['updated_at'] = self.format_date(instance.updated_at)
       representation['author'] = instance.author.username
       representation['article'] = instance.article.title
       representation['reply_count'] = instance.threads.count() 
       representation['threads'] = threads
       del representation['parent']

       return representation

    class Meta:
       model = Comment
       fields = ('id', 'body', 'created_at', 'updated_at', 'author', 'article', 'parent') 
        

class RatingSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(
        required=True,
        validators=[
            MinValueValidator(
                settings.RATING_MIN,
                message='Rating cannot be less than ' + str(settings.RATING_MIN)
            ),
            MaxValueValidator(
                settings.RATING_MAX,
                message='Rating cannot be more than ' + str(settings.RATING_MAX)
            )
        ],
        error_messages={
            'required': 'The rating is required'
        }
    )

    avg_rating = serializers.SerializerMethodField()
    article = serializers.SerializerMethodField()

    def get_avg_rating(self, obj):
        avg = Rating.objects.filter(article=obj.article.id).aggregate(Avg('rating'))
        return avg['rating__avg']

    def get_article(self, obj):
        return obj.article.slug

    def get_rating(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj
        return None

    class Meta:
        model = Rating
        fields = ('article', 'rating', 'avg_rating')

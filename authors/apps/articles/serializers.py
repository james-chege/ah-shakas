from rest_framework import serializers

from authors.apps.profiles.models import Profile
from .models import ArticlesModel
from authors.apps.profiles.serializers import ProfileSerializer


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

    author = serializers.SerializerMethodField(read_only=True)

    def get_author(self, obj):
        """This method gets the profile object for the article"""
        serializer = ProfileSerializer(instance=Profile.objects.get(user=obj.author))
        return serializer.data

    class Meta:
        model = ArticlesModel
        fields = (
            'title',
            'description',
            'body',
            'slug',
            'image_url',
            'author',
            'created_at',
            'updated_at'
        )



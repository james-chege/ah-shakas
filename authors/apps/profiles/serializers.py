from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator

from .models import Profile
from authors.apps.authentication.models import User
from rest_framework.response import Response

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to map the UserProfile instance into JSON format
    """
    username = serializers.RegexField(
        regex='^(?!.*\ )[A-Za-z\d\-\_]+$',
        min_length=4,
        required=True,
        source='user.username',
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Username must be unique',
            )
        ],
        error_messages={
            'invalid': 'Username cannot have a space',
            'required': 'Username is required',
            'min_length': 'Username must have at least 4 characters'
        }
    )

    followers_count = serializers.IntegerField(
        read_only=True,
        source="followers.count"
    )

    following_count = serializers.IntegerField(
        read_only=True,
        source="following.count"
    )

    follow_status = serializers.SerializerMethodField()

    def get_follow_status(self, request):
        follows = Profile.objects.values_list('followers',flat=True).filter(
            user=request.user.id,
            followers=self.context['request'].user.id
            )
        if (follows):
            return True
        else:
            return False
        


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        super().update(instance, validated_data)
        if user_data is not None and user_data.get('username') is not None:
            instance.user.username = user_data.get('username')
            instance.user.save()
        return instance


    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image_url', 'followers_count', 'follow_status', 'following_count', 'created_at', 'updated_at')

class ProfileListSerializer(serializers.ModelSerializer):
    """
    serializes the list of profiles to be shown
    """
    username = serializers.CharField(source='user.username', read_only=True)

    followers_count = serializers.IntegerField(
        read_only=True,
        source="followers.count"
    )

    following_count = serializers.IntegerField(
        read_only=True,
        source="following.count"
    )
    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image_url', 'followers_count', 'following_count')

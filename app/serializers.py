from rest_framework import serializers
from . models import User , Post , Comment


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email' , 'password']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title' , 'desc']

LIKE_CHOICES = (
        (True, 'Like'),
        (False, 'Dislike'),
    )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']


class CommentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id' , 'user' , 'post' , 'content']

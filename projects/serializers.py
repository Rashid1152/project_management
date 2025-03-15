from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, ProjectUser, Comment
from users.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'owner']
        read_only_fields = ['created_at', 'updated_at']


class ProjectUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = ProjectUser
        fields = ['id', 'project', 'user', 'user_details', 'role', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {
            'project': {'required': False}
        }


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'project', 'user', 'text', 'created_at']
        read_only_fields = ['created_at', 'user']
        extra_kwargs = {
            'project': {'required': False}
        } 
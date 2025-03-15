from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Project, ProjectUser, Comment
from .serializers import ProjectSerializer, ProjectUserSerializer, CommentSerializer
from .permissions import IsProjectOwner, IsProjectOwnerOrEditor, HasProjectAccess


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only projects the user has access to
        user = self.request.user
        return Project.objects.filter(projectuser__user=user).distinct()

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [permissions.IsAuthenticated, IsProjectOwnerOrEditor]
        elif self.action in ['destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsProjectOwner]
        elif self.action in ['retrieve']:
            self.permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Create the project and assign the current user as owner
        project = serializer.save()
        ProjectUser.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectUser.OWNER
        )

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        project = self.get_object()
        project_users = ProjectUser.objects.filter(project=project)
        serializer = ProjectUserSerializer(project_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsProjectOwner])
    def add_user(self, request, pk=None):
        project = self.get_object()
        
        # Check if username is provided
        username = request.data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                # Check if user is already in the project
                if ProjectUser.objects.filter(project=project, user=user).exists():
                    return Response({"detail": "User is already in the project."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Create project user with the provided role
                role = request.data.get('role', ProjectUser.READER)
                project_user = ProjectUser.objects.create(
                    project=project,
                    user=user,
                    role=role
                )
                serializer = ProjectUserSerializer(project_user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # If username is not provided, fall back to the original behavior
        serializer = ProjectUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove-user/(?P<user_id>[^/.]+)', permission_classes=[permissions.IsAuthenticated, IsProjectOwner])
    def remove_user(self, request, pk=None, user_id=None):
        project = self.get_object()
        project_user = get_object_or_404(ProjectUser, project=project, user_id=user_id)
        
        # Prevent removing the owner
        if project_user.role == ProjectUser.OWNER:
            return Response({"detail": "Cannot remove the project owner."}, status=status.HTTP_400_BAD_REQUEST)
        
        project_user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='update-role/(?P<user_id>[^/.]+)', permission_classes=[permissions.IsAuthenticated, IsProjectOwner])
    def update_role(self, request, pk=None, user_id=None):
        project = self.get_object()
        project_user = get_object_or_404(ProjectUser, project=project, user_id=user_id)
        
        # Prevent changing the owner's role
        if project_user.role == ProjectUser.OWNER:
            return Response({"detail": "Cannot change the owner's role."}, status=status.HTTP_400_BAD_REQUEST)
        
        role = request.data.get('role')
        if role not in [choice[0] for choice in ProjectUser.ROLE_CHOICES]:
            return Response({"detail": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)
        
        project_user.role = role
        project_user.save()
        
        serializer = ProjectUserSerializer(project_user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        project = self.get_object()
        comments = Comment.objects.filter(project=project)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsProjectOwnerOrEditor])
    def add_comment(self, request, pk=None):
        project = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(project=project, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
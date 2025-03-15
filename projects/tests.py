import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from .models import Project, ProjectUser, Comment


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(username='testuser', email='test@example.com', password='testpassword123'):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
    return _create_user


@pytest.fixture
def create_project(create_user):
    def _create_project(title='Test Project', description='Test Description', owner=None):
        if owner is None:
            owner = create_user()
        
        project = Project.objects.create(
            title=title,
            description=description
        )
        
        ProjectUser.objects.create(
            project=project,
            user=owner,
            role=ProjectUser.OWNER
        )
        
        return project, owner
    return _create_project


@pytest.mark.django_db
class TestProjectCRUD:
    def test_create_project(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'Project Description'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Project.objects.filter(title='New Project').exists()
        
        # Check if user is assigned as owner
        project = Project.objects.get(title='New Project')
        assert ProjectUser.objects.filter(project=project, user=user, role=ProjectUser.OWNER).exists()
    
    def test_list_projects(self, api_client, create_project, create_user):
        # Create projects with different owners
        project1, owner1 = create_project(title='Project 1')
        project2, owner2 = create_project(title='Project 2', owner=create_user(username='user2'))
        
        # Add user1 as editor to project2
        ProjectUser.objects.create(
            project=project2,
            user=owner1,
            role=ProjectUser.EDITOR
        )
        
        # Authenticate as owner1
        api_client.force_authenticate(user=owner1)
        
        url = reverse('project-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # User should see both projects
    
    def test_retrieve_project(self, api_client, create_project):
        project, owner = create_project()
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-detail', args=[project.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == project.title
    
    def test_update_project_owner(self, api_client, create_project):
        project, owner = create_project()
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-detail', args=[project.id])
        data = {
            'title': 'Updated Title',
            'description': project.description
        }
        
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        project.refresh_from_db()
        assert project.title == 'Updated Title'
    
    def test_update_project_editor(self, api_client, create_project, create_user):
        project, owner = create_project()
        editor = create_user(username='editor')
        
        # Add editor to project
        ProjectUser.objects.create(
            project=project,
            user=editor,
            role=ProjectUser.EDITOR
        )
        
        api_client.force_authenticate(user=editor)
        
        url = reverse('project-detail', args=[project.id])
        data = {
            'title': 'Editor Updated',
            'description': project.description
        }
        
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        project.refresh_from_db()
        assert project.title == 'Editor Updated'
    
    def test_update_project_reader(self, api_client, create_project, create_user):
        project, owner = create_project()
        reader = create_user(username='reader')
        
        # Add reader to project
        ProjectUser.objects.create(
            project=project,
            user=reader,
            role=ProjectUser.READER
        )
        
        api_client.force_authenticate(user=reader)
        
        url = reverse('project-detail', args=[project.id])
        data = {
            'title': 'Reader Updated',
            'description': project.description
        }
        
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_project_owner(self, api_client, create_project):
        project, owner = create_project()
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-detail', args=[project.id])
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(id=project.id).exists()
    
    def test_delete_project_editor(self, api_client, create_project, create_user):
        project, owner = create_project()
        editor = create_user(username='editor')
        
        # Add editor to project
        ProjectUser.objects.create(
            project=project,
            user=editor,
            role=ProjectUser.EDITOR
        )
        
        api_client.force_authenticate(user=editor)
        
        url = reverse('project-detail', args=[project.id])
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Project.objects.filter(id=project.id).exists()


@pytest.mark.django_db
class TestProjectUsers:
    def test_add_user_to_project(self, api_client, create_project, create_user):
        project, owner = create_project()
        new_user = create_user(username='newuser')
        
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-add-user', args=[project.id])
        data = {
            'username': new_user.username,
            'role': ProjectUser.EDITOR
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert ProjectUser.objects.filter(project=project, user=new_user, role=ProjectUser.EDITOR).exists()
    
    def test_remove_user_from_project(self, api_client, create_project, create_user):
        project, owner = create_project()
        editor = create_user(username='editor')
        
        # Add editor to project
        project_user = ProjectUser.objects.create(
            project=project,
            user=editor,
            role=ProjectUser.EDITOR
        )
        
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-remove-user', args=[project.id, editor.id])
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ProjectUser.objects.filter(id=project_user.id).exists()
    
    def test_update_user_role(self, api_client, create_project, create_user):
        project, owner = create_project()
        editor = create_user(username='editor')
        
        # Add editor to project
        ProjectUser.objects.create(
            project=project,
            user=editor,
            role=ProjectUser.EDITOR
        )
        
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-update-role', args=[project.id, editor.id])
        data = {
            'role': ProjectUser.READER
        }
        
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        project_user = ProjectUser.objects.get(project=project, user=editor)
        assert project_user.role == ProjectUser.READER


@pytest.mark.django_db
class TestComments:
    def test_add_comment_owner(self, api_client, create_project):
        project, owner = create_project()
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-add-comment', args=[project.id])
        data = {
            'text': 'Test comment from owner'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        comment = Comment.objects.get(project=project)
        assert comment.text == 'Test comment from owner'
        assert comment.user == owner
    
    def test_add_comment_editor(self, api_client, create_project, create_user):
        project, owner = create_project()
        editor = create_user(username='editor')
        
        # Add editor to project
        ProjectUser.objects.create(
            project=project,
            user=editor,
            role=ProjectUser.EDITOR
        )
        
        api_client.force_authenticate(user=editor)
        
        url = reverse('project-add-comment', args=[project.id])
        data = {
            'text': 'Test comment from editor'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        comment = Comment.objects.get(project=project)
        assert comment.text == 'Test comment from editor'
        assert comment.user == editor
    
    def test_add_comment_reader(self, api_client, create_project, create_user):
        project, owner = create_project()
        reader = create_user(username='reader')
        
        # Add reader to project
        ProjectUser.objects.create(
            project=project,
            user=reader,
            role=ProjectUser.READER
        )
        
        api_client.force_authenticate(user=reader)
        
        url = reverse('project-add-comment', args=[project.id])
        data = {
            'text': 'Test comment from reader'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Comment.objects.filter(project=project, user=reader).exists()
    
    def test_list_comments(self, api_client, create_project):
        project, owner = create_project()
        
        # Create some comments
        Comment.objects.create(project=project, user=owner, text='Comment 1')
        Comment.objects.create(project=project, user=owner, text='Comment 2')
        
        api_client.force_authenticate(user=owner)
        
        url = reverse('project-comments', args=[project.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2 
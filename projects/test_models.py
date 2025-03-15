import pytest
from django.contrib.auth.models import User
from .models import Project, ProjectUser

@pytest.mark.django_db
def test_create_project():
    """Test that a project can be created"""
    # Create a user first
    user = User.objects.create_user(
        username='projectowner',
        email='owner@example.com',
        password='password123'
    )
    
    # Create a project
    project = Project.objects.create(
        title='Test Project',
        description='This is a test project'
    )
    
    # Add the user as owner
    ProjectUser.objects.create(
        project=project,
        user=user,
        role=ProjectUser.OWNER
    )
    
    assert project.title == 'Test Project'
    assert project.description == 'This is a test project'
    assert project.owner == user 
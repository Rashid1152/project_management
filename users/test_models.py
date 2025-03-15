import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_create_user():
    """Test that a user can be created"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password123'
    )
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('password123') 
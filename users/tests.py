import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


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


@pytest.mark.django_db
class TestUserRegistration:
    def test_user_registration_success(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
    
    def test_user_registration_password_mismatch(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password2': 'differentpassword',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_user_registration_duplicate_username(self, api_client, create_user):
        create_user(username='existinguser')
        
        url = reverse('register')
        data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data


@pytest.mark.django_db
class TestUserLogin:
    def test_user_login_success(self, api_client, create_user):
        user = create_user()
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
    
    def test_user_login_invalid_credentials(self, api_client, create_user):
        create_user()
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data


@pytest.mark.django_db
class TestUserLogout:
    def test_user_logout(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        
        url = reverse('logout')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data


@pytest.mark.django_db
class TestUserDetail:
    def test_get_user_detail_authenticated(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        
        url = reverse('user-detail')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
    
    def test_get_user_detail_unauthenticated(self, api_client):
        url = reverse('user-detail')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN 
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from chama.models import ChamaGroup, GroupMembership

User = get_user_model()

class ChamaAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'phone_number': '1234567890',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/api/users/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
    def test_user_login(self):
        """Test user login"""
        # First create a user
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            phone_number='1234567890',
            password='testpass123'
        )
        
        # Now test login
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/users/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_create_chama_group(self):
        """Test creating a chama group"""
        # Create and authenticate user
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            phone_number='1234567890',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        group_data = {
            'name': 'Test Chama',
            'description': 'A test chama group',
            'contribution_amount': '1000.00',
            'contribution_frequency': 'weekly',
            'max_members': 10,
            'group_type': 'merry_go_round'
        }
        
        response = self.client.post('/api/chama/groups/', group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ChamaGroup.objects.filter(name='Test Chama').exists())
        
        # Check that the creator is automatically added as a member
        group = ChamaGroup.objects.get(name='Test Chama')
        self.assertTrue(GroupMembership.objects.filter(group=group, member=user).exists())
        
    def test_join_chama_group(self):
        """Test joining a chama group"""
        # Create group creator
        creator = User.objects.create_user(
            email='creator@example.com',
            username='creator',
            phone_number='1111111111',
            password='testpass123'
        )
        
        # Create another user
        joiner = User.objects.create_user(
            email='joiner@example.com',
            username='joiner',
            phone_number='2222222222',
            password='testpass123'
        )
        
        # Create a group
        group = ChamaGroup.objects.create(
            name='Test Chama',
            description='A test chama group',
            creator=creator,
            contribution_amount=1000.00,
            contribution_frequency='weekly',
            max_members=10,
            group_type='merry_go_round'
        )
        
        # Add creator as first member
        GroupMembership.objects.create(group=group, member=creator, order=1)
        
        # Authenticate as joiner and join the group
        self.client.force_authenticate(user=joiner)
        response = self.client.post(f'/api/chama/groups/{group.id}/join/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(GroupMembership.objects.filter(group=group, member=joiner).exists())
        
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        response = self.client.get('/api/chama/groups/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_group_dashboard(self):
        """Test user dashboard"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            phone_number='1234567890',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.get('/api/chama/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('groups_count', response.data)
        self.assertIn('total_contributions', response.data)

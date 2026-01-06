import pytest
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from coaching.models import UserProfile, VisionElement, VisionBoard, VisionBoardElement, WheelAssessment, Goal


@pytest.mark.django_db
class TestUserProfileAPI(APITestCase):
    def setUp(self):
        """Set up test user and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            'bio': 'Updated bio',
            'coaching_focus': 'Personal Growth'
        }
        response = self.client.patch('/api/profiles/me/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        self.assertEqual(response.data['coaching_focus'], 'Personal Growth')


@pytest.mark.django_db
class TestVisionBoardAPI(APITestCase):
    def setUp(self):
        """Set up test user and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_vision_board(self):
        """Test creating a vision board"""
        data = {
            'title': 'My Goals Board',
            'description': 'Board for 2024 goals',
            'elements': [
                {'type': 'text', 'content': 'Be healthy', 'x': 100, 'y': 100}
            ]
        }
        response = self.client.post('/api/vision-boards/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'My Goals Board')
        self.assertEqual(len(response.data['elements']), 1)

    def test_get_vision_boards(self):
        """Test getting user's vision boards"""
        # Create a board
        VisionBoard.objects.create(
            user=self.user,
            title='Test Board',
            elements=[]
        )

        response = self.client.get('/api/vision-boards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Board')

    def test_duplicate_vision_board(self):
        """Test duplicating a vision board"""
        board = VisionBoard.objects.create(
            user=self.user,
            title='Original Board',
            elements=[{'type': 'text', 'content': 'Test', 'x': 0, 'y': 0}]
        )

        response = self.client.post(f'/api/vision-boards/{board.id}/duplicate/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Original Board (Copy)')

        # Check that we now have 2 boards
        response = self.client.get('/api/vision-boards/')
        self.assertEqual(len(response.data), 2)


@pytest.mark.django_db
class TestWheelAssessmentAPI(APITestCase):
    def setUp(self):
        """Set up test user and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_wheel_assessment(self):
        """Test creating a wheel assessment"""
        data = {
            'title': 'Monthly Check-in',
            'career': 8,
            'health': 7,
            'relationships': 9,
            'personal_growth': 6,
            'fun_recreation': 5,
            'home_family': 8,
            'contribution': 7,
            'spirituality': 6,
            'notes': 'Feeling good overall'
        }
        response = self.client.post('/api/wheel-assessments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Monthly Check-in')
        self.assertEqual(response.data['average_score'], 7.0)

    def test_get_assessments(self):
        """Test getting user's assessments"""
        # Create an assessment
        WheelAssessment.objects.create(
            user=self.user,
            title='Test Assessment',
            career=7, health=7, relationships=7, personal_growth=7,
            fun_recreation=7, home_family=7, contribution=7, spirituality=7
        )

        response = self.client.get('/api/wheel-assessments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['average_score'], 7.0)

    def test_get_latest_assessment(self):
        """Test getting the latest assessment"""
        # Create assessments
        WheelAssessment.objects.create(
            user=self.user, title='First',
            career=5, health=5, relationships=5, personal_growth=5,
            fun_recreation=5, home_family=5, contribution=5, spirituality=5
        )
        latest = WheelAssessment.objects.create(
            user=self.user, title='Latest',
            career=8, health=8, relationships=8, personal_growth=8,
            fun_recreation=8, home_family=8, contribution=8, spirituality=8
        )

        response = self.client.get('/api/wheel-assessments/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Latest')
        self.assertEqual(response.data['average_score'], 8.0)

    def test_get_assessment_stats(self):
        """Test getting assessment statistics"""
        WheelAssessment.objects.create(
            user=self.user, title='Test',
            career=6, health=9, relationships=7, personal_growth=5,
            fun_recreation=8, home_family=7, contribution=6, spirituality=4
        )

        response = self.client.get('/api/wheel-assessments/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_assessments'], 1)
        self.assertEqual(response.data['latest_average'], 6.5)
        self.assertIn('career', response.data['areas'])
        self.assertIn('spirituality', response.data['improvement_areas'])


@pytest.mark.django_db
class TestGoalAPI(APITestCase):
    def setUp(self):
        """Set up test user and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_goal(self):
        """Test creating a goal"""
        data = {
            'wheel_area': 'health',
            'title': 'Run 5K daily',
            'description': 'Build running habit',
            'progress': 25,
            'status': 'active'
        }
        response = self.client.post('/api/goals/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Run 5K daily')
        self.assertEqual(response.data['wheel_area'], 'health')
        self.assertEqual(response.data['progress'], 25)

    def test_get_goals(self):
        """Test getting user's goals"""
        # Create a goal
        Goal.objects.create(
            user=self.user,
            wheel_area='health',
            title='Test Goal'
        )

        response = self.client.get('/api/goals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Goal')

    def test_get_active_goals(self):
        """Test getting only active goals"""
        # Create goals with different statuses
        Goal.objects.create(user=self.user, wheel_area='health', title='Active Goal', status='active')
        Goal.objects.create(user=self.user, wheel_area='career', title='Completed Goal', status='completed')

        response = self.client.get('/api/goals/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Active Goal')

    def test_update_goal_progress(self):
        """Test updating goal progress"""
        goal = Goal.objects.create(
            user=self.user,
            wheel_area='health',
            title='Test Goal',
            progress=0
        )

        # Update progress
        response = self.client.post(f'/api/goals/{goal.id}/update_progress/', {'progress': 75})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 75)

        # Update to 100% should mark as completed
        response = self.client.post(f'/api/goals/{goal.id}/update_progress/', {'progress': 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 100)
        self.assertEqual(response.data['status'], 'completed')

    def test_get_goals_by_area(self):
        """Test getting goals grouped by area"""
        Goal.objects.create(user=self.user, wheel_area='health', title='Health Goal')
        Goal.objects.create(user=self.user, wheel_area='career', title='Career Goal')
        Goal.objects.create(user=self.user, wheel_area='health', title='Another Health Goal')

        response = self.client.get('/api/goals/by_area/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should have health and career areas
        self.assertIn('Health/Wellness', response.data)
        self.assertIn('Career/Finance', response.data)
        self.assertEqual(len(response.data['Health/Wellness']), 2)
        self.assertEqual(len(response.data['Career/Finance']), 1)


@pytest.mark.django_db
class TestAuthAPI(APITestCase):
    def test_register_user(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'pass1',
            'password_confirm': 'pass2'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_get_current_user_unauthenticated(self):
        """Test getting current user when not authenticated"""
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user_authenticated(self):
        """Test getting current user when authenticated"""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')


@pytest.mark.django_db
class TestVisionElementAPI(APITestCase):
    def setUp(self):
        """Set up test user and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_vision_element(self):
        """Test creating a vision element"""
        data = {
            'element_type': 'text',
            'title': 'My Goal',
            'content': 'Achieve financial freedom',
            'color': '#ff0000',
            'font_size': 18,
            'text_color': '#ffffff'
        }
        response = self.client.post('/api/vision-elements/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['element_type'], 'text')
        self.assertEqual(response.data['title'], 'My Goal')
        self.assertEqual(response.data['content'], 'Achieve financial freedom')

    def test_create_element_empty_title(self):
        """Test creating element with empty title (should be allowed)"""
        data = {
            'element_type': 'text',
            'content': 'Content without title'
        }
        response = self.client.post('/api/vision-elements/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], '')
        self.assertEqual(response.data['content'], 'Content without title')

    def test_create_element_empty_content(self):
        """Test creating element with empty content (should fail)"""
        data = {
            'element_type': 'text',
            'title': 'Title without content'
        }
        response = self.client.post('/api/vision-elements/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

    def test_create_element_invalid_type(self):
        """Test creating element with invalid element_type"""
        data = {
            'element_type': 'invalid_type',
            'content': 'Test content'
        }
        response = self.client.post('/api/vision-elements/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('element_type', response.data)

    def test_get_vision_elements(self):
        """Test getting user's vision elements"""
        # Create elements
        VisionElement.objects.create(
            user=self.user,
            element_type='text',
            content='First element'
        )
        VisionElement.objects.create(
            user=self.user,
            element_type='quote',
            content='Second element'
        )

        response = self.client.get('/api/vision-elements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_other_user_elements(self):
        """Test that users can only see their own elements"""
        other_user = User.objects.create_user(username='otheruser', password='pass123')
        VisionElement.objects.create(
            user=other_user,
            element_type='text',
            content='Other user element'
        )

        response = self.client.get('/api/vision-elements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should not see other user's elements

    def test_update_vision_element(self):
        """Test updating a vision element"""
        element = VisionElement.objects.create(
            user=self.user,
            element_type='text',
            content='Original content'
        )

        data = {'content': 'Updated content'}
        response = self.client.patch(f'/api/vision-elements/{element.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated content')

    def test_delete_vision_element(self):
        """Test deleting a vision element"""
        element = VisionElement.objects.create(
            user=self.user,
            element_type='text',
            content='Test element'
        )

        response = self.client.delete(f'/api/vision-elements/{element.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's deleted
        response = self.client.get(f'/api/vision-elements/{element.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class TestVisionBoardUpdateLayoutAPI(APITestCase):
    def setUp(self):
        """Set up test user and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_update_layout_valid_elements(self):
        """Test updating board layout with valid elements"""
        board = VisionBoard.objects.create(user=self.user, title='Test Board')
        element1 = VisionElement.objects.create(user=self.user, element_type='text', content='Element 1')
        element2 = VisionElement.objects.create(user=self.user, element_type='text', content='Element 2')

        layout_data = {
            'elements': [
                {'element_id': element1.id, 'x': 100, 'y': 100, 'width': 200, 'height': 150},
                {'element_id': element2.id, 'x': 300, 'y': 100, 'width': 200, 'height': 150}
            ]
        }

        response = self.client.post(f'/api/vision-boards/{board.id}/update_layout/', layout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that board elements were created
        board_elements = VisionBoardElement.objects.filter(vision_board=board)
        self.assertEqual(board_elements.count(), 2)

    def test_update_layout_nonexistent_element(self):
        """Test updating board layout with non-existent element ID"""
        board = VisionBoard.objects.create(user=self.user, title='Test Board')

        layout_data = {
            'elements': [
                {'element_id': 99999, 'x': 100, 'y': 100, 'width': 200, 'height': 150}
            ]
        }

        response = self.client.post(f'/api/vision-boards/{board.id}/update_layout/', layout_data, format='json')
        # This should fail because the element doesn't exist
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_layout_other_user_element(self):
        """Test updating board layout with another user's element"""
        board = VisionBoard.objects.create(user=self.user, title='Test Board')
        other_user = User.objects.create_user(username='otheruser', password='pass123')
        other_element = VisionElement.objects.create(user=other_user, element_type='text', content='Other element')

        layout_data = {
            'elements': [
                {'element_id': other_element.id, 'x': 100, 'y': 100, 'width': 200, 'height': 150}
            ]
        }

        response = self.client.post(f'/api/vision-boards/{board.id}/update_layout/', layout_data, format='json')
        # This should fail because the element belongs to another user
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_layout_nonexistent_board(self):
        """Test updating layout for non-existent board"""
        layout_data = {
            'elements': [
                {'element_id': 1, 'x': 100, 'y': 100, 'width': 200, 'height': 150}
            ]
        }

        response = self.client.post('/api/vision-boards/99999/update_layout/', layout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from coaching.models import UserProfile, VisionElement, VisionBoard, VisionBoardElement, WheelAssessment, Goal


@pytest.mark.django_db
class TestUserProfile:
    def test_create_user_profile(self):
        """Test creating a user profile"""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        profile = UserProfile.objects.create(
            user=user,
            bio='Test bio',
            coaching_focus='Personal Growth'
        )

        assert profile.user == user
        assert profile.bio == 'Test bio'
        assert profile.coaching_focus == 'Personal Growth'
        assert str(profile) == "testuser's profile"

    def test_profile_str_representation(self):
        """Test string representation of profile"""
        user = User.objects.create_user(username='john_doe')
        profile = UserProfile.objects.create(user=user)
        assert str(profile) == "john_doe's profile"


@pytest.mark.django_db
class TestVisionBoard:
    def test_create_vision_board(self):
        """Test creating a vision board"""
        user = User.objects.create_user(username='testuser')
        board = VisionBoard.objects.create(
            user=user,
            title='My Goals Board',
            description='Board for 2024 goals',
            elements=[
                {'type': 'text', 'content': 'Be healthy', 'x': 100, 'y': 100},
                {'type': 'image', 'url': 'image.jpg', 'x': 200, 'y': 200}
            ]
        )

        assert board.user == user
        assert board.title == 'My Goals Board'
        assert board.description == 'Board for 2024 goals'
        assert len(board.elements) == 2
        assert board.is_active is True
        assert str(board) == 'testuser - My Goals Board'

    def test_board_ordering(self):
        """Test that boards are ordered by updated_at descending"""
        user = User.objects.create_user(username='testuser')

        # Create boards with different update times
        board1 = VisionBoard.objects.create(user=user, title='Board 1')
        board2 = VisionBoard.objects.create(user=user, title='Board 2')

        # Update board1 to make it more recent
        board1.title = 'Updated Board 1'
        board1.save()

        boards = VisionBoard.objects.all()
        assert boards[0] == board1  # Most recently updated first
        assert boards[1] == board2


@pytest.mark.django_db
class TestWheelAssessment:
    def test_create_wheel_assessment(self):
        """Test creating a wheel assessment"""
        user = User.objects.create_user(username='testuser')
        assessment = WheelAssessment.objects.create(
            user=user,
            title='Monthly Check-in',
            career=8,
            health=7,
            relationships=9,
            personal_growth=6,
            fun_recreation=5,
            home_family=8,
            contribution=7,
            spirituality=6,
            notes='Feeling good overall'
        )

        assert assessment.user == user
        assert assessment.title == 'Monthly Check-in'
        assert assessment.career == 8
        assert assessment.health == 7
        assert str(assessment).startswith('testuser - Monthly Check-in')

    def test_get_average_score(self):
        """Test calculating average score"""
        user = User.objects.create_user(username='testuser')
        assessment = WheelAssessment.objects.create(
            user=user,
            career=8, health=7, relationships=9, personal_growth=6,
            fun_recreation=5, home_family=8, contribution=7, spirituality=6
        )

        # Average: (8+7+9+6+5+8+7+6) / 8 = 56 / 8 = 7.0
        assert assessment.get_average_score() == 7.0

    def test_get_scores_dict(self):
        """Test getting scores as dictionary"""
        user = User.objects.create_user(username='testuser')
        assessment = WheelAssessment.objects.create(
            user=user,
            career=8, health=7, relationships=9, personal_growth=6,
            fun_recreation=5, home_family=8, contribution=7, spirituality=6
        )

        scores = assessment.get_scores_dict()
        assert scores['career'] == 8
        assert scores['health'] == 7
        assert scores['relationships'] == 9

    def test_score_validation(self):
        """Test that scores must be between 1-10"""
        user = User.objects.create_user(username='testuser')

        # Test minimum value
        with pytest.raises(ValidationError):
            assessment = WheelAssessment(
                user=user, career=0, health=7, relationships=9, personal_growth=6,
                fun_recreation=5, home_family=8, contribution=7, spirituality=6
            )
            assessment.full_clean()

        # Test maximum value
        with pytest.raises(ValidationError):
            assessment = WheelAssessment(
                user=user, career=11, health=7, relationships=9, personal_growth=6,
                fun_recreation=5, home_family=8, contribution=7, spirituality=6
            )
            assessment.full_clean()

    def test_assessment_ordering(self):
        """Test that assessments are ordered by created_at descending"""
        user = User.objects.create_user(username='testuser')

        assessment1 = WheelAssessment.objects.create(
            user=user, title='First',
            career=5, health=5, relationships=5, personal_growth=5,
            fun_recreation=5, home_family=5, contribution=5, spirituality=5
        )
        assessment2 = WheelAssessment.objects.create(
            user=user, title='Second',
            career=6, health=6, relationships=6, personal_growth=6,
            fun_recreation=6, home_family=6, contribution=6, spirituality=6
        )

        assessments = WheelAssessment.objects.all()
        assert assessments[0] == assessment2  # Most recent first
        assert assessments[1] == assessment1


@pytest.mark.django_db
class TestGoal:
    def test_create_goal(self):
        """Test creating a goal"""
        user = User.objects.create_user(username='testuser')
        goal = Goal.objects.create(
            user=user,
            wheel_area='health',
            title='Run 5K daily',
            description='Build running habit',
            progress=25,
            status='active'
        )

        assert goal.user == user
        assert goal.wheel_area == 'health'
        assert goal.title == 'Run 5K daily'
        assert goal.progress == 25
        assert goal.status == 'active'
        assert str(goal) == 'testuser - Run 5K daily'

    def test_goal_status_choices(self):
        """Test goal status choices"""
        user = User.objects.create_user(username='testuser')

        # Test all valid statuses
        for status in ['active', 'completed', 'paused', 'cancelled']:
            goal = Goal.objects.create(
                user=user,
                wheel_area='career',
                title=f'Goal {status}',
                status=status
            )
            assert goal.status == status

    def test_progress_validation(self):
        """Test that progress must be between 0-100"""
        user = User.objects.create_user(username='testuser')

        # Test negative progress
        with pytest.raises(ValidationError):
            goal = Goal(user=user, wheel_area='health', title='Test', progress=-1)
            goal.full_clean()

        # Test progress over 100
        with pytest.raises(ValidationError):
            goal = Goal(user=user, wheel_area='health', title='Test', progress=101)
            goal.full_clean()

    def test_is_overdue(self):
        """Test overdue goal detection"""
        user = User.objects.create_user(username='testuser')

        # Future date - not overdue
        future_date = timezone.now().date().replace(year=timezone.now().year + 1)
        goal_future = Goal.objects.create(
            user=user,
            wheel_area='health',
            title='Future goal',
            target_date=future_date,
            status='active'
        )
        assert not goal_future.is_overdue()

        # Past date - overdue
        past_date = timezone.now().date().replace(year=timezone.now().year - 1)
        goal_past = Goal.objects.create(
            user=user,
            wheel_area='health',
            title='Past goal',
            target_date=past_date,
            status='active'
        )
        assert goal_past.is_overdue()

        # No target date - not overdue
        goal_no_date = Goal.objects.create(
            user=user,
            wheel_area='health',
            title='No date goal',
            status='active'
        )
        assert not goal_no_date.is_overdue()

        # Completed goal - not overdue
        goal_completed = Goal.objects.create(
            user=user,
            wheel_area='health',
            title='Completed goal',
            target_date=past_date,
            status='completed'
        )
        assert not goal_completed.is_overdue()

    def test_goal_ordering(self):
        """Test that goals are ordered by created_at descending"""
        user = User.objects.create_user(username='testuser')

        goal1 = Goal.objects.create(user=user, wheel_area='health', title='Goal 1')
        goal2 = Goal.objects.create(user=user, wheel_area='health', title='Goal 2')

        goals = Goal.objects.all()
        assert goals[0] == goal2  # Most recent first
        assert goals[1] == goal1


@pytest.mark.django_db
class TestVisionElement:
    def test_create_vision_element(self):
        """Test creating a vision element"""
        user = User.objects.create_user(username='testuser')
        element = VisionElement.objects.create(
            user=user,
            element_type='text',
            title='My Goal',
            content='Achieve financial freedom',
            color='#ff0000',
            font_size=18,
            text_color='#ffffff'
        )

        assert element.user == user
        assert element.element_type == 'text'
        assert element.title == 'My Goal'
        assert element.content == 'Achieve financial freedom'
        assert element.color == '#ff0000'
        assert element.font_size == 18
        assert element.text_color == '#ffffff'
        assert str(element) == 'testuser - My Goal'

    def test_create_element_without_title(self):
        """Test creating element with empty title (should be allowed)"""
        user = User.objects.create_user(username='testuser')
        element = VisionElement.objects.create(
            user=user,
            element_type='text',
            content='Content without title'
        )

        assert element.title == ''  # Empty string allowed
        assert element.content == 'Content without title'
        assert str(element) == 'testuser - Content without title'

    def test_element_types(self):
        """Test valid element types"""
        user = User.objects.create_user(username='testuser')

        for element_type in ['text', 'image', 'quote']:
            element = VisionElement.objects.create(
                user=user,
                element_type=element_type,
                content=f'{element_type} content'
            )
            assert element.element_type == element_type

    def test_element_ordering(self):
        """Test that elements are ordered by created_at descending"""
        user = User.objects.create_user(username='testuser')

        element1 = VisionElement.objects.create(user=user, element_type='text', content='First')
        element2 = VisionElement.objects.create(user=user, element_type='text', content='Second')

        elements = VisionElement.objects.all()
        assert elements[0] == element2  # Most recent first
        assert elements[1] == element1


@pytest.mark.django_db
class TestVisionBoardElement:
    def test_create_board_element(self):
        """Test creating a vision board element"""
        user = User.objects.create_user(username='testuser')
        board = VisionBoard.objects.create(user=user, title='Test Board')
        element = VisionElement.objects.create(user=user, element_type='text', content='Test')

        board_element = VisionBoardElement.objects.create(
            vision_board=board,
            vision_element=element,
            x_position=100,
            y_position=200,
            width=150,
            height=100,
            z_index=1,
            rotation=45
        )

        assert board_element.vision_board == board
        assert board_element.vision_element == element
        assert board_element.x_position == 100
        assert board_element.y_position == 200
        assert board_element.width == 150
        assert board_element.height == 100
        assert board_element.z_index == 1
        assert board_element.rotation == 45

    def test_unique_together_constraint(self):
        """Test that board-element pairs must be unique"""
        user = User.objects.create_user(username='testuser')
        board = VisionBoard.objects.create(user=user, title='Test Board')
        element = VisionElement.objects.create(user=user, element_type='text', content='Test')

        # First board element should work
        VisionBoardElement.objects.create(vision_board=board, vision_element=element)

        # Second should fail due to unique constraint
        with pytest.raises(Exception):  # Could be IntegrityError or ValidationError
            VisionBoardElement.objects.create(vision_board=board, vision_element=element)
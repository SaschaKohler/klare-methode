from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UserProfile, VisionElement, VisionBoard, VisionBoardElement, WheelAssessment, WheelArea, WheelAssessmentScore, Goal


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'bio', 'coaching_focus', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VisionElementSerializer(serializers.ModelSerializer):
    """Serializer for vision elements"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = VisionElement
        fields = [
            'id', 'element_type', 'title', 'content', 'image', 'image_url',
            'color', 'font_size', 'text_color', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']

    def get_image_url(self, obj):
        """Get full image URL"""
        if obj.image:
            return obj.image.url
        return None

    def create(self, validated_data):
        """Create element for the authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class VisionBoardElementSerializer(serializers.ModelSerializer):
    """Serializer for board element positions"""
    vision_element = VisionElementSerializer(read_only=True)

    class Meta:
        model = VisionBoardElement
        fields = [
            'id', 'vision_element', 'x_position', 'y_position',
            'width', 'height', 'z_index', 'rotation'
        ]
        read_only_fields = ['id']


class VisionBoardSerializer(serializers.ModelSerializer):
    """Serializer for vision boards"""
    board_elements = VisionBoardElementSerializer(many=True, read_only=True)

    class Meta:
        model = VisionBoard
        fields = [
            'id', 'title', 'description', 'elements', 'board_elements', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create vision board for the authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WheelAreaSerializer(serializers.ModelSerializer):
    """Serializer for wheel areas"""

    class Meta:
        model = WheelArea
        fields = ['id', 'name', 'description', 'color', 'order', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class WheelAssessmentScoreSerializer(serializers.ModelSerializer):
    """Serializer for assessment scores"""
    area = WheelAreaSerializer(read_only=True)

    class Meta:
        model = WheelAssessmentScore
        fields = ['id', 'area', 'score']
        read_only_fields = ['id']


class WheelAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for wheel of life assessments"""
    average_score = serializers.SerializerMethodField()
    scores = WheelAssessmentScoreSerializer(many=True, read_only=True)
    scores_with_areas = serializers.SerializerMethodField()

    class Meta:
        model = WheelAssessment
        fields = [
            'id', 'title', 'notes', 'created_at', 'average_score', 'scores', 'scores_with_areas'
        ]
        read_only_fields = ['id', 'created_at', 'average_score', 'scores', 'scores_with_areas']

    def get_average_score(self, obj):
        """Get calculated average score"""
        return obj.get_average_score()

    def get_scores_with_areas(self, obj):
        """Get scores with area information"""
        return [
            {'area': score.area, 'score': score.score}
            for score in obj.scores.all().order_by('area__order')
        ]

    def create(self, validated_data):
        """Create assessment for the authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class GoalSerializer(serializers.ModelSerializer):
    """Serializer for goals"""
    wheel_area = WheelAreaSerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            'id', 'wheel_area', 'title', 'description',
            'target_date', 'progress', 'status', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue']

    def get_is_overdue(self, obj):
        """Check if goal is overdue"""
        return obj.is_overdue()

    def create(self, validated_data):
        """Create goal for the authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        """Create user (profile created by signal)"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']
        read_only_fields = ['id']
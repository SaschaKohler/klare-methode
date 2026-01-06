from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    UserProfileViewSet, VisionElementViewSet, VisionBoardViewSet,
    WheelAssessmentViewSet, GoalViewSet, AuthViewSet
)

# Create a router for the API
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'vision-elements', VisionElementViewSet, basename='visionelement')
router.register(r'vision-boards', VisionBoardViewSet, basename='visionboard')
router.register(r'wheel-assessments', WheelAssessmentViewSet, basename='wheelassessment')
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('vision-boards/', views.vision_board_list, name='vision_board_list'),
    path('vision-boards/create/', views.vision_board_create, name='vision_board_create'),
    path('vision-boards/<int:pk>/', views.vision_board_detail, name='vision_board_detail'),
    path('vision-boards/<int:pk>/edit/', views.vision_board_edit, name='vision_board_edit'),
    path('vision-elements/', views.vision_element_list, name='vision_element_list'),
    path('vision-elements/create/', views.vision_element_create, name='vision_element_create'),
    path('vision-elements/<int:pk>/', views.vision_element_detail, name='vision_element_detail'),
    path('vision-elements/<int:pk>/edit/', views.vision_element_edit, name='vision_element_edit'),
    path('vision-elements/<int:pk>/delete/', views.vision_element_delete, name='vision_element_delete'),
    path('wheel-assessments/create/', views.wheel_assessment_create, name='wheel_assessment_create'),
    path('wheel-assessments/<int:pk>/', views.wheel_assessment_detail, name='wheel_assessment_detail'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/', views.goal_detail, name='goal_detail'),
    path('api/', include(router.urls)),
]
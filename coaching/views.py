from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Goal,
    UserProfile,
    VisionBoard,
    VisionBoardElement,
    VisionBoardTemplate,
    VisionElement,
    VisionElementCategory,
    WheelArea,
    WheelAssessment,
    WheelAssessmentScore,
)
from .serializers import (
    GoalSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    VisionBoardElementSerializer,
    VisionBoardSerializer,
    VisionElementSerializer,
    WheelAssessmentSerializer,
)


class VisionBoardForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=VisionBoardTemplate.objects.filter(is_default=True),
        required=False,
        empty_label="Start from scratch",
        help_text="Choose a template to start with",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
        })
    )

    class Meta:
        model = VisionBoard
        fields = ["title", "description", "related_goal"]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Vision Board Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Describe your vision...'
            }),
            'related_goal': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Limit related_goal choices to user's goals
            self.fields["related_goal"].queryset = Goal.objects.filter(user=self.user)


class VisionElementForm(forms.ModelForm):
    class Meta:
        model = VisionElement
        fields = ["element_type", "title", "content", "image", "color", "font_size", "text_color", "categories"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Limit categories to user's categories
            self.fields["categories"].queryset = VisionElementCategory.objects.filter(user=self.user)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = VisionElementCategory
        fields = ["name", "color", "order"]


class WheelAssessmentForm(forms.ModelForm):
    class Meta:
        model = WheelAssessment
        fields = ["title", "notes"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Get user's wheel areas or create defaults
        if self.user:
            areas = WheelArea.objects.filter(user=self.user).order_by("order")
            if not areas.exists():
                # Create default areas for new users
                self._create_default_areas(self.user)
                areas = WheelArea.objects.filter(user=self.user).order_by("order")

            # Add dynamic score fields
            for area in areas:
                field_name = f"area_{area.id}"
                self.fields[field_name] = forms.IntegerField(
                    label=area.name,
                    min_value=1,
                    max_value=10,
                    help_text=area.description or f"Rate your satisfaction with {area.name} (1-10)",
                    widget=forms.Select(choices=[(i, i) for i in range(1, 11)]),
                )

                # Set initial value if editing
                if self.instance and self.instance.pk:
                    try:
                        score = WheelAssessmentScore.objects.get(
                            assessment=self.instance, area=area
                        )
                        self.initial[field_name] = score.score
                    except WheelAssessmentScore.DoesNotExist:
                        pass

    def _create_default_areas(self, user):
        """Create default wheel areas for a user"""
        defaults = [
            ("Career/Finance", "#4F46E5", "Professional and financial satisfaction"),
            ("Health/Wellness", "#10B981", "Physical and mental health"),
            ("Relationships", "#F59E0B", "Personal relationships and connections"),
            ("Personal Growth", "#EF4444", "Learning and self-development"),
            ("Fun/Recreation", "#8B5CF6", "Leisure and entertainment"),
            ("Home/Family", "#06B6D4", "Home environment and family life"),
            ("Contribution/Service", "#84CC16", "Community involvement and giving"),
            ("Spirituality", "#F97316", "Spiritual and life purpose"),
        ]

        for i, (name, color, description) in enumerate(defaults):
            WheelArea.objects.create(
                user=user, name=name, description=description, color=color, order=i, is_default=True
            )

    def save(self, commit=True):
        assessment = super().save(commit=False)
        if self.user:
            assessment.user = self.user
        if commit:
            assessment.save()

            # Save scores
            areas = WheelArea.objects.filter(user=self.user).order_by("order")
            for area in areas:
                field_name = f"area_{area.id}"
                score_value = self.cleaned_data.get(field_name)
                if score_value is not None:
                    WheelAssessmentScore.objects.update_or_create(
                        assessment=assessment, area=area, defaults={"score": score_value}
                    )

        return assessment


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "description", "wheel_area", "target_date", "status"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Limit wheel_area choices to user's areas
            self.fields["wheel_area"].queryset = WheelArea.objects.filter(user=self.user).order_by(
                "order"
            )


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for user profiles"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's profile"""
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Return the current user's profile"""
        return self.get_queryset().first()

    def list(self, request):
        """List profiles (only current user's)"""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Retrieve profile by pk (only current user's)"""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def update(self, request, pk=None, partial=True):
        """Update current user's profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """Partial update current user's profile"""
        return self.update(request, pk, partial=True)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class VisionElementViewSet(viewsets.ModelViewSet):
    """API endpoint for vision elements"""

    serializer_class = VisionElementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's vision elements"""
        return VisionElement.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create vision element for the authenticated user"""
        serializer.save(user=self.request.user)


class VisionBoardViewSet(viewsets.ModelViewSet):
    """API endpoint for vision boards"""

    serializer_class = VisionBoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's vision boards"""
        return VisionBoard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create vision board for the authenticated user"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """Duplicate a vision board"""
        board = self.get_object()
        board.pk = None
        board.title = f"{board.title} (Copy)"
        board.save()
        serializer = self.get_serializer(board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def update_layout(self, request, pk=None):
        """Update board element positions"""
        board = self.get_object()
        layout_data = request.data.get("elements", [])

        # Validate that all elements belong to the current user
        element_ids = [
            element_data.get("element_id")
            for element_data in layout_data
            if element_data.get("element_id")
        ]
        if element_ids:
            user_elements = set(
                VisionElement.objects.filter(user=request.user, id__in=element_ids).values_list(
                    "id", flat=True
                )
            )

            invalid_elements = set(element_ids) - user_elements
            if invalid_elements:
                return Response(
                    {
                        "detail": f"Elements {list(invalid_elements)} do not exist or do not belong to you"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Clear existing elements
        board.vision_elements.clear()

        # Create new elements
        for element_data in layout_data:
            board.vision_elements.add(
                element_data["element_id"],
                through_defaults={
                    "x_position": element_data.get("x", 0),
                    "y_position": element_data.get("y", 0),
                    "width": element_data.get("width", 200),
                    "height": element_data.get("height", 150),
                    "z_index": element_data.get("z_index", 0),
                    "rotation": element_data.get("rotation", 0),
                },
            )

        serializer = self.get_serializer(board)
        return Response(serializer.data)


class WheelAssessmentViewSet(viewsets.ModelViewSet):
    """API endpoint for wheel of life assessments"""

    serializer_class = WheelAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's assessments"""
        return WheelAssessment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create assessment for the authenticated user"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Get the most recent assessment"""
        assessment = self.get_queryset().first()
        if assessment:
            serializer = self.get_serializer(assessment)
            return Response(serializer.data)
        return Response({"detail": "No assessments found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get assessment statistics"""
        assessments = self.get_queryset()
        if not assessments:
            return Response({"detail": "No assessments found"}, status=status.HTTP_404_NOT_FOUND)

        latest = assessments.first()
        stats = {
            "total_assessments": assessments.count(),
            "latest_average": latest.get_average_score(),
            "areas": latest.get_scores_dict(),
            "improvement_areas": [
                area for area, score in latest.get_scores_dict().items() if score < 7
            ],
        }
        return Response(stats)


class GoalViewSet(viewsets.ModelViewSet):
    """API endpoint for goals"""

    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's goals"""
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create goal for the authenticated user"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get only active goals"""
        goals = self.get_queryset().filter(status="active")
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_area(self, request):
        """Get goals grouped by life area"""
        goals = self.get_queryset()
        areas = {}

        for goal in goals:
            area_name = goal.wheel_area.name
            if area_name not in areas:
                areas[area_name] = []
            areas[area_name].append(GoalSerializer(goal).data)

        return Response(areas)

    @action(detail=True, methods=["post"])
    def update_progress(self, request, pk=None):
        """Update goal progress"""
        goal = self.get_object()
        progress = request.data.get("progress")

        if progress is not None:
            try:
                progress = int(progress)
                if 0 <= progress <= 100:
                    goal.progress = progress
                    if progress == 100:
                        goal.status = "completed"
                    goal.save()
                    serializer = self.get_serializer(goal)
                    return Response(serializer.data)
                else:
                    return Response(
                        {"detail": "Progress must be between 0 and 100"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Invalid progress value"}, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"detail": "Progress field is required"}, status=status.HTTP_400_BAD_REQUEST
        )


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""

    @action(detail=False, methods=["post"], permission_classes=[])
    def login(self, request):
        """Login a user"""
        from django.contrib.auth import authenticate, login

        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["post"], permission_classes=[])
    def register(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"detail": "User registered successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], permission_classes=[])
    def me(self, request):
        """Get current user info"""
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)


# Frontend Views
@login_required
def dashboard(request):
    """Dashboard view"""
    user = request.user
    vision_boards_count = VisionBoard.objects.filter(user=user).count()
    assessments_count = WheelAssessment.objects.filter(user=user).count()
    active_goals_count = Goal.objects.filter(user=user, status="active").count()

    recent_boards = VisionBoard.objects.filter(user=user).order_by("-created_at")[:5]
    latest_assessment = WheelAssessment.objects.filter(user=user).order_by("-created_at").first()
    active_goals = Goal.objects.filter(user=user, status="active").order_by("-created_at")[:5]

    context = {
        "vision_boards_count": vision_boards_count,
        "assessments_count": assessments_count,
        "active_goals_count": active_goals_count,
        "recent_boards": recent_boards,
        "latest_assessment": latest_assessment,
        "active_goals": active_goals,
    }

    if latest_assessment:
        context["assessment_width_percentage"] = latest_assessment.get_average_score() * 10
    return render(request, "coaching/dashboard.html", context)


@login_required
def vision_board_list(request):
    """List user's vision boards"""
    boards = VisionBoard.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "coaching/vision_board_list.html", {"boards": boards})


@login_required
def vision_board_create(request):
    """Create a new vision board"""
    if request.method == "POST":
        form = VisionBoardForm(request.POST, user=request.user)
        if form.is_valid():
            board = form.save(commit=False)
            board.user = request.user
            board.save()

            # If a template was selected, apply it
            template = form.cleaned_data.get('template')
            if template:
                # Apply template elements
                template_elements = template.template_data.get('elements', [])
                board.elements = template_elements
                board.save()

            messages.success(request, "Vision board created successfully!")
            return redirect("vision_board_detail", pk=board.pk)
    else:
        form = VisionBoardForm(user=request.user)
    return render(request, "coaching/vision_board_form.html", {"form": form})


@login_required
def vision_board_detail(request, pk):
    """View vision board details"""
    board = get_object_or_404(VisionBoard, pk=pk, user=request.user)

    # Get element details for rendering
    elements_data = []
    for element_data in board.elements:
        element_id = element_data.get("element_id")
        if element_id and str(element_id).isdigit():
            try:
                element = VisionElement.objects.get(id=int(element_id), user=request.user)
                elements_data.append({"layout": element_data, "element": element})
            except VisionElement.DoesNotExist:
                # Fallback to layout data only
                elements_data.append({"layout": element_data, "element": None})
        else:
            elements_data.append({"layout": element_data, "element": None})

    return render(
        request,
        "coaching/vision_board_detail.html",
        {"board": board, "elements_data": elements_data},
    )


@login_required
def wheel_assessment_create(request):
    """Create a new wheel assessment"""
    if request.method == "POST":
        form = WheelAssessmentForm(request.POST, user=request.user)
        if form.is_valid():
            assessment = form.save()
            messages.success(request, "Assessment completed successfully!")
            return redirect("wheel_assessment_detail", pk=assessment.pk)
    else:
        form = WheelAssessmentForm(user=request.user)
    return render(request, "coaching/wheel_assessment_form.html", {"form": form})


@login_required
def wheel_assessment_detail(request, pk):
    """View wheel assessment details"""
    assessment = get_object_or_404(WheelAssessment, pk=pk, user=request.user)
    return render(request, "coaching/wheel_assessment_detail.html", {"assessment": assessment})


@login_required
def goal_create(request):
    """Create a new goal"""
    if request.method == "POST":
        form = GoalForm(request.POST, user=request.user)
        if form.is_valid():
            goal = form.save()
            messages.success(request, "Goal created successfully!")
            return redirect("goal_detail", pk=goal.pk)
    else:
        form = GoalForm(user=request.user)
    return render(request, "coaching/goal_form.html", {"form": form})


@login_required
def goal_detail(request, pk):
    """View goal details"""
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    # Get related vision boards
    related_boards = VisionBoard.objects.filter(related_goal=goal)
    return render(request, "coaching/goal_detail.html", {"goal": goal, "related_boards": related_boards})


@login_required
def vision_board_edit(request, pk):
    """Edit vision board with interactive editor"""
    board = get_object_or_404(VisionBoard, pk=pk, user=request.user)

    if request.method == "POST":
        # Handle layout save
        import json

        layout_data = json.loads(request.POST.get("elements", "[]"))

        # Save layout data to JSON field (fallback until migrations run)
        board.elements = layout_data
        board.save()

        messages.success(request, "Vision board saved successfully!")
        return redirect("vision_board_detail", pk=board.pk)

    # Load user elements for adding to the board
    user_elements = VisionElement.objects.filter(user=request.user)
    return render(
        request, "coaching/vision_board_edit.html", {"board": board, "user_elements": user_elements}
    )


@login_required
def vision_element_list(request):
    """List user's vision elements"""
    elements = VisionElement.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "coaching/vision_element_list.html", {"elements": elements})


@login_required
def vision_element_detail(request, pk):
    """View vision element details"""
    element = get_object_or_404(VisionElement, pk=pk, user=request.user)
    return render(request, "coaching/vision_element_detail.html", {"element": element})


@login_required
def vision_element_edit(request, pk):
    """Edit a vision element"""
    element = get_object_or_404(VisionElement, pk=pk, user=request.user)
    if request.method == "POST":
        form = VisionElementForm(request.POST, request.FILES, instance=element, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vision element updated successfully!")
            return redirect("vision_element_detail", pk=element.pk)
    else:
        form = VisionElementForm(instance=element, user=request.user)
    return render(request, "coaching/vision_element_form.html", {"form": form, "element": element})


@login_required
def vision_element_delete(request, pk):
    """Delete a vision element"""
    element = get_object_or_404(VisionElement, pk=pk, user=request.user)
    if request.method == "POST":
        element.delete()
        messages.success(request, "Vision element deleted successfully!")
        return redirect("vision_element_list")
    return render(request, "coaching/vision_element_confirm_delete.html", {"element": element})


@login_required
def vision_element_create(request):
    """Create a new vision element"""
    if request.method == "POST":
        form = VisionElementForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            element = form.save(commit=False)
            element.user = request.user
            element.save()
            messages.success(request, "Vision element created successfully!")
            return redirect("vision_element_list")
    else:
        form = VisionElementForm(user=request.user)
    return render(request, "coaching/vision_element_form.html", {"form": form})


# Category Management Views
@login_required
def category_list(request):
    """List user's categories"""
    categories = VisionElementCategory.objects.filter(user=request.user).order_by("order", "name")
    return render(request, "coaching/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    """Create a new category"""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Category created successfully!")
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "coaching/category_form.html", {"form": form})


@login_required
def category_edit(request, pk):
    """Edit a category"""
    category = get_object_or_404(VisionElementCategory, pk=pk, user=request.user)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "coaching/category_form.html", {"form": form, "category": category})


@login_required
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(VisionElementCategory, pk=pk, user=request.user)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect("category_list")
    return render(request, "coaching/category_confirm_delete.html", {"category": category})


# Authentication Views
def register_view(request):
    """User registration view"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard")
    else:
        form = UserRegistrationForm()
    return render(request, "coaching/register.html", {"form": form})


def login_view(request):
    """User login view"""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "coaching/login.html", {"form": form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")

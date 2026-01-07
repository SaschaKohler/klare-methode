from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class UserProfile(models.Model):
    """Extended user profile for coaching app"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, help_text="Short bio or personal statement")
    coaching_focus = models.CharField(
        max_length=100, blank=True, help_text="Main area of personal development focus"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s profile"


class VisionElementCategory(models.Model):
    """Categories for organizing vision elements"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vision_element_categories"
    )
    name = models.CharField(max_length=100, help_text="Category name")
    color = models.CharField(max_length=7, default="#4F46E5", help_text="Category color (hex)")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ["user", "name"]
        verbose_name = "Vision Element Category"
        verbose_name_plural = "Vision Element Categories"

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class VisionElement(models.Model):
    """User's personal collection of visual elements for vision boards"""

    ELEMENT_TYPES = [
        ("text", "Text Snippet"),
        ("image", "Image"),
        ("quote", "Quote"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vision_elements")
    element_type = models.CharField(max_length=10, choices=ELEMENT_TYPES, default="text")
    title = models.CharField(max_length=200, blank=True, help_text="Optional title for the element")
    content = models.TextField(help_text="Text content or image alt text")
    image = models.ImageField(upload_to="vision_elements/", blank=True, null=True)
    color = models.CharField(max_length=7, default="#ffffff", help_text="Background color (hex)")
    font_size = models.IntegerField(default=16, help_text="Font size in pixels")
    text_color = models.CharField(max_length=7, default="#000000", help_text="Text color (hex)")
    categories = models.ManyToManyField(
        VisionElementCategory,
        related_name="vision_elements",
        blank=True,
        help_text="Categories this element belongs to",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Vision Element"
        verbose_name_plural = "Vision Elements"

    def __str__(self):
        return f"{self.user.username} - {self.title or self.content[:50]}"


class VisionBoardElement(models.Model):
    """Positions elements on vision boards"""

    vision_board = models.ForeignKey(
        "VisionBoard", on_delete=models.CASCADE, related_name="board_elements"
    )
    vision_element = models.ForeignKey(VisionElement, on_delete=models.CASCADE)
    x_position = models.IntegerField(default=0, help_text="X coordinate on board")
    y_position = models.IntegerField(default=0, help_text="Y coordinate on board")
    width = models.IntegerField(default=200, help_text="Element width in pixels")
    height = models.IntegerField(default=150, help_text="Element height in pixels")
    z_index = models.IntegerField(default=0, help_text="Stacking order")
    rotation = models.IntegerField(default=0, help_text="Rotation in degrees")

    class Meta:
        unique_together = ["vision_board", "vision_element"]


class VisionBoardTemplate(models.Model):
    """Templates for creating vision boards"""

    name = models.CharField(max_length=200, help_text="Template name")
    description = models.TextField(blank=True, help_text="Template description")
    template_data = models.JSONField(
        default=dict, help_text="Template structure with default elements and layout"
    )
    is_default = models.BooleanField(default=False, help_text="System default template")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vision Board Template"
        verbose_name_plural = "Vision Board Templates"

    def __str__(self):
        return self.name


class VisionBoard(models.Model):
    """Vision board for visual goal setting"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vision_boards")
    title = models.CharField(max_length=200, help_text="Name of the vision board")
    description = models.TextField(blank=True, help_text="Optional description")
    elements = models.JSONField(
        default=list, help_text="List of board elements with positions and content"
    )
    # New M2M field for scrapbook functionality
    vision_elements = models.ManyToManyField(
        VisionElement,
        through=VisionBoardElement,
        related_name="boards",
        blank=True,
        help_text="Elements placed on this board",
    )
    related_goal = models.ForeignKey(
        "Goal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vision_boards",
        help_text="Goal this vision board is related to",
    )
    is_active = models.BooleanField(default=True, help_text="Is this board currently active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Vision Board"
        verbose_name_plural = "Vision Boards"

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class WheelArea(models.Model):
    """Customizable life areas for wheel assessments"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wheel_areas")
    name = models.CharField(max_length=100, help_text="Area name (e.g., Career, Health)")
    description = models.TextField(blank=True, help_text="Optional description")
    color = models.CharField(max_length=7, default="#4F46E5", help_text="Hex color code")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_default = models.BooleanField(default=False, help_text="System default area")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ["user", "name"]
        verbose_name = "Wheel Area"
        verbose_name_plural = "Wheel Areas"

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class WheelAssessmentScore(models.Model):
    """Individual scores for each area in an assessment"""

    assessment = models.ForeignKey(
        "WheelAssessment", on_delete=models.CASCADE, related_name="scores"
    )
    area = models.ForeignKey("WheelArea", on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Satisfaction score (1-10)",
    )

    class Meta:
        unique_together = ["assessment", "area"]

    def __str__(self):
        return f"{self.assessment.title} - {self.area.name}: {self.score}"


class WheelAssessment(models.Model):
    """Wheel of Life assessment with customizable life areas"""

    WHEEL_AREAS = [
        ("career", "Career/Finance"),
        ("health", "Health/Wellness"),
        ("relationships", "Relationships"),
        ("personal_growth", "Personal Growth"),
        ("fun_recreation", "Fun/Recreation"),
        ("home_family", "Home/Family"),
        ("contribution", "Contribution/Service"),
        ("spirituality", "Spirituality"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wheel_assessments")
    title = models.CharField(
        max_length=200, default="Life Assessment", help_text="Name for this assessment"
    )

    notes = models.TextField(blank=True, help_text="Additional notes or reflections")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at.date()})"

    def get_average_score(self):
        """Calculate average score across all life areas"""
        scores = self.scores.all()
        if not scores:
            return 0
        total = sum(score.score for score in scores)
        return round(total / len(scores), 1)

    def get_scores_dict(self):
        """Return scores as dictionary for easy access"""
        scores_dict = {}
        for score in self.scores.all():
            scores_dict[score.area.name.lower().replace(" ", "_")] = score.score
        return scores_dict

    def get_scores_with_areas(self):
        """Return scores with area information for templates"""
        return [
            {"area": score.area, "score": score.score}
            for score in self.scores.all().order_by("area__order")
        ]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Wheel Assessment"
        verbose_name_plural = "Wheel Assessments"


class Goal(models.Model):
    """Personal goals linked to life areas"""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    wheel_area = models.ForeignKey(
        WheelArea, on_delete=models.CASCADE, help_text="Life area this goal belongs to"
    )
    title = models.CharField(max_length=200, help_text="Goal title")
    description = models.TextField(blank=True, help_text="Detailed description")
    target_date = models.DateField(blank=True, null=True, help_text="Target completion date")
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", help_text="Current goal status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def is_overdue(self):
        """Check if goal is overdue"""
        if self.target_date and self.status == "active":
            from django.utils import timezone

            return self.target_date < timezone.now().date()
        return False

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Goal"
        verbose_name_plural = "Goals"

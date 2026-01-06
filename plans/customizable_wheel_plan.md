# Plan: Make Wheel of Life Assessment Customizable with Pie Chart Visualization

## Current State Analysis
- WheelAssessment model has 8 fixed life areas with hardcoded fields
- Basic pie chart visualization exists in `wheel_of_life.html` template
- Areas are predefined: Career, Health, Relationships, Personal Growth, Fun/Recreation, Home/Family, Contribution, Spirituality
- Colors are auto-generated based on score using HSL

## Proposed Architecture

### New Models

#### WheelArea Model
```python
class WheelArea(models.Model):
    """Customizable life areas for wheel assessments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wheel_areas')
    name = models.CharField(max_length=100, help_text="Area name (e.g., Career, Health)")
    description = models.TextField(blank=True, help_text="Optional description")
    color = models.CharField(max_length=7, default='#4F46E5', help_text='Hex color code')
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_default = models.BooleanField(default=False, help_text="System default area")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['user', 'name']
```

#### WheelAssessmentScore Model
```python
class WheelAssessmentScore(models.Model):
    """Individual scores for each area in an assessment"""
    assessment = models.ForeignKey('WheelAssessment', on_delete=models.CASCADE, related_name='scores')
    area = models.ForeignKey('WheelArea', on_delete=models.CASCADE)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Satisfaction score (1-10)"
    )

    class Meta:
        unique_together = ['assessment', 'area']
```

#### Updated WheelAssessment Model
- Remove fixed area fields (career, health, etc.)
- Keep title, notes, created_at
- Add relationship to WheelAssessmentScore

### Migration Strategy
1. Create new models with migration
2. Data migration to create default WheelArea instances for all users
3. Data migration to convert existing WheelAssessment fixed fields to WheelAssessmentScore records
4. Remove old fields from WheelAssessment model

### Default Areas (created automatically for new users)
- Career/Finance (#4F46E5 - Indigo)
- Health/Wellness (#10B981 - Emerald)
- Relationships (#F59E0B - Amber)
- Personal Growth (#EF4444 - Red)
- Fun/Recreation (#8B5CF6 - Violet)
- Home/Family (#06B6D4 - Cyan)
- Contribution/Service (#84CC16 - Lime)
- Spirituality (#F97316 - Orange)

## Implementation Steps

### 1. Database Changes
- Create WheelArea and WheelAssessmentScore models
- Migration to populate default areas for existing users
- Migration to convert existing assessment data
- Remove old fields from WheelAssessment

### 2. Forms and Views Updates
- Update WheelAssessmentForm to dynamically generate fields based on user's areas
- Modify wheel_assessment_create view to handle dynamic scoring
- Update serializers for API compatibility

### 3. Template Updates
- Modify wheel_assessment_form.html to show dynamic areas
- Update wheel_assessment_detail.html for customizable display
- Enhance wheel_of_life.html pie chart to use user-defined colors
- Add area management interface

### 4. Visualization Improvements
- Update Canvas drawing to use area.color instead of HSL calculation
- Ensure proper color contrast for labels
- Add hover effects and better interactivity

### 5. User Interface for Area Management
- Create views for listing/creating/editing wheel areas
- Add color picker for area customization
- Allow reordering of areas

## Benefits
- Users can customize life areas to match their personal context
- Visual consistency with user-defined colors
- Maintains backward compatibility with existing data
- Extensible for future enhancements

## Technical Considerations
- Need to handle users with no custom areas (use defaults)
- Ensure migration doesn't lose existing assessment data
- Update all related code (goals, statistics, etc.)
- Consider performance with dynamic form generation

## Testing Requirements
- Verify migration preserves all existing data
- Test form generation with different numbers of areas
- Validate pie chart rendering with custom colors
- Check API endpoints still work correctly
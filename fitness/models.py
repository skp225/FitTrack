from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    date_of_birth = models.DateField(null=True, blank=True)
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    profile_picture = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def get_bmi(self):
        if self.height and self.weight:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 2)
        return None

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    muscle_group = models.CharField(
        max_length=50,
        choices=[
            ('chest', 'Chest'),
            ('back', 'Back'),
            ('legs', 'Legs'),
            ('shoulders', 'Shoulders'),
            ('arms', 'Arms'),
            ('core', 'Core'),
            ('full_body', 'Full Body'),
            ('cardio', 'Cardio'),
        ]
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    equipment_required = models.CharField(max_length=100, blank=True)
    demonstration_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workouts")
    title = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    duration = models.IntegerField(help_text="Duration in minutes")
    notes = models.TextField(blank=True)
    calories_burned = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.date}"

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=10)
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds")
    distance = models.FloatField(null=True, blank=True, help_text="Distance in km")
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"

class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_plans")
    title = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    duration_weeks = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class PlanDay(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="days")
    day_number = models.IntegerField()
    focus = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['day_number']
    
    def __str__(self):
        return f"Day {self.day_number}: {self.focus}"

class PlanExercise(models.Model):
    plan_day = models.ForeignKey(PlanDay, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(default=10)
    rest_time = models.IntegerField(default=60, help_text="Rest time in seconds")
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    goal_type = models.CharField(
        max_length=20,
        choices=[
            ('weight_loss', 'Weight Loss'),
            ('muscle_gain', 'Muscle Gain'),
            ('endurance', 'Endurance'),
            ('strength', 'Strength'),
            ('flexibility', 'Flexibility'),
            ('habit', 'Habit Formation'),
            ('custom', 'Custom'),
        ]
    )
    target_value = models.FloatField(null=True, blank=True)
    target_unit = models.CharField(max_length=20, blank=True)
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def days_remaining(self):
        if self.is_completed:
            return 0
        today = timezone.now().date()
        return (self.target_date - today).days
    
    def progress_percentage(self):
        if self.is_completed:
            return 100
        
        # Get all progress entries ordered by date
        progress_entries = list(self.progress_entries.all().order_by('date', 'id'))
        
        # Check if we have progress entries and a target value
        if not progress_entries or not self.target_value:
            return 0
        
        # Get the first and latest progress entries
        first_progress = progress_entries[0]
        latest_progress = progress_entries[-1]
        
        # For weight loss goals, calculate progress differently
        if self.goal_type == 'weight_loss':
            # Calculate progress as percentage of weight lost
            starting_weight = first_progress.value
            current_weight = latest_progress.value
            target_weight = self.target_value
            
            # Debug: Print values to server console
            print(f"Weight Loss Goal Progress Calculation:")
            print(f"Progress Entries: {[(entry.date, entry.value) for entry in progress_entries]}")
            print(f"First Progress Entry: {first_progress.date} - {first_progress.value}")
            print(f"Latest Progress Entry: {latest_progress.date} - {latest_progress.value}")
            print(f"Starting Weight: {starting_weight}")
            print(f"Current Weight: {current_weight}")
            print(f"Target Weight: {target_weight}")
            
            # Avoid division by zero
            if starting_weight == target_weight:
                return 100 if current_weight <= target_weight else 0
            
            # Calculate progress percentage
            weight_lost = starting_weight - current_weight
            weight_to_lose = starting_weight - target_weight
            
            # Debug: Print more values
            print(f"Weight Lost: {weight_lost}")
            print(f"Weight to Lose: {weight_to_lose}")
            
            # Ensure we don't divide by zero
            if weight_to_lose == 0:
                return 0
                
            progress = (weight_lost / weight_to_lose) * 100
            
            # Ensure progress is between 0 and 100
            progress_percentage = min(100, max(0, int(progress)))
            
            # Debug: Print final values
            print(f"Progress: {progress}%")
            print(f"Progress Percentage: {progress_percentage}%")
            
            return progress_percentage
        else:
            # For other goals, higher values mean more progress
            return min(100, int((latest_progress.value / self.target_value) * 100))

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_entries")
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="progress_entries", null=True, blank=True)
    date = models.DateField(default=timezone.now)
    metric = models.CharField(max_length=50)
    value = models.FloatField()
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Progress Entries"
    
    def __str__(self):
        return f"{self.metric}: {self.value} on {self.date}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

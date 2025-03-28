from django.contrib import admin
from .models import (
    UserProfile, Exercise, Workout, WorkoutExercise, 
    WorkoutPlan, PlanDay, PlanExercise, Goal, Progress, Notification
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fitness_level', 'get_age', 'get_bmi')
    search_fields = ('user__username', 'user__email')

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'muscle_group', 'difficulty')
    list_filter = ('muscle_group', 'difficulty')
    search_fields = ('name', 'description')

class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'duration', 'calories_burned')
    list_filter = ('date', 'user')
    search_fields = ('title', 'notes', 'user__username')
    inlines = [WorkoutExerciseInline]

@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'workout', 'sets', 'reps', 'weight')
    list_filter = ('exercise__muscle_group',)

class PlanDayInline(admin.TabularInline):
    model = PlanDay
    extra = 1

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'difficulty', 'duration_weeks', 'is_public')
    list_filter = ('difficulty', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    inlines = [PlanDayInline]

class PlanExerciseInline(admin.TabularInline):
    model = PlanExercise
    extra = 1

@admin.register(PlanDay)
class PlanDayAdmin(admin.ModelAdmin):
    list_display = ('workout_plan', 'day_number', 'focus')
    list_filter = ('workout_plan',)
    inlines = [PlanExerciseInline]

@admin.register(PlanExercise)
class PlanExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'plan_day', 'sets', 'reps')
    list_filter = ('exercise__muscle_group',)

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'goal_type', 'start_date', 'target_date', 'is_completed')
    list_filter = ('goal_type', 'is_completed', 'start_date', 'target_date')
    search_fields = ('title', 'description', 'user__username')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'date', 'metric', 'value')
    list_filter = ('date', 'metric')
    search_fields = ('notes', 'user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')

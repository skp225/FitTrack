from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    UserProfile, Exercise, Workout, WorkoutExercise, 
    WorkoutPlan, PlanDay, PlanExercise, Goal, Progress, Notification
)

def index(request):
    """Home page view"""
    if request.user.is_authenticated:
        # Get user's recent workouts
        recent_workouts = Workout.objects.filter(user=request.user).order_by('-date')[:5]
        
        # Get user's active goals
        active_goals = Goal.objects.filter(user=request.user, is_completed=False).order_by('target_date')
        
        # Get user's workout plans
        workout_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')[:3]
        
        # Get user's progress data for charts
        progress_data = {}
        for goal in active_goals:
            progress_entries = Progress.objects.filter(goal=goal).order_by('date')
            if progress_entries.exists():
                progress_data[goal.id] = {
                    'title': goal.title,
                    'labels': [entry.date.strftime('%Y-%m-%d') for entry in progress_entries],
                    'values': [entry.value for entry in progress_entries],
                    'target': goal.target_value,
                }
        
        context = {
            'recent_workouts': recent_workouts,
            'active_goals': active_goals,
            'workout_plans': workout_plans,
            'progress_data': json.dumps(progress_data),
        }
        return render(request, 'fitness/dashboard.html', context)
    else:
        return render(request, 'fitness/index.html')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('profile_setup')
    else:
        form = UserCreationForm()
    return render(request, 'fitness/register.html', {'form': form})

@login_required
def profile_setup(request):
    """Initial profile setup after registration"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update profile with form data
        profile.height = request.POST.get('height')
        profile.weight = request.POST.get('weight')
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.fitness_level = request.POST.get('fitness_level')
        profile.save()
        
        # Create initial goals based on user preferences
        goal_types = request.POST.getlist('goal_types')
        for goal_type in goal_types:
            if goal_type == 'weight_loss':
                target_weight = float(request.POST.get('target_weight', 0))
                if target_weight > 0:
                    Goal.objects.create(
                        user=request.user,
                        title="Weight Loss Goal",
                        description=f"Reach target weight of {target_weight} kg",
                        goal_type='weight_loss',
                        target_value=target_weight,
                        target_unit='kg',
                        target_date=timezone.now().date() + timedelta(days=90)
                    )
            elif goal_type == 'muscle_gain':
                Goal.objects.create(
                    user=request.user,
                    title="Muscle Gain Goal",
                    description="Increase strength and muscle mass",
                    goal_type='muscle_gain',
                    target_date=timezone.now().date() + timedelta(days=90)
                )
            elif goal_type == 'endurance':
                Goal.objects.create(
                    user=request.user,
                    title="Endurance Goal",
                    description="Improve cardiovascular fitness",
                    goal_type='endurance',
                    target_date=timezone.now().date() + timedelta(days=60)
                )
        
        # Suggest workout plans based on fitness level
        if profile.fitness_level:
            public_plans = WorkoutPlan.objects.filter(
                is_public=True, 
                difficulty=profile.fitness_level
            )[:3]
            
            # Create notification about suggested plans
            if public_plans.exists():
                Notification.objects.create(
                    user=request.user,
                    title="Workout Plans Suggested",
                    message="We've suggested some workout plans based on your fitness level. Check them out!"
                )
        
        return redirect('dashboard')
    
    return render(request, 'fitness/profile_setup.html', {'profile': profile})

@login_required
def dashboard(request):
    """User dashboard view"""
    # Get user's recent workouts
    recent_workouts = Workout.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Get user's active goals
    active_goals = Goal.objects.filter(user=request.user, is_completed=False).order_by('target_date')
    
    # Get user's workout plans
    workout_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')[:3]
    
    # Get user's progress data for charts
    progress_data = {}
    for goal in active_goals:
        progress_entries = Progress.objects.filter(goal=goal).order_by('date')
        if progress_entries.exists():
            progress_data[goal.id] = {
                'title': goal.title,
                'labels': [entry.date.strftime('%Y-%m-%d') for entry in progress_entries],
                'values': [entry.value for entry in progress_entries],
                'target': goal.target_value,
            }
    
    # Get unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    
    context = {
        'recent_workouts': recent_workouts,
        'active_goals': active_goals,
        'workout_plans': workout_plans,
        'progress_data': json.dumps(progress_data),
        'notifications': notifications,
    }
    return render(request, 'fitness/dashboard.html', context)

@login_required
def profile(request):
    """User profile view and edit"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update profile with form data
        profile.height = request.POST.get('height')
        profile.weight = request.POST.get('weight')
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.fitness_level = request.POST.get('fitness_level')
        profile.save()
        
        # Record weight progress if changed
        if 'weight' in request.POST and request.POST.get('weight'):
            weight = float(request.POST.get('weight'))
            # Find weight loss goals
            weight_goals = Goal.objects.filter(
                user=request.user,
                goal_type='weight_loss',
                is_completed=False
            )
            
            # Create progress entry
            progress = Progress.objects.create(
                user=request.user,
                metric='weight',
                value=weight,
                date=timezone.now().date()
            )
            
            # Link to first weight goal if exists
            if weight_goals.exists():
                progress.goal = weight_goals.first()
                progress.save()
                
                # Check if goal is completed
                if weight_goals.first().target_value and weight <= weight_goals.first().target_value:
                    weight_goals.first().is_completed = True
                    weight_goals.first().completed_date = timezone.now().date()
                    weight_goals.first().save()
                    
                    # Create notification
                    Notification.objects.create(
                        user=request.user,
                        title="Goal Achieved!",
                        message=f"Congratulations! You've reached your weight goal of {weight_goals.first().target_value} kg."
                    )
        
        return redirect('profile')
    
    # Get weight progress history
    weight_history = Progress.objects.filter(
        user=request.user,
        metric='weight'
    ).order_by('date')
    
    context = {
        'profile': profile,
        'weight_history': weight_history,
    }
    return render(request, 'fitness/profile.html', context)

@login_required
def exercises(request):
    """View all exercises"""
    exercises = Exercise.objects.all()
    
    # Filter by muscle group if specified
    muscle_group = request.GET.get('muscle_group')
    if muscle_group:
        exercises = exercises.filter(muscle_group=muscle_group)
    
    # Filter by difficulty if specified
    difficulty = request.GET.get('difficulty')
    if difficulty:
        exercises = exercises.filter(difficulty=difficulty)
    
    context = {
        'exercises': exercises,
        'muscle_groups': dict(Exercise._meta.get_field('muscle_group').choices),
        'difficulties': dict(Exercise._meta.get_field('difficulty').choices),
    }
    return render(request, 'fitness/exercises.html', context)

@login_required
def exercise_detail(request, exercise_id):
    """View exercise details"""
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    context = {
        'exercise': exercise,
    }
    return render(request, 'fitness/exercise_detail.html', context)

@login_required
def workouts(request):
    """View user's workouts"""
    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    
    context = {
        'workouts': workouts,
    }
    return render(request, 'fitness/workouts.html', context)

@login_required
def workout_detail(request, workout_id):
    """View workout details"""
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    exercises = WorkoutExercise.objects.filter(workout=workout)
    
    context = {
        'workout': workout,
        'exercises': exercises,
    }
    return render(request, 'fitness/workout_detail.html', context)

@login_required
def create_workout(request):
    """Create a new workout"""
    if request.method == 'POST':
        # Create workout
        workout = Workout.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            date=request.POST.get('date') or timezone.now().date(),
            duration=request.POST.get('duration'),
            notes=request.POST.get('notes', ''),
            calories_burned=request.POST.get('calories_burned')
        )
        
        # Add exercises to workout
        exercise_ids = request.POST.getlist('exercise_id')
        sets_list = request.POST.getlist('sets')
        reps_list = request.POST.getlist('reps')
        weight_list = request.POST.getlist('weight')
        
        for i in range(len(exercise_ids)):
            if i < len(sets_list) and i < len(reps_list):
                exercise = Exercise.objects.get(id=exercise_ids[i])
                sets = sets_list[i]
                reps = reps_list[i]
                weight = weight_list[i] if i < len(weight_list) and weight_list[i] else None
                
                WorkoutExercise.objects.create(
                    workout=workout,
                    exercise=exercise,
                    sets=sets,
                    reps=reps,
                    weight=weight
                )
        
        return redirect('workout_detail', workout_id=workout.id)
    
    # Get all exercises for the form
    exercises = Exercise.objects.all()
    
    context = {
        'exercises': exercises,
    }
    return render(request, 'fitness/create_workout.html', context)

@login_required
def goals(request):
    """View user's goals"""
    active_goals = Goal.objects.filter(user=request.user, is_completed=False).order_by('target_date')
    completed_goals = Goal.objects.filter(user=request.user, is_completed=True).order_by('-completed_date')
    
    context = {
        'active_goals': active_goals,
        'completed_goals': completed_goals,
    }
    return render(request, 'fitness/goals.html', context)

@login_required
def goal_detail(request, goal_id):
    """View goal details"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    progress_entries = Progress.objects.filter(goal=goal).order_by('date')
    
    context = {
        'goal': goal,
        'progress_entries': progress_entries,
    }
    return render(request, 'fitness/goal_detail.html', context)

@login_required
def create_goal(request):
    """Create a new goal"""
    if request.method == 'POST':
        goal = Goal.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            goal_type=request.POST.get('goal_type'),
            target_value=request.POST.get('target_value') or None,
            target_unit=request.POST.get('target_unit', ''),
            start_date=request.POST.get('start_date') or timezone.now().date(),
            target_date=request.POST.get('target_date')
        )
        
        # Create initial progress entry if value provided
        if request.POST.get('initial_value'):
            Progress.objects.create(
                user=request.user,
                goal=goal,
                metric=goal.goal_type,
                value=request.POST.get('initial_value'),
                date=timezone.now().date()
            )
        
        return redirect('goal_detail', goal_id=goal.id)
    
    context = {
        'goal_types': dict(Goal._meta.get_field('goal_type').choices),
    }
    return render(request, 'fitness/create_goal.html', context)

@login_required
def add_progress(request, goal_id):
    """Add progress to a goal"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        value = request.POST.get('value')
        notes = request.POST.get('notes', '')
        date = request.POST.get('date') or timezone.now().date()
        
        progress = Progress.objects.create(
            user=request.user,
            goal=goal,
            metric=goal.goal_type,
            value=value,
            notes=notes,
            date=date
        )
        
        # Check if goal is completed
        if goal.target_value:
            if (goal.goal_type == 'weight_loss' and float(value) <= goal.target_value) or \
               (goal.goal_type != 'weight_loss' and float(value) >= goal.target_value):
                goal.is_completed = True
                goal.completed_date = timezone.now().date()
                goal.save()
                
                # Create notification
                Notification.objects.create(
                    user=request.user,
                    title="Goal Achieved!",
                    message=f"Congratulations! You've reached your goal: {goal.title}"
                )
        
        return redirect('goal_detail', goal_id=goal.id)
    
    context = {
        'goal': goal,
    }
    return render(request, 'fitness/add_progress.html', context)

@login_required
def workout_plans(request):
    """View workout plans"""
    user_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')
    public_plans = WorkoutPlan.objects.filter(is_public=True).exclude(user=request.user)
    
    context = {
        'user_plans': user_plans,
        'public_plans': public_plans,
    }
    return render(request, 'fitness/workout_plans.html', context)

@login_required
def workout_plan_detail(request, plan_id):
    """View workout plan details"""
    plan = get_object_or_404(WorkoutPlan, id=plan_id)
    days = PlanDay.objects.filter(workout_plan=plan).order_by('day_number')
    
    # Get exercises for each day
    days_with_exercises = []
    for day in days:
        exercises = PlanExercise.objects.filter(plan_day=day)
        days_with_exercises.append({
            'day': day,
            'exercises': exercises
        })
    
    context = {
        'plan': plan,
        'days_with_exercises': days_with_exercises,
    }
    return render(request, 'fitness/workout_plan_detail.html', context)

@login_required
def create_workout_plan(request):
    """Create a new workout plan"""
    if request.method == 'POST':
        # Create workout plan
        plan = WorkoutPlan.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            difficulty=request.POST.get('difficulty'),
            duration_weeks=request.POST.get('duration_weeks'),
            is_public=request.POST.get('is_public') == 'on'
        )
        
        # Get number of days
        num_days = int(request.POST.get('num_days', 0))
        
        # Process each day
        for i in range(1, num_days + 1):
            day_focus = request.POST.get(f'day_{i}_focus')
            
            # Create day
            day = PlanDay.objects.create(
                workout_plan=plan,
                day_number=i,
                focus=day_focus
            )
            
            # Get exercises for this day
            exercise_ids = request.POST.getlist(f'day_{i}_exercise_id')
            sets_list = request.POST.getlist(f'day_{i}_sets')
            reps_list = request.POST.getlist(f'day_{i}_reps')
            
            # Add exercises to day
            for j in range(len(exercise_ids)):
                if j < len(sets_list) and j < len(reps_list):
                    exercise = Exercise.objects.get(id=exercise_ids[j])
                    sets = sets_list[j]
                    reps = reps_list[j]
                    
                    PlanExercise.objects.create(
                        plan_day=day,
                        exercise=exercise,
                        sets=sets,
                        reps=reps
                    )
        
        return redirect('workout_plan_detail', plan_id=plan.id)
    
    # Get all exercises for the form
    exercises = Exercise.objects.all()
    
    context = {
        'exercises': exercises,
        'difficulties': dict(WorkoutPlan._meta.get_field('difficulty').choices),
    }
    return render(request, 'fitness/create_workout_plan.html', context)

@login_required
def start_workout_from_plan(request, plan_id, day_number):
    """Start a workout from a workout plan day"""
    plan = get_object_or_404(WorkoutPlan, id=plan_id)
    day = get_object_or_404(PlanDay, workout_plan=plan, day_number=day_number)
    plan_exercises = PlanExercise.objects.filter(plan_day=day)
    
    if request.method == 'POST':
        # Create workout
        workout = Workout.objects.create(
            user=request.user,
            title=f"{plan.title} - Day {day.day_number}: {day.focus}",
            date=timezone.now().date(),
            duration=request.POST.get('duration'),
            notes=request.POST.get('notes', '')
        )
        
        # Add exercises to workout
        for plan_exercise in plan_exercises:
            WorkoutExercise.objects.create(
                workout=workout,
                exercise=plan_exercise.exercise,
                sets=plan_exercise.sets,
                reps=plan_exercise.reps,
                weight=request.POST.get(f'weight_{plan_exercise.id}')
            )
        
        return redirect('workout_detail', workout_id=workout.id)
    
    context = {
        'plan': plan,
        'day': day,
        'plan_exercises': plan_exercises,
    }
    return render(request, 'fitness/start_workout_from_plan.html', context)

@login_required
def notifications(request):
    """View all notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'fitness/notifications.html', context)

# API Views for AJAX requests

@login_required
def api_mark_goal_complete(request, goal_id):
    """API to mark a goal as complete"""
    if request.method == 'POST':
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        goal.is_completed = True
        goal.completed_date = timezone.now().date()
        goal.save()
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            title="Goal Achieved!",
            message=f"Congratulations! You've completed your goal: {goal.title}"
        )
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        else:
            # If it's a regular form submission, redirect to the goals page
            return redirect('goals')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def api_get_progress_data(request, goal_id):
    """API to get progress data for charts"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    progress_entries = Progress.objects.filter(goal=goal).order_by('date')
    
    data = {
        'title': goal.title,
        'labels': [entry.date.strftime('%Y-%m-%d') for entry in progress_entries],
        'values': [float(entry.value) for entry in progress_entries],
        'target': float(goal.target_value) if goal.target_value else None,
    }
    
    return JsonResponse(data)

@login_required
def api_get_workout_stats(request):
    """API to get workout statistics for charts"""
    # Get date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get workouts in date range
    workouts = Workout.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Calculate stats
    total_workouts = workouts.count()
    total_duration = workouts.aggregate(Sum('duration'))['duration__sum'] or 0
    total_calories = workouts.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    
    # Get workout counts by day
    workout_days = workouts.values('date').annotate(count=Count('id'))
    workout_days_data = {
        'labels': [day['date'].strftime('%Y-%m-%d') for day in workout_days],
        'values': [day['count'] for day in workout_days],
    }
    
    # Get workout durations by day
    workout_durations = workouts.values('date').annotate(duration=Sum('duration'))
    workout_durations_data = {
        'labels': [day['date'].strftime('%Y-%m-%d') for day in workout_durations],
        'values': [day['duration'] for day in workout_durations],
    }
    
    data = {
        'total_workouts': total_workouts,
        'total_duration': total_duration,
        'total_calories': total_calories,
        'workout_days': workout_days_data,
        'workout_durations': workout_durations_data,
    }
    
    return JsonResponse(data)

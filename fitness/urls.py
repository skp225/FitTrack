from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Exercise routes
    path('exercises/', views.exercises, name='exercises'),
    path('exercises/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    
    # Workout routes
    path('workouts/', views.workouts, name='workouts'),
    path('workouts/<int:workout_id>/', views.workout_detail, name='workout_detail'),
    path('workouts/create/', views.create_workout, name='create_workout'),
    
    # Goal routes
    path('goals/', views.goals, name='goals'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/progress/add/', views.add_progress, name='add_progress'),
    
    # Workout plan routes
    path('workout-plans/', views.workout_plans, name='workout_plans'),
    path('workout-plans/<int:plan_id>/', views.workout_plan_detail, name='workout_plan_detail'),
    path('workout-plans/create/', views.create_workout_plan, name='create_workout_plan'),
    path('workout-plans/<int:plan_id>/day/<int:day_number>/start/', views.start_workout_from_plan, name='start_workout_from_plan'),
    
    # Notification routes
    path('notifications/', views.notifications, name='notifications'),
    
    # Authentication routes
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # API routes
    path('api/goals/<int:goal_id>/complete/', views.api_mark_goal_complete, name='api_mark_goal_complete'),
    path('api/goals/<int:goal_id>/progress-data/', views.api_get_progress_data, name='api_get_progress_data'),
    path('api/workout-stats/', views.api_get_workout_stats, name='api_get_workout_stats'),
]

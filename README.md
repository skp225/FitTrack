# FitTrack - Personalized Fitness Tracker and Goal Setter

FitTrack is a comprehensive web application designed to help users track their fitness journey, set personalized goals, and follow workout plans tailored to their fitness level. This project was developed as my final project for CS50's Web Programming with Python and JavaScript course.

## Project Overview

In today's fast-paced world, maintaining a consistent fitness routine can be challenging. Many people struggle to stay motivated and track their progress effectively. FitTrack aims to solve this problem by providing a centralized platform where users can:

- Set personalized fitness goals with deadlines
- Track progress with visual indicators and graphs
- Log workouts with detailed exercise information
- Create and follow custom workout plans
- Access a comprehensive exercise library
- Receive notifications for achievements and reminders

The application is built with Django on the backend and uses Bootstrap 5 for a responsive frontend design. It incorporates JavaScript for interactive elements and Chart.js for data visualization.

## Distinctiveness and Complexity

This project stands out from other course projects in several ways. Unlike the e-commerce and social network projects, FitTrack focuses on personal health and fitness tracking with a complex data model that handles relationships between users, goals, workouts, exercises, and workout plans.

The complexity of this project is evident in the following aspects:

1. **Complex Data Relationships**: The application manages intricate relationships between multiple models. For example, a workout plan consists of multiple days, each with multiple exercises, sets, and reps. Goals track progress over time with multiple data points. These relationships required careful planning and implementation.

2. **Personalized User Experience**: The application tailors content based on user preferences and fitness level. The dashboard displays personalized statistics, goal progress, and workout recommendations. This required implementing complex queries and data aggregation.

3. **Interactive Data Visualization**: Unlike previous projects, FitTrack incorporates interactive charts and graphs to visualize user progress over time. This was implemented using Chart.js and required custom JavaScript to handle data formatting and display.

4. **Responsive Design with Complex UI Components**: The UI includes advanced components like tabbed interfaces, progress bars, modals, and dynamic form handling. The workout plan creator, for example, allows users to dynamically add days and exercises with JavaScript.

5. **API Integration**: The application includes a REST API for fetching workout statistics and goal progress data, which is then displayed in the frontend using asynchronous JavaScript.

The project also demonstrates distinctiveness in its focus on health and fitness, which wasn't covered by other course projects. It combines elements of a tracking tool, social platform (through shared workout plans), and educational resource (through the exercise library).

## File Structure and Contents

### Backend (Django)

- **fitness/models.py**: Contains all the data models including User, Profile, Goal, GoalProgress, Exercise, Workout, WorkoutExercise, WorkoutPlan, WorkoutPlanDay, WorkoutPlanExercise, and Notification.
- **fitness/views.py**: Contains all the view functions that handle requests and render templates or return JSON responses.
- **fitness/urls.py**: Defines URL patterns for the application.
- **fitness/admin.py**: Configures the Django admin interface for the models.
- **fitness_tracker/settings.py**: Contains project settings including database configuration, installed apps, middleware, etc.
- **fitness_tracker/urls.py**: Main URL configuration that includes the fitness app URLs.

### Frontend (Templates)

- **templates/fitness/base.html**: Base template that all other templates extend, includes navigation, footer, and common CSS/JS.
- **templates/fitness/index.html**: Landing page with features and call-to-action.
- **templates/fitness/login.html** & **register.html**: Authentication templates.
- **templates/fitness/dashboard.html**: Main dashboard showing user stats, goals, and recent workouts.
- **templates/fitness/profile.html** & **profile_setup.html**: User profile management.
- **templates/fitness/goals.html** & **goal_detail.html**: Goal listing and detailed view.
- **templates/fitness/create_goal.html** & **add_progress.html**: Forms for creating goals and adding progress.
- **templates/fitness/workouts.html** & **workout_detail.html**: Workout listing and detailed view.
- **templates/fitness/create_workout.html**: Form for logging new workouts.
- **templates/fitness/exercises.html** & **exercise_detail.html**: Exercise library and detailed view.
- **templates/fitness/workout_plans.html** & **workout_plan_detail.html**: Workout plan listing and detailed view.
- **templates/fitness/create_workout_plan.html**: Form for creating custom workout plans.
- **templates/fitness/notifications.html**: Notification center.

### Other Files

- **requirements.txt**: Lists all Python packages required to run the application.
- **manage.py**: Django's command-line utility for administrative tasks.

## How to Run the Application

Follow these steps to run the FitTrack application:

1. Clone the repository to your local machine.
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Apply migrations to create the database:
   ```
   python manage.py migrate
   ```
6. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```
7. Load initial data (optional):
   ```
   python manage.py loaddata exercises.json
   ```
8. Run the development server:
   ```
   python manage.py runserver
   ```
9. Open your browser and navigate to `http://127.0.0.1:8000/`

## Additional Information

### Features Implemented

- **User Authentication**: Registration, login, logout, and profile management.
- **Goal Setting**: Create goals with target values, deadlines, and progress tracking.
- **Workout Logging**: Record workouts with exercises, sets, reps, and weights.
- **Exercise Library**: Browse exercises by muscle group and difficulty level.
- **Workout Plans**: Create and follow structured workout plans.
- **Progress Tracking**: Visual representation of progress towards goals.
- **Notifications**: System notifications for achievements and reminders.

### Known Issues and Future Improvements

- The progress charts sometimes don't render correctly on mobile devices.
- Planning to add social features like sharing workouts and following friends.
- Would like to implement a mobile app version using the Django REST framework.
- Need to add more comprehensive exercise demonstrations, possibly with videos.

### Credits

- Exercise data compiled from various fitness resources.
- Icons from Font Awesome.
- UI components from Bootstrap 5.
- Charts implemented with Chart.js.

I learned a ton while building this project, especially about managing complex data relationships in Django and creating interactive UI components with JavaScript. The most challenging part was implementing the workout plan creator with dynamic form handling, but it was also the most rewarding when it finally worked!

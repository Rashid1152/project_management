# Project Management System

A Django-based project management application with role-based access control, allowing teams to collaborate on projects with different permission levels.

## Features

- **User Authentication**: Register, login, and logout functionality
- **Project Management**: Create, view, edit, and delete projects
- **Role-Based Access Control**: Three permission levels (Owner, Editor, Reader)
- **Project Comments**: Add and view comments on projects
- **User Management**: Add users to projects and manage their roles
- **Admin Interface**: Django admin panel for system administration

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository** (or download and extract the ZIP file)

2. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows: 
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux: 
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

5. **Run database migrations**:
   ```
   python manage.py makemigrations
   python manage.py makemigrations projects
   python manage.py makemigrations users
   python manage.py migrate
   ```

6. **Create a superuser** (admin account):
   ```
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin username, email, and password.

7. **Start the development server**:
   ```
   python manage.py runserver
   ```

8. **Access the application** at http://127.0.0.1:8000/

## How to Use the Application

### User Authentication

1. **Register**: Click the "Register" button on the homepage and fill in the required information.
2. **Login**: Use your credentials to log in to the system.
3. **Logout**: Click the "Logout" button when you're done.

### Project Management

1. **Create a Project**:
   - Click the "New Project" button
   - Enter a title and description
   - Click "Save Project"

2. **View Projects**:
   - All projects you have access to are displayed on the homepage
   - Click "View Details" to see more information about a project

3. **Edit a Project**:
   - Open the project details
   - Click the "Edit" button
   - Update the title and/or description
   - Click "Save Project"

4. **Delete a Project**:
   - Open the project details
   - Click the "Delete" button
   - Confirm the deletion

### User and Role Management

1. **Add Users to a Project**:
   - Open the project details
   - Click "Manage Users"
   - Enter the username of the user you want to add
   - Select a role (Owner, Editor, or Reader)
   - Click "Add User"

2. **Change User Roles**:
   - Open the project details
   - Click "Manage Users"
   - Use the dropdown next to the user's name to change their role
   - Changes are saved automatically

3. **Remove Users**:
   - Open the project details
   - Click "Manage Users"
   - Click the "Remove" button next to the user you want to remove

### Role Permissions

- **Owner**: Full control over the project. Can edit, delete, manage users, and add comments.
- **Editor**: Can edit project details and add comments, but cannot delete the project or manage users.
- **Reader**: Can only view the project details, cannot make any changes.

### Comments

1. **Add a Comment**:
   - Open the project details
   - Type your comment in the text area
   - Click "Add Comment"

2. **View Comments**:
   - All comments are displayed in the project details view

## Design Decisions and Assumptions

### Architecture

- **Django Framework**: Used for its robust ORM, authentication system, and admin interface.
- **Django REST Framework**: Provides a RESTful API for the frontend to interact with.
- **Single-Page Application**: The frontend is built as a SPA using vanilla JavaScript for simplicity.

### Database Design

- **User Model**: Leveraged Django's built-in User model for authentication.
- **Project Model**: Stores basic project information (title, description, timestamps).
- **ProjectUser Model**: Many-to-many relationship between users and projects with an additional role field.
- **Comment Model**: Stores comments with references to the project and user.

### Security Considerations

#### Authentication
- **Session-based Authentication**: Secure session management using Django's built-in authentication system.
- **Password Validation**: Enforces password strength requirements.
- **CSRF Protection**: Implemented for all POST, PUT, PATCH, and DELETE requests to prevent cross-site request forgery attacks.

#### Authorization
- **Role-Based Access Control (RBAC)**: Implemented through custom permission classes that check user roles before allowing actions.
- **Object-Level Permissions**: Each project has its own set of permissions based on the user's role within that project.
- **Permission Classes**:
  - `IsProjectOwner`: Only allows project owners to perform certain actions (delete project, manage users).
  - `IsProjectOwnerOrEditor`: Allows both owners and editors to perform actions (edit project, add comments).
  - `HasProjectAccess`: Ensures users have at least reader access to view project details.
- **Server-Side Validation**: All permission checks are performed on the server side to prevent unauthorized access even if the frontend is bypassed.
- **API Endpoint Protection**: Each API endpoint has appropriate permission classes applied to ensure only authorized users can access or modify data.

### User Experience

- **Bootstrap UI**: Used for responsive design and consistent styling.
- **Modal Dialogs**: Used for forms and confirmations to keep the UI clean.
- **Real-time Updates**: The UI refreshes automatically after actions are performed.

### Assumptions

1. **Single Owner**: Each project has exactly one owner at any given time.
2. **Username Uniqueness**: Usernames are unique across the system.
3. **Public Registration**: Anyone can register for an account.
4. **Project Privacy**: Projects are only visible to users who have been explicitly added to them.
5. **Comment Permissions**: Only owners and editors can add comments.

## API Endpoints

- `/api/auth/register/` - Register a new user
- `/api/auth/login/` - Login
- `/api/auth/logout/` - Logout
- `/api/auth/me/` - Get current user details
- `/api/auth/users/` - Search for users by username
- `/api/projects/` - List and create projects
- `/api/projects/<id>/` - Retrieve, update, delete a project
- `/api/projects/<id>/users/` - List project users
- `/api/projects/<id>/add_user/` - Add a user to a project
- `/api/projects/<id>/remove-user/<user_id>/` - Remove a user from a project
- `/api/projects/<id>/update-role/<user_id>/` - Update a user's role
- `/api/projects/<id>/comments/` - List project comments
- `/api/projects/<id>/add_comment/` - Add a comment to a project

## Testing

The project includes comprehensive tests for both the backend API and the models. These tests ensure that all functionality works as expected and that permissions are properly enforced.

### Running All Tests

To run all tests:

```
pytest
```

If you encounter issues with test discovery, make sure:
1. Your test files follow the naming convention: `test_*.py`, `*_test.py`, or `tests.py`
2. The pytest.ini file is properly configured
3. You have installed pytest-django: `pip install pytest-django`

### Running Specific Test Modules

You can run tests for specific apps or files:

```
# Test the users app
pytest users/

# Test the projects app
pytest projects/

# Test a specific file
pytest users/test_models.py
```

### Test Structure

Tests are organized by app and functionality:

- `users/test_models.py` - Tests for user models and authentication
- `users/tests.py` - Tests for user API endpoints
- `projects/test_models.py` - Tests for project models
- `projects/tests.py` - Tests for project API endpoints

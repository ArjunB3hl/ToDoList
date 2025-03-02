# TaskFlow - Modern Task Management Application

TaskFlow is a modern, feature-rich task management application built with Django. It allows users to create, manage, and track tasks with various attributes such as priority levels, due dates, and status.

## Features

- **User Authentication**: Register, login, and manage your personal tasks
- **Task Management**: Create, edit, and delete tasks
- **Task Attributes**: Set priority levels (Low, Medium, High), status (Pending, In Progress, Completed), and due dates
- **Task Filtering**: Filter tasks by status, priority, and search terms
- **Responsive Design**: Works on desktop and mobile devices
- **Cookie-based Storage**: Non-authenticated users can still use the app with tasks stored in cookies

## Technologies Used

- **Backend**: Django 5.1+
- **Database**: SQLite (can be configured for PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript
- **Icons**: Material Icons

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd TaskFlow
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the backend directory with the following content:
   ```
   DJANGO_SECRET_KEY=your-secret-key
   ```

4. Run migrations:
   ```
   cd backend
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Usage

### Adding Tasks
- Click the "Add Task" button to create a new task
- Fill in the task details including title, description, priority, status, and due date
- Click "Add Task" to save

### Managing Tasks
- View all your tasks on the main page
- Click on a task to edit its details
- Use the filter form to sort and filter tasks
- Mark tasks as completed using the checkmark icon
- Delete tasks using the delete icon

### User Authentication
- Register a new account to save your tasks to the database
- Log in to access your tasks from any device
- Log out when you're done

## PostgreSQL Configuration (Optional)

To use PostgreSQL instead of SQLite:

1. Install PostgreSQL and create a database
2. Install psycopg2-binary:
   ```
   pip install psycopg2-binary
   ```
3. Update the `.env` file with your PostgreSQL credentials:
   ```
   DATABASE_NAME=your_db_name
   DATABASE_USER=your_db_user
   DATABASE_PASSWORD=your_db_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```
4. Uncomment the PostgreSQL configuration in `backend/tools/settings.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

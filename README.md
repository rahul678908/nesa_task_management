# Task Management Application

A straightforward Django app that lets admins assign tasks to users and track how those tasks get done. When a user finishes a task, they write a short report and log how many hours they spent — admins can then review everything from a clean web dashboard.

---

## What's in here?

- Users log in via the web panel or the API using JWT tokens
- Three roles — SuperAdmin, Admin, and User — each with their own set of things they can and can't do
- When a user marks a task as done, they're required to explain what they did and how long it took
- Admins get a web dashboard to create tasks, assign them, and read completion reports
- SQLite is used as the database so there's no extra setup needed

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x, Django 4.2 |
| REST API | Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | SQLite |
| Frontend | Django HTML Templates |

---

## Project Structure

```
task_management/
├── manage.py
├── requirements.txt
│
├── task_management/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                 # Users, roles, JWT login
│   ├── models.py             # Custom User model with role field
│   ├── views.py              # JWT login API
│   ├── serializers.py
│   ├── permissions.py        # Hardcoded role-based permission classes
│   └── urls.py
│
├── tasks/                    # Task API endpoints
│   ├── models.py             # Task model
│   ├── views.py              # GET /tasks, PUT /tasks/{id}, GET /tasks/{id}/report
│   ├── serializers.py
│   └── urls.py
│
├── dashboard/                # Admin panel (web views)
│   ├── views.py              # SuperAdmin & Admin dashboard logic
│   └── urls.py
│
└── templates/
    ├── base.html
    ├── auth/
    │   └── login.html
    ├── superadmin/
    │   ├── dashboard.html
    │   ├── create_user.html
    │   └── task_report.html
    └── admin/
        ├── dashboard.html
        ├── create_task.html
        └── task_report.html
```

---

## Getting Started

### 1. Create a virtual environment and activate it

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install the dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the database

```bash
python manage.py makemigrations accounts tasks
python manage.py migrate
```

### 4. Create your first SuperAdmin

```bash
python manage.py createsuperuser
```

> Just fill in a username and password when prompted. Because `is_superuser` gets set to `True`, the app automatically assigns that account the `superadmin` role.

### 5. Run the server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser — it'll take you straight to the login page.

---

## Who Can Do What

| Action | SuperAdmin | Admin | User |
|---|:---:|:---:|:---:|
| Create / delete users | ✅ | ❌ | ❌ |
| Create / delete admins | ✅ | ❌ | ❌ |
| Promote / demote users ↔ admins | ✅ | ❌ | ❌ |
| Assign users to admins | ✅ | ❌ | ❌ |
| View all tasks | ✅ | ✅ (their users only) | ❌ |
| Create & assign tasks | ✅ | ✅ (their users only) | ❌ |
| Delete tasks | ✅ | ✅ (their users only) | ❌ |
| View task completion reports | ✅ | ✅ (their users only) | ❌ |
| View own assigned tasks (API) | ❌ | ❌ | ✅ |
| Update task status (API) | ❌ | ❌ | ✅ |

---

## API Endpoints

Base URL: `http://127.0.0.1:8000`

### Logging in

| Method | Endpoint | Description | Needs Auth? |
|---|---|---|:---:|
| POST | `/api/auth/login/` | Get a JWT token using username & password | No |
| POST | `/api/auth/token/refresh/` | Refresh an expired access token | No |

**Request body:**
```json
{
  "username": "john",
  "password": "secret123"
}
```

**Response:**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "role": "user",
  "username": "john"
}
```

> Once you have the token, attach it to every API request like this:
> `Authorization: Bearer <access_token>`

---

### Tasks

| Method | Endpoint | Description | Who can use it |
|---|---|---|---|
| GET | `/api/tasks/` | Get all tasks assigned to you | Users only |
| PUT | `/api/tasks/{id}/` | Update a task's status | Users only (your own tasks) |
| GET | `/api/tasks/{id}/report/` | Read the completion report for a finished task | Admins & SuperAdmins |

#### Updating a task — PUT `/api/tasks/{id}/`

Just changing the status to in progress:
```json
{
  "status": "in_progress"
}
```

Marking it as completed (report and hours are both required here):
```json
{
  "status": "completed",
  "completion_report": "Finished all subtasks. Hit a CSS bug along the way but sorted it with a flexbox fix.",
  "worked_hours": 4.5
}
```

If you forget the report or hours, you'll get back something like:
```json
{
  "completion_report": ["Completion report is required when marking a task as completed."]
}
```

#### Reading a report — GET `/api/tasks/{id}/report/`

```json
{
  "id": 3,
  "title": "Build login page",
  "assigned_to_username": "john",
  "status": "completed",
  "completion_report": "Page built and tested across Chrome, Firefox, and Safari.",
  "worked_hours": "6.00",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

## Admin Panel Pages

| URL | Who sees it | What it does |
|---|---|---|
| `/login/` | Everyone | Login page |
| `/logout/` | Everyone | Logs you out |
| `/superadmin/dashboard/` | SuperAdmin | Full overview — users, admins, all tasks |
| `/superadmin/users/create/` | SuperAdmin | Add a new user or admin |
| `/superadmin/users/{id}/delete/` | SuperAdmin | Remove a user or admin |
| `/superadmin/users/{id}/role/` | SuperAdmin | Promote or demote someone |
| `/superadmin/assign/` | SuperAdmin | Assign a user to a specific admin |
| `/superadmin/tasks/{id}/report/` | SuperAdmin | Read a task's completion report |
| `/admin-panel/dashboard/` | Admin | Task dashboard for their assigned users |
| `/admin-panel/tasks/create/` | Admin | Create and assign a task |
| `/admin-panel/tasks/{id}/delete/` | Admin | Delete a task |
| `/admin-panel/tasks/{id}/report/` | Admin | Read a completion report |

---

## Task Fields

| Field | Type | Notes |
|---|---|---|
| `title` | CharField | What the task is called |
| `description` | TextField | More detail about what needs doing |
| `assigned_to` | ForeignKey → User | Which user is responsible |
| `created_by` | ForeignKey → User | Which admin created it |
| `due_date` | DateField | When it's due |
| `status` | CharField | `pending`, `in_progress`, or `completed` |
| `completion_report` | TextField | What the user did — required on completion |
| `worked_hours` | DecimalField | How long it took — required on completion, must be > 0 |

---

## Permission Classes

All permissions are hardcoded by role in `accounts/permissions.py`. No database flags, no dynamic config.

| Class | Who gets in |
|---|---|
| `IsUser` | `role == 'user'` |
| `IsAdmin` | `role == 'admin'` |
| `IsSuperAdmin` | `role == 'superadmin'` |
| `IsAdminOrSuperAdmin` | `role` is `admin` or `superadmin` |
| `IsAuthenticatedUser` | Anyone who's logged in |

Just drop the right class into `permission_classes` on any view:

```python
from accounts.permissions import IsUser, IsAdminOrSuperAdmin

class TaskListAPIView(APIView):
    permission_classes = [IsUser]  # only role='user' gets through
```

---

## How the Task Completion Flow Works

```
User logs in  →  GET /api/tasks/  →  sees their tasks
      ↓
PUT /api/tasks/{id}/   status = in_progress
      ↓
PUT /api/tasks/{id}/   status = completed
                       + completion_report  (required)
                       + worked_hours       (required, > 0)
      ↓
Admin or SuperAdmin reads the report
via GET /api/tasks/{id}/report/  or  the Admin Panel
```

---

## A Few Things Worth Knowing

- Going to `http://127.0.0.1:8000/` sends you straight to the login page
- Admins only see tasks and reports for users who are assigned to them — they can't peek at other admins' users
- SuperAdmins can't be deleted or have their role changed through the UI (by design)
- You only need to include `completion_report` and `worked_hours` when setting status to `completed` — updating to `in_progress` doesn't need them

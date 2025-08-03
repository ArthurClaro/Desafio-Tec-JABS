# Time Tracking System - JABS Technical Challenge

## 📋 Project Description

Complete time tracking system developed with **Django** and **Django Rest Framework**, following best development practices. The project allows users to register tasks and record work time dedicated to each one, with a modern web interface and complete RESTful API.

## ✨ Implemented Features

### 🎯 Main Features
- **Task Registration**: Creation and management of tasks with detailed description
- **Time Recording**: Recording of time worked on each task
- **Interactive Dashboard**: Overview with statistics and recent data
- **Advanced Filters**: Search and filtering by multiple criteria
- **Responsive Interface**: Modern design with Bootstrap 5

### 🔧 Technical Features
- **Complete RESTful API**: Endpoints for all CRUD operations
- **Authentication and Authorization**: Login system with permissions
- **Dynamic Filters**: Search by text, dates, periods and status
- **Data Validation**: Custom validations in models
- **Custom Admin**: Optimized administrative interface
- **Auto Documentation**: Self-documented API
- **Comprehensive Tests**: Unit and integration tests

## 🛠️ Technologies Used

- **Backend**: Django 4.2.7, Django Rest Framework 3.14.0
- **Database**: SQLite (configurable for PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Filters**: django-filter 23.3
- **CORS**: django-cors-headers 4.3.1
- **Configuration**: python-decouple 3.8

## 🚀 How to Run the Project

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository
```bash
git clone <REPOSITORY_URL>
cd Desafio-Tec-JABS
```

### 2. Create a Virtual Environment
```bash
# Windows
py -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your settings
# The file contains all necessary environment variables
```

### 5. Configure the Database
```bash
py manage.py makemigrations
py manage.py migrate
```

### 6. Create a Superuser
```bash
py manage.py createsuperuser
```

### 7. Run the Server
```bash
py manage.py runserver
```

### 8. Access the Application
- **Web Interface**: http://127.0.0.1:8000/
- **REST API**: http://127.0.0.1:8000/api/
- **Django Admin**: http://127.0.0.1:8000/admin/

## 📱 Web Interface

### Dashboard
- Overview with statistics
- Recent tasks and records
- Quick actions

### Task Management
- Task list with filters
- Task creation and editing
- Detailed view with records

### Time Records
- Record list with advanced filters
- Record creation and editing
- Filters by period, date and text search

## 🔌 REST API

### Available Endpoints

#### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Remove task
- `GET /api/tasks/active/` - List active tasks
- `GET /api/tasks/inactive/` - List inactive tasks
- `POST /api/tasks/{id}/toggle_status/` - Toggle status

#### Time Records
- `GET /api/records/` - List all records
- `POST /api/records/` - Create new record
- `GET /api/records/{id}/` - Record details
- `PUT /api/records/{id}/` - Update record
- `DELETE /api/records/{id}/` - Remove record
- `GET /api/records/today/` - Today's records
- `GET /api/records/this_week/` - This week's records
- `GET /api/records/this_month/` - This month's records
- `GET /api/records/summary/` - Statistical summary

#### Dashboard
- `GET /api/dashboard/` - Dashboard data

### Available Filters

#### Tasks
- `search`: Search by description
- `creation_date_start`: Creation date (start)
- `creation_date_end`: Creation date (end)
- `active`: Task status

#### Records
- `search`: General search
- `work_description`: Work description
- `task_description`: Task description
- `record_date_start`: Record date (start)
- `record_date_end`: Record date (end)
- `min_time`: Minimum time
- `max_time`: Maximum time
- `user`: Responsible user
- `period`: Predefined period (today, this_week, etc.)

### API Usage Example

```bash
# List tasks
curl -H "Authorization: Basic <credentials>" http://127.0.0.1:8000/api/tasks/

# Create new task
curl -X POST -H "Content-Type: application/json" \
     -d '{"description": "New task", "active": true}' \
     http://127.0.0.1:8000/api/tasks/

# Filter records
curl "http://127.0.0.1:8000/api/records/?period=this_week&search=development"
```

## 🏗️ Project Structure

```
Desafio-Tec-JABS/
├── time_control/           # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URLs
│   └── wsgi.py            # WSGI configuration
├── time_tracking/         # Main application
│   ├── models.py          # Data models
│   ├── views.py           # API ViewSets
│   ├── web_views.py       # Web interface views
│   ├── serializers.py     # API serializers
│   ├── forms.py           # Web forms
│   ├── filters.py         # API filters
│   ├── admin.py           # Admin configuration
│   ├── tests.py           # Comprehensive tests
│   ├── urls.py            # Application URLs
│   └── templates/         # HTML templates
│       ├── base.html      # Base template
│       └── time_tracking/ # Specific templates
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables example
├── manage.py             # Management script
└── README.md             # This file
```

## 📊 Data Models

### Task
- `responsible_user`: Relationship with User
- `creation_date`: Creation date/time
- `description`: Task description
- `active`: Task status (active/inactive)

### TimeRecord
- `task`: Relationship with Task
- `record_date`: Record date
- `worked_time`: Work duration
- `work_description`: Description of work performed
- `creation_date`: Record creation date/time

## 🔐 Authentication and Security

- **Authentication**: Session Authentication + Basic Authentication
- **Permissions**: Only authenticated users can access
- **Isolation**: Users only see their own data
- **Validation**: Custom validations in models

## 🎨 Interface and UX

- **Responsive Design**: Works on desktop, tablet and mobile
- **Bootstrap 5**: Modern CSS framework
- **Bootstrap Icons**: Consistent icons
- **Sidebar Navigation**: Intuitive navigation
- **Cards and Tables**: Organized and clean layout
- **Intuitive Filters**: User-friendly search interface

## 📈 Advanced Features

### Dashboard
- Real-time statistics
- Productivity charts
- Recent data
- Quick actions

### Advanced Filters
- Text search
- Date filters
- Period filters
- Status filters

### Reports
- Total time per task
- Statistics by period
- Averages and totals
- Data export

## 🧪 Tests

To run tests:
```bash
py manage.py test
```

The project includes comprehensive tests covering:
- **Model Tests**: Task and TimeRecord model functionality
- **API Tests**: All REST endpoints and CRUD operations
- **Validation Tests**: Data validation and business logic
- **Integration Tests**: End-to-end functionality

## 📝 API Documentation

The API is self-documented and can be accessed at:
- **Browsable API**: http://127.0.0.1:8000/api/
- **Interactive Documentation**: Available in browser

## 🚀 Deployment

### Production Settings
1. Change `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Configure production database
4. Configure static files
5. Configure environment variables

### Example with PostgreSQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'time_tracking',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🤝 Contribution

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project was developed as part of the technical challenge for the Python/Django Developer position at JABS.

## 📞 Contact

- **Email**: iabstecnologia@iabs.org.br
- **Questions**: Send to the email above

---

## 🎯 Evaluation Criteria Met

✅ **Functionality**: All specifications implemented
✅ **Code Quality**: Organized and well-documented code
✅ **Technical Solution**: Efficient use of Django resources
✅ **Documentation**: Complete and detailed README
✅ **Best Practices**: Django Rest Framework, advanced filters, modern interface
✅ **Testing**: Comprehensive test coverage
✅ **Internationalization**: English language support
✅ **Project Structure**: Clean and organized codebase
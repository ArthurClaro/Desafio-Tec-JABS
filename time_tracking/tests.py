from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task, TimeRecord


class TaskModelTest(TestCase):
    """Test cases for Task model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.task = Task.objects.create(
            responsible_user=self.user,
            description='Test task for unit testing',
            active=True
        )
    
    def test_task_creation(self):
        """Test if task is created correctly."""
        self.assertEqual(self.task.description, 'Test task for unit testing')
        self.assertEqual(self.task.responsible_user, self.user)
        self.assertTrue(self.task.active)
        self.assertIsNotNone(self.task.creation_date)
    
    def test_task_string_representation(self):
        """Test task string representation."""
        expected = f"{self.task.description[:50]} - {self.user.username}"
        self.assertEqual(str(self.task), expected)
    
    def test_task_total_worked_time(self):
        """Test total worked time calculation."""
        # Create time records
        TimeRecord.objects.create(
            task=self.task,
            record_date=timezone.now().date(),
            worked_time=timedelta(hours=2),
            work_description='First work session'
        )
        TimeRecord.objects.create(
            task=self.task,
            record_date=timezone.now().date(),
            worked_time=timedelta(hours=1, minutes=30),
            work_description='Second work session'
        )
        
        total_time = self.task.total_worked_time
        expected_seconds = (2 * 3600) + (1 * 3600 + 30 * 60)  # 3.5 hours
        self.assertEqual(total_time.total_seconds(), expected_seconds)
    
    def test_task_total_hours_formatting(self):
        """Test total hours formatting."""
        TimeRecord.objects.create(
            task=self.task,
            record_date=timezone.now().date(),
            worked_time=timedelta(hours=2, minutes=30),
            work_description='Work session'
        )
        
        self.assertEqual(self.task.total_hours, "2.50 hours")


class TimeRecordModelTest(TestCase):
    """Test cases for TimeRecord model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.task = Task.objects.create(
            responsible_user=self.user,
            description='Test task',
            active=True
        )
        self.time_record = TimeRecord.objects.create(
            task=self.task,
            record_date=timezone.now().date(),
            worked_time=timedelta(hours=2, minutes=30),
            work_description='Test work description'
        )
    
    def test_time_record_creation(self):
        """Test if time record is created correctly."""
        self.assertEqual(self.time_record.task, self.task)
        self.assertEqual(self.time_record.record_date, timezone.now().date())
        self.assertEqual(self.time_record.worked_time, timedelta(hours=2, minutes=30))
        self.assertEqual(self.time_record.work_description, 'Test work description')
    
    def test_time_record_string_representation(self):
        """Test time record string representation."""
        expected = f"{self.task.description[:30]} - {self.time_record.record_date} ({self.time_record.worked_time})"
        self.assertEqual(str(self.time_record), expected)
    
    def test_worked_hours_formatting(self):
        """Test worked hours formatting."""
        self.assertEqual(self.time_record.worked_hours, "02:30")
    
    def test_time_record_validation(self):
        """Test time record validation."""
        # Test future date validation
        future_record = TimeRecord(
            task=self.task,
            record_date=timezone.now().date() + timedelta(days=1),
            worked_time=timedelta(hours=1),
            work_description='Future work'
        )
        
        with self.assertRaises(Exception):
            future_record.full_clean()


class TaskAPITest(APITestCase):
    """Test cases for Task API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(
            responsible_user=self.user,
            description='Test task for API',
            active=True
        )
    
    def test_list_tasks(self):
        """Test listing tasks."""
        url = '/api/tasks/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_task(self):
        """Test creating a new task."""
        url = '/api/tasks/'
        data = {
            'description': 'New test task',
            'active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
    
    def test_retrieve_task(self):
        """Test retrieving a specific task."""
        url = f'/api/tasks/{self.task.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], self.task.description)
    
    def test_update_task(self):
        """Test updating a task."""
        url = f'/api/tasks/{self.task.id}/'
        data = {
            'description': 'Updated task description',
            'active': False
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, 'Updated task description')
        self.assertFalse(self.task.active)
    
    def test_delete_task(self):
        """Test deleting a task."""
        url = f'/api/tasks/{self.task.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_toggle_task_status(self):
        """Test toggling task status."""
        url = f'/api/tasks/{self.task.id}/toggle_status/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertFalse(self.task.active)
    
    def test_active_tasks_filter(self):
        """Test filtering active tasks."""
        # Create inactive task
        Task.objects.create(
            responsible_user=self.user,
            description='Inactive task',
            active=False
        )
        
        url = '/api/tasks/active/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['active'])


class TimeRecordAPITest(APITestCase):
    """Test cases for TimeRecord API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(
            responsible_user=self.user,
            description='Test task for time records',
            active=True
        )
        self.time_record = TimeRecord.objects.create(
            task=self.task,
            record_date=timezone.now().date(),
            worked_time=timedelta(hours=2),
            work_description='Test work session'
        )
    
    def test_list_time_records(self):
        """Test listing time records."""
        url = '/api/records/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_time_record(self):
        """Test creating a new time record."""
        url = '/api/records/'
        data = {
            'task_id': self.task.id,
            'record_date': timezone.now().date().isoformat(),
            'worked_time': '01:30:00',
            'work_description': 'New work session'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimeRecord.objects.count(), 2)
    
    def test_retrieve_time_record(self):
        """Test retrieving a specific time record."""
        url = f'/api/records/{self.time_record.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['work_description'], self.time_record.work_description)
    
    def test_update_time_record(self):
        """Test updating a time record."""
        url = f'/api/records/{self.time_record.id}/'
        data = {
            'task_id': self.task.id,
            'record_date': timezone.now().date().isoformat(),
            'worked_time': '03:00:00',
            'work_description': 'Updated work session'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.time_record.refresh_from_db()
        self.assertEqual(self.time_record.work_description, 'Updated work session')
    
    def test_delete_time_record(self):
        """Test deleting a time record."""
        url = f'/api/records/{self.time_record.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TimeRecord.objects.count(), 0)
    
    def test_today_records_filter(self):
        """Test filtering today's records."""
        url = '/api/records/today/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_summary_endpoint(self):
        """Test summary endpoint."""
        url = '/api/records/summary/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_hours', response.data)
        self.assertIn('total_records', response.data)


class DashboardAPITest(APITestCase):
    """Test cases for Dashboard API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(
            responsible_user=self.user,
            description='Test task for dashboard',
            active=True
        )
        TimeRecord.objects.create(
            task=self.task,
            record_date=timezone.now().date(),
            worked_time=timedelta(hours=3),
            work_description='Dashboard test work'
        )
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint."""
        url = '/api/dashboard/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tasks', response.data)
        self.assertIn('active_tasks', response.data)
        self.assertIn('total_worked_hours', response.data)
        self.assertIn('recent_tasks', response.data)
        self.assertIn('recent_records', response.data)
        
        self.assertEqual(response.data['total_tasks'], 1)
        self.assertEqual(response.data['active_tasks'], 1)
        self.assertEqual(response.data['total_worked_hours'], 3.0)

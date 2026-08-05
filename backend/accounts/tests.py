from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, UserRole
from departments.models import Department
from tasks.models import Task, TaskCategory, TaskStatus


class AuthAndTaskAPITests(APITestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='ICT Support')
        self.category = TaskCategory.objects.create(
            name='Data Entry',
            default_expected_output=5,
            default_expected_duration_minutes=30,
        )
        self.supervisor = User.objects.create_user(
            email='supervisor@example.com',
            password='TestPass123!',
            first_name='Sam',
            last_name='Supervisor',
            employee_or_intern_number='SUP-001',
            role=UserRole.SUPERVISOR,
            department=self.dept,
        )
        self.intern = User.objects.create_user(
            email='intern@example.com',
            password='TestPass123!',
            first_name='Ian',
            last_name='Intern',
            employee_or_intern_number='INT-001',
            role=UserRole.INTERN,
            department=self.dept,
            supervisor=self.supervisor,
        )

    def test_login_returns_tokens(self):
        url = reverse('auth-login')
        response = self.client.post(
            url,
            {'email': 'intern@example.com', 'password': 'TestPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'intern@example.com')

    def test_me_requires_auth(self):
        response = self.client.get(reverse('auth-me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submit_approve_and_prevent_self_approve(self):
        self.client.force_authenticate(user=self.intern)
        create = self.client.post(
            reverse('task-list'),
            {
                'title': 'Update electronic records',
                'category_id': self.category.id,
                'assigned_to_id': self.intern.id,
                'supervisor_id': self.supervisor.id,
                'actual_output': 5,
            },
            format='json',
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED, create.data)
        task_id = create.data['id']

        submit = self.client.post(reverse('task-submit', args=[task_id]))
        self.assertEqual(submit.status_code, status.HTTP_200_OK)
        self.assertEqual(submit.data['status'], TaskStatus.PENDING)

        self_approve = self.client.post(
            reverse('task-approve', args=[task_id]),
            {
                'supervisor_quality_rating': 4,
                'supervisor_accuracy_rating': 4,
            },
            format='json',
        )
        self.assertEqual(self_approve.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.supervisor)
        approve = self.client.post(
            reverse('task-approve', args=[task_id]),
            {
                'supervisor_quality_rating': 5,
                'supervisor_accuracy_rating': 4,
                'supervisor_comments': 'Good work',
            },
            format='json',
        )
        self.assertEqual(approve.status_code, status.HTTP_200_OK, approve.data)
        self.assertEqual(approve.data['status'], TaskStatus.APPROVED)
        self.assertEqual(Task.objects.get(pk=task_id).status, TaskStatus.APPROVED)

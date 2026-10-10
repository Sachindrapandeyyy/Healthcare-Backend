from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from .models import Patient

class PatientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            name='User One',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            name='User Two',
            password='Password123!'
        )

        self.list_create_url = reverse('patient-list-create')
        self.valid_patient_data = {
            'name': 'Alice Wonderland',
            'age': 32,
            'gender': 'Female',
            'contact_number': '+1-555-0199',
            'address': '123 Health Ave, Medical City',
            'medical_history': 'No allergies known'
        }

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_create_url, self.valid_patient_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Alice Wonderland')
        self.assertEqual(response.data['created_by_email'], self.user1.email)

        # Ensure database record was created with user1
        patient = Patient.objects.get(id=response.data['id'])
        self.assertEqual(patient.created_by, self.user1)

    def test_patients_scoped_to_authenticated_user(self):
        # Create patients for user1 and user2
        Patient.objects.create(
            name='User1 Patient', age=40, gender='Male',
            contact_number='111', address='Addr 1', created_by=self.user1
        )
        Patient.objects.create(
            name='User2 Patient', age=50, gender='Female',
            contact_number='222', address='Addr 2', created_by=self.user2
        )

        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'User1 Patient')

    def test_patient_search_and_filter(self):
        Patient.objects.create(
            name='Alice Smith', age=30, gender='Female',
            contact_number='1234567890', address='Addr A', created_by=self.user1
        )
        Patient.objects.create(
            name='Bob Jones', age=45, gender='Male',
            contact_number='0987654321', address='Addr B', created_by=self.user1
        )

        self.client.force_authenticate(user=self.user1)

        # Filter by gender
        res_filter = self.client.get(f"{self.list_create_url}?gender=Female")
        results_filter = res_filter.data.get('results', res_filter.data)
        self.assertEqual(len(results_filter), 1)
        self.assertEqual(results_filter[0]['name'], 'Alice Smith')

        # Search by name
        res_search = self.client.get(f"{self.list_create_url}?search=Jones")
        results_search = res_search.data.get('results', res_search.data)
        self.assertEqual(len(results_search), 1)
        self.assertEqual(results_search[0]['name'], 'Bob Jones')

    def test_get_patient_detail(self):
        patient = Patient.objects.create(
            name='Detail Patient', age=25, gender='Other',
            contact_number='333', address='Addr 3', created_by=self.user1
        )
        detail_url = reverse('patient-detail', kwargs={'id': patient.id})

        # User1 can retrieve their patient
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Detail Patient')

        # User2 cannot retrieve user1's patient (returns 404)
        self.client.force_authenticate(user=self.user2)
        response_user2 = self.client.get(detail_url)
        self.assertEqual(response_user2.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_patient(self):
        patient = Patient.objects.create(
            name='Old Name', age=25, gender='Male',
            contact_number='444', address='Addr 4', created_by=self.user1
        )
        detail_url = reverse('patient-detail', kwargs={'id': patient.id})

        self.client.force_authenticate(user=self.user1)
        update_data = {
            'name': 'Updated Name',
            'age': 26,
            'gender': 'Male',
            'contact_number': '444-999',
            'address': 'New Address',
            'medical_history': 'Asthma'
        }
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')
        self.assertEqual(response.data['age'], 26)

    def test_delete_patient_soft_deletes(self):
        patient = Patient.objects.create(
            name='Delete Me', age=30, gender='Female',
            contact_number='555', address='Addr 5', created_by=self.user1
        )
        detail_url = reverse('patient-detail', kwargs={'id': patient.id})

        # User1 deletes own patient
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Active queryset excludes soft-deleted record
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())

        # But all_objects retains the record for healthcare compliance audit
        archived = Patient.all_objects.filter(id=patient.id).first()
        self.assertIsNotNone(archived)
        self.assertTrue(archived.is_deleted)
        self.assertIsNotNone(archived.deleted_at)

    def test_patient_validation_invalid_age(self):
        self.client.force_authenticate(user=self.user1)
        bad_data = self.valid_patient_data.copy()
        bad_data['age'] = -5
        response = self.client.post(self.list_create_url, bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

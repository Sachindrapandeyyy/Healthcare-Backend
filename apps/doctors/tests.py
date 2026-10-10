from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from .models import Doctor

class DoctorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='doctoradmin@example.com',
            name='Admin User',
            password='Password123!'
        )
        self.list_create_url = reverse('doctor-list-create')
        self.valid_doctor_data = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine',
            'phone': '+1-555-0987',
            'email': 'house@princeton-plainsboro.org',
            'experience_years': 20
        }

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_create_url, self.valid_doctor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Gregory House')
        self.assertEqual(response.data['specialization'], 'Diagnostic Medicine')
        self.assertTrue(Doctor.objects.filter(email='house@princeton-plainsboro.org').exists())

    def test_get_all_doctors(self):
        Doctor.objects.create(
            name='Doctor A', specialization='Cardiology', phone='111',
            email='doca@example.com', experience_years=5
        )
        Doctor.objects.create(
            name='Doctor B', specialization='Neurology', phone='222',
            email='docb@example.com', experience_years=8
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_doctor_detail(self):
        doctor = Doctor.objects.create(
            name='Doctor Detail', specialization='Pediatrics', phone='333',
            email='docdetail@example.com', experience_years=12
        )
        detail_url = reverse('doctor-detail', kwargs={'id': doctor.id})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Doctor Detail')

    def test_update_doctor(self):
        doctor = Doctor.objects.create(
            name='Doctor Edit', specialization='General', phone='444',
            email='docedit@example.com', experience_years=3
        )
        detail_url = reverse('doctor-detail', kwargs={'id': doctor.id})

        self.client.force_authenticate(user=self.user)
        update_data = {
            'name': 'Doctor Edited',
            'specialization': 'General Medicine',
            'phone': '444-999',
            'email': 'docedit@example.com',
            'experience_years': 4
        }
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Doctor Edited')
        self.assertEqual(response.data['experience_years'], 4)

    def test_delete_doctor(self):
        doctor = Doctor.objects.create(
            name='Doctor Delete', specialization='Dermatology', phone='555',
            email='docdelete@example.com', experience_years=7
        )
        detail_url = reverse('doctor-detail', kwargs={'id': doctor.id})

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())

    def test_doctor_duplicate_email_rejected(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.list_create_url, self.valid_doctor_data, format='json')

        # Attempt to create another doctor with identical email
        response = self.client.post(self.list_create_url, self.valid_doctor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_doctor_negative_experience_rejected(self):
        self.client.force_authenticate(user=self.user)
        bad_data = self.valid_doctor_data.copy()
        bad_data['email'] = 'newdoc@example.com'
        bad_data['experience_years'] = -1
        response = self.client.post(self.list_create_url, bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

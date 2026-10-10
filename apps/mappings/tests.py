from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from .models import PatientDoctorMapping

class PatientDoctorMappingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='mapuser1@example.com',
            name='Mapping User 1',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            email='mapuser2@example.com',
            name='Mapping User 2',
            password='Password123!'
        )

        self.doctor1 = Doctor.objects.create(
            name='Dr. Strange',
            specialization='Neuroscience',
            phone='1234567890',
            email='strange@marvel.com',
            experience_years=15
        )
        self.doctor2 = Doctor.objects.create(
            name='Dr. McCoy',
            specialization='General Practice',
            phone='0987654321',
            email='mccoy@enterprise.org',
            experience_years=12
        )

        self.patient1 = Patient.objects.create(
            name='Peter Parker',
            age=21,
            gender='Male',
            contact_number='1112223333',
            address='Queens, NY',
            created_by=self.user1
        )
        self.patient2 = Patient.objects.create(
            name='Miles Morales',
            age=18,
            gender='Male',
            contact_number='4445556666',
            address='Brooklyn, NY',
            created_by=self.user2
        )

        self.mappings_url = reverse('mapping-list-create')

    def test_unauthenticated_mapping_access_denied(self):
        response = self.client.get(self.mappings_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assign_doctor_to_patient_success(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id,
            'notes': 'Initial neurological assessment'
        }
        response = self.client.post(self.mappings_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['patient']['id'], self.patient1.id)
        self.assertEqual(response.data['doctor']['id'], self.doctor1.id)
        self.assertEqual(response.data['notes'], 'Initial neurological assessment')

    def test_assign_doctor_to_unowned_patient_rejected(self):
        # User 1 tries to assign doctor to User 2's patient
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient': self.patient2.id,
            'doctor': self.doctor1.id
        }
        response = self.client.post(self.mappings_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', response.data['details'])

    def test_duplicate_mapping_rejected(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id
        }
        # First assignment succeeds
        res1 = self.client.post(self.mappings_url, payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Duplicate assignment fails
        res2 = self.client.post(self.mappings_url, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor1)
        PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.mappings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_doctors_assigned_to_specific_patient(self):
        PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor1)
        patient_mappings_url = reverse('mapping-detail-delete', kwargs={'id': self.patient1.id})

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(patient_mappings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['doctor']['name'], 'Dr. Strange')

    def test_delete_mapping_by_id(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient1, doctor=self.doctor1)
        delete_url = reverse('mapping-detail-delete', kwargs={'id': mapping.id})

        # User 2 cannot delete user 1's mapping
        self.client.force_authenticate(user=self.user2)
        res_fail = self.client.delete(delete_url)
        self.assertEqual(res_fail.status_code, status.HTTP_404_NOT_FOUND)

        # User 1 successfully deletes mapping
        self.client.force_authenticate(user=self.user1)
        res_success = self.client.delete(delete_url)
        self.assertEqual(res_success.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class EndToEndHealthcareWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_complete_healthcare_workflow(self):
        # 0. Health check endpoint (Public)
        health_resp = self.client.get(reverse('health-check'))
        self.assertEqual(health_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(health_resp.data['status'], 'healthy')
        self.assertEqual(health_resp.data['database'], 'connected')

        # 0.1 OpenAPI schema endpoint
        schema_resp = self.client.get(reverse('schema'))
        self.assertEqual(schema_resp.status_code, status.HTTP_200_OK)

        # 1. Register a new user
        reg_resp = self.client.post(
            reverse('register'),
            {
                'name': 'Dr. Sarah Connor',
                'email': 'sarah@healthcare.org',
                'password': 'SuperPassword2026!'
            },
            format='json'
        )
        self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reg_resp.data['user']['email'], 'sarah@healthcare.org')

        # 2. Log in and acquire JWT tokens
        login_resp = self.client.post(
            reverse('login'),
            {
                'email': 'sarah@healthcare.org',
                'password': 'SuperPassword2026!'
            },
            format='json'
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        access_token = login_resp.data['access']
        refresh_token = login_resp.data['refresh']
        self.assertTrue(bool(access_token))

        # Set Bearer token in client authorization header
        auth_header = f'Bearer {access_token}'
        self.client.credentials(HTTP_AUTHORIZATION=auth_header)

        # 3. Create a patient
        patient_resp = self.client.post(
            reverse('patient-list-create'),
            {
                'name': 'John Reese',
                'age': 45,
                'gender': 'Male',
                'contact_number': '+1-555-8371',
                'address': 'Subway 8th Street Station, NY',
                'medical_history': 'Prior gunshot wound, fully recovered'
            },
            format='json'
        )
        self.assertEqual(patient_resp.status_code, status.HTTP_201_CREATED)
        patient_id = patient_resp.data['id']
        self.assertEqual(patient_resp.data['name'], 'John Reese')

        # 3.1 Verify paginated patient list
        patients_list_resp = self.client.get(reverse('patient-list-create'))
        self.assertEqual(patients_list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patients_list_resp.data['count'], 1)

        # 4. Create a doctor
        doctor_resp = self.client.post(
            reverse('doctor-list-create'),
            {
                'name': 'Harold Finch',
                'specialization': 'Neuropsychiatry',
                'phone': '+1-555-4920',
                'email': 'finch@iff-solutions.org',
                'experience_years': 25
            },
            format='json'
        )
        self.assertEqual(doctor_resp.status_code, status.HTTP_201_CREATED)
        doctor_id = doctor_resp.data['id']
        self.assertEqual(doctor_resp.data['name'], 'Harold Finch')

        # 4.1 Verify paginated doctor list
        doctors_list_resp = self.client.get(reverse('doctor-list-create'))
        self.assertEqual(doctors_list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(doctors_list_resp.data['count'], 1)

        # 5. Assign doctor to patient (POST /api/mappings/)
        mapping_resp = self.client.post(
            reverse('mapping-list-create'),
            {
                'patient': patient_id,
                'doctor': doctor_id,
                'notes': 'Assigned for weekly cognitive rehabilitation'
            },
            format='json'
        )
        self.assertEqual(mapping_resp.status_code, status.HTTP_201_CREATED)
        mapping_id = mapping_resp.data['id']
        self.assertEqual(mapping_resp.data['patient']['name'], 'John Reese')
        self.assertEqual(mapping_resp.data['doctor']['name'], 'Harold Finch')

        # 6. Retrieve all mappings (GET /api/mappings/)
        all_mappings_resp = self.client.get(reverse('mapping-list-create'))
        self.assertEqual(all_mappings_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(all_mappings_resp.data), 1)

        # 7. Retrieve doctors assigned to patient (GET /api/mappings/<patient_id>/)
        patient_mappings_resp = self.client.get(
            reverse('mapping-detail-delete', kwargs={'id': patient_id})
        )
        self.assertEqual(patient_mappings_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(patient_mappings_resp.data), 1)
        self.assertEqual(patient_mappings_resp.data[0]['doctor']['id'], doctor_id)

        # 8. Update patient details (PUT /api/patients/<id>/)
        update_patient_resp = self.client.put(
            reverse('patient-detail', kwargs={'id': patient_id}),
            {
                'name': 'John Reese',
                'age': 46,
                'gender': 'Male',
                'contact_number': '+1-555-8371',
                'address': 'Safehouse 4, Brooklyn, NY',
                'medical_history': 'Prior gunshot wound, fully recovered. Regular checkups.'
            },
            format='json'
        )
        self.assertEqual(update_patient_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(update_patient_resp.data['age'], 46)

        # 9. Update doctor details (PUT /api/doctors/<id>/)
        update_doctor_resp = self.client.put(
            reverse('doctor-detail', kwargs={'id': doctor_id}),
            {
                'name': 'Harold Finch, MD, PhD',
                'specialization': 'Neuropsychiatry & Cognitive Science',
                'phone': '+1-555-4920',
                'email': 'finch@iff-solutions.org',
                'experience_years': 26
            },
            format='json'
        )
        self.assertEqual(update_doctor_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(update_doctor_resp.data['experience_years'], 26)

        # 10. Remove doctor from patient (DELETE /api/mappings/<id>/)
        delete_map_resp = self.client.delete(
            reverse('mapping-detail-delete', kwargs={'id': mapping_id})
        )
        self.assertEqual(delete_map_resp.status_code, status.HTTP_200_OK)

        # 11. Delete patient (DELETE /api/patients/<id>/)
        delete_patient_resp = self.client.delete(
            reverse('patient-detail', kwargs={'id': patient_id})
        )
        self.assertEqual(delete_patient_resp.status_code, status.HTTP_200_OK)

        # 12. Delete doctor (DELETE /api/doctors/<id>/)
        delete_doctor_resp = self.client.delete(
            reverse('doctor-detail', kwargs={'id': doctor_id})
        )
        self.assertEqual(delete_doctor_resp.status_code, status.HTTP_200_OK)

        # 13. Logout & Token Blacklist (POST /api/auth/logout/)
        logout_resp = self.client.post(
            reverse('logout'),
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)

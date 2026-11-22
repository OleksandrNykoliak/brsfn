from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import ContactRequest


class ContactRequestTests(TestCase):
    def payload(self, **overrides):
        data = {
            'name': 'Contact Test', 'email': 'contact@example.com',
            'phone': '+39 123 456 789', 'interest': 'volunteer',
            'message': 'I can help with cultural events.', 'consent': 'on',
            'website': '',
        }
        data.update(overrides)
        return data

    def test_valid_contact_is_saved_before_success_redirect(self):
        response = self.client.post('/', self.payload())
        self.assertRedirects(response, '/#newsletter', fetch_redirect_response=False)
        contact = ContactRequest.objects.get()
        self.assertEqual(contact.name, 'Contact Test')
        self.assertEqual(contact.email, 'contact@example.com')
        self.assertEqual(contact.phone, '+39 123 456 789')
        self.assertEqual(contact.interest, ContactRequest.Interest.VOLUNTEER)
        self.assertEqual(contact.message, 'I can help with cultural events.')
        self.assertTrue(contact.consent)
        self.assertEqual(contact.status, ContactRequest.Status.NEW)
        self.assertIsNotNone(contact.created_at)

    def test_hero_link_preselects_volunteering_in_the_same_form(self):
        response = self.client.get('/?interest=volunteer')
        self.assertContains(response, 'href="/?interest=volunteer#newsletter"')
        self.assertContains(response, 'Become a volunteer')
        self.assertContains(response, 'id="contactRequestForm"')
        self.assertContains(response, '<option value="volunteer" selected>Volunteering</option>')
        self.assertEqual(response.context['contact_form']['interest'].value(), 'volunteer')
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_unknown_prefill_defaults_to_updates(self):
        response = self.client.get('/?interest=unrecognised')
        self.assertEqual(response.context['contact_form']['interest'].value(), 'updates')

    def test_invalid_input_is_not_saved_and_values_are_preserved(self):
        for field, value in [('name', ''), ('email', 'invalid'), ('consent', ''), ('interest', 'invalid')]:
            with self.subTest(field=field):
                response = self.client.post('/', self.payload(**{field: value}))
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.context['contact_form'].errors)
                self.assertContains(response, 'I can help with cultural events.', status_code=400)
                self.assertNotContains(response, 'We have received your details', status_code=400)
                self.assertEqual(ContactRequest.objects.count(), 0)

    def test_message_length_is_validated_on_server(self):
        response = self.client.post('/', self.payload(message='a' * 3001))
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.context['contact_form'].errors)
        self.assertFalse(ContactRequest.objects.exists())

    def test_phone_and_message_are_optional(self):
        response = self.client.post('/', self.payload(phone='', message='', interest='updates'))
        self.assertEqual(response.status_code, 302)
        contact = ContactRequest.objects.get()
        self.assertEqual((contact.phone, contact.message, contact.interest), ('', '', 'updates'))

    def test_honeypot_blocks_submission(self):
        response = self.client.post('/', self.payload(website='https://example.com'))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.context['contact_form'].non_field_errors())
        self.assertFalse(ContactRequest.objects.exists())

    def test_public_submission_cannot_set_private_processing_fields(self):
        response = self.client.post('/', self.payload(status='closed', internal_notes='Public note'))
        self.assertEqual(response.status_code, 302)
        contact = ContactRequest.objects.get()
        self.assertEqual(contact.status, ContactRequest.Status.NEW)
        self.assertEqual(contact.internal_notes, '')

    def test_refresh_after_success_does_not_create_duplicate(self):
        response = self.client.post('/', self.payload(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'We have received your details')
        refreshed = self.client.get('/')
        self.assertNotContains(refreshed, 'We have received your details')
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_post_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.get('/')
        self.assertEqual(client.post('/', self.payload()).status_code, 403)
        self.assertFalse(ContactRequest.objects.exists())
        data = self.payload(csrfmiddlewaretoken=client.cookies['csrftoken'].value)
        self.assertEqual(client.post('/', data).status_code, 302)
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_contacts_are_private_and_visible_only_with_admin_permission(self):
        ContactRequest.objects.create(name='Private contact', email='private-contact@example.com', consent=True)
        url = reverse('admin:landing_contactrequest_changelist')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertNotContains(self.client.get('/'), 'private-contact@example.com')
        staff = get_user_model().objects.create_user('contact-reader', is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(url).status_code, 403)
        staff.user_permissions.add(Permission.objects.get(codename='view_contactrequest'))
        self.assertContains(self.client.get(url), 'private-contact@example.com')
        self.assertContains(self.client.get(reverse('admin:index')), 'Contact requests')

    def test_admin_can_process_contact_without_changing_submitted_details(self):
        contact = ContactRequest.objects.create(
            name='<script>alert(1)</script>', email='contact@example.com',
            interest='volunteer', consent=True,
        )
        admin = get_user_model().objects.create_superuser('contact-admin', 'admin@example.com', 'test-password')
        self.client.force_login(admin)
        url = reverse('admin:landing_contactrequest_change', args=[contact.pk])
        response = self.client.get(url)
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
        response = self.client.post(url, {'status': 'in_progress', 'internal_notes': 'Ready for follow-up.'})
        self.assertEqual(response.status_code, 302)
        contact.refresh_from_db()
        self.assertEqual(contact.status, ContactRequest.Status.IN_PROGRESS)
        self.assertEqual(contact.internal_notes, 'Ready for follow-up.')
        self.assertEqual(contact.email, 'contact@example.com')
        self.assertTrue(contact.consent)

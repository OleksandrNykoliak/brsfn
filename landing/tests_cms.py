"""Regression checks for database-backed website content and permissions."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from landing.models import SiteIdentity, SiteLink, SiteMedia, SiteText, SupportTier


class ContentStudioTests(TestCase):
    def test_migration_seeds_editable_content(self):
        self.assertGreater(SiteText.objects.count(), 600)
        self.assertEqual(SupportTier.objects.count(), 6)
        self.assertTrue(SiteIdentity.objects.filter(pk=1).exists())

    def test_home_page_reflects_edited_hero_text(self):
        text = SiteText.objects.get(key='landing.sections.hero.t0003')
        text.text = 'A NEW CULTURAL MESSAGE FOR MILAN'
        text.save()
        response = self.client.get(reverse('homeview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A NEW CULTURAL MESSAGE FOR MILAN')

    def test_escaped_text_cannot_insert_untrusted_html(self):
        text = SiteText.objects.get(key='landing.sections.hero.t0003')
        text.text = '<script>alert(1)</script>'
        text.save()
        response = self.client.get(reverse('homeview'))
        self.assertNotContains(response, '<script>alert(1)</script>', html=False)
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')

    def test_support_details_and_membership_are_database_backed(self):
        identity = SiteIdentity.objects.get(pk=1)
        identity.swift = 'NEWBANKCODE'
        identity.save()
        tier = SupportTier.objects.order_by('display_order').first()
        tier.name = 'Updated donation level'
        tier.save()
        response = self.client.get(reverse('support'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NEWBANKCODE')
        self.assertContains(response, 'Updated donation level')

    def test_media_and_links_can_be_changed_without_template_edits(self):
        media = SiteMedia.objects.get(key='landing.sections.hero.m0001')
        media.external_url = 'https://example.com/sample.svg'
        media.save()
        link = SiteLink.objects.order_by('id').first()
        link.url = 'https://example.com/new-link'
        link.save()
        response = self.client.get(reverse('homeview'))
        self.assertContains(response, 'https://example.com/sample.svg')

    def test_cms_requires_admin_login(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_admin_index_and_editors(self):
        User = get_user_model()
        User.objects.create_superuser('editor', 'editor@example.com', 'test-only-password')
        self.client.login(username='editor', password='test-only-password')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Content Studio')
        response = self.client.get(reverse('admin:landing_sitetext_changelist'))
        self.assertEqual(response.status_code, 200)

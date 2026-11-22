"""Bilingual page, form, CMS and navigation integration tests."""
import importlib
from datetime import date
from types import SimpleNamespace

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import translation

from .localization import italian_catalog
from .models import (
    BookClubMeeting, BookClubMeetingPhoto, ContactRequest, Event, EventGalleryImage,
    FAQ, FestivalEdition, FestivalEditionPhoto, MediaMention, Partner, PartnerCredit,
    Project, ProjectGalleryImage, SiteIdentity, SiteText, SupportTier, TeamMember,
)
from .templatetags.boristene_cms import _defaults


class ItalianWebsiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            title='Sample project', title_it='Progetto di esempio', slug='sample',
            category=Project.ANNUAL, short_description='English summary',
            short_description_it='Sintesi italiana', description='English project report',
            description_it='Resoconto italiano del progetto', location='Milan', location_it='Milano',
            goal='English objective', goal_it='Obiettivo italiano',
        )
        ProjectGalleryImage.objects.create(
            project=cls.project, image='projects/gallery/sample.jpg',
            caption='English caption', caption_it='Didascalia italiana',
        )
        cls.event = Event.objects.create(
            project=cls.project, title='English event', title_it='Evento italiano',
            description='English event report', description_it='Resoconto italiano dell’evento',
            date=date(2030, 5, 12), registration_type=Event.TICKETS,
            registration_url='https://example.com/tickets', is_confirmed=True,
        )
        EventGalleryImage.objects.create(event=cls.event, image='events/sample.jpg', caption_it='Foto italiana')
        cls.edition = FestivalEdition.objects.create(
            project=cls.project, year=2030, title='English edition', title_it='Edizione italiana',
            description='English edition report', description_it='Resoconto italiano dell’edizione',
        )
        FestivalEditionPhoto.objects.create(edition=cls.edition, image='festivals/sample.jpg', caption='Photo', caption_it='Foto del festival')
        cls.book_project = Project.objects.create(title='Book project', slug='book-project', category=Project.MONTHLY, short_description='Books')
        cls.meeting = BookClubMeeting.objects.create(
            project=cls.book_project, title='English meeting', title_it='Incontro italiano',
            report='English meeting report', report_it='Resoconto italiano dell’incontro', date=date(2030, 5, 12),
        )
        BookClubMeetingPhoto.objects.create(meeting=cls.meeting, image='bookclub/sample.jpg', caption='Photo', caption_it='Foto dell’incontro')
        TeamMember.objects.create(name='Example Name', role='English role', role_it='Ruolo italiano', bio='English bio', bio_it='Biografia italiana')
        FAQ.objects.create(question='English question?', question_it='Domanda italiana?', answer='English answer', answer_it='Risposta italiana')
        cls.level = SupportTier.objects.create(
            name='English membership', name_it='Adesione italiana', period='/year', period_it='/anno',
            benefits_lines='English benefit one\nEnglish benefit two', benefits_lines_it='Vantaggio uno\nVantaggio due',
        )
        for number in range(13):
            MediaMention.objects.create(outlet='Example News', headline=f'English headline {number}',
                headline_it=f'Titolo italiano {number}', excerpt='English excerpt', excerpt_it='Estratto italiano')

    def setUp(self):
        translation.activate('en')

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_all_public_page_types_have_italian_copy_and_language_metadata(self):
        paths = [
            ('/', 'Diventa volontario'), ('/projects/', 'Progetto di esempio'),
            ('/projects/sample/', 'Resoconto italiano del progetto'),
            (f'/events/{self.event.pk}/', 'Resoconto italiano dell’evento'),
            ('/projects/sample/editions/2030/', 'Resoconto italiano dell’edizione'),
            (f'/projects/book-project/meetings/{self.meeting.pk}/', 'Resoconto italiano dell’incontro'),
            ('/about/', 'Ruolo italiano'), ('/join/', 'Come partecipare'),
            ('/support/', 'Adesione italiana'),
        ]
        for path, expected in paths:
            with self.subTest(path=path):
                response = self.client.get('/it' + path)
                self.assertContains(response, expected)
                self.assertContains(response, '<html lang="it">')
                self.assertContains(response, 'hreflang="en"')
                self.assertContains(response, 'hreflang="it"')
                self.assertEqual(response.headers['Content-Language'], 'it')

    def test_english_pages_preserve_original_fields_and_existing_urls(self):
        self.assertContains(self.client.get('/projects/sample/'), 'English project report')
        self.assertNotContains(self.client.get('/projects/sample/'), 'Resoconto italiano del progetto')
        self.assertContains(self.client.get('/'), 'Become a volunteer')
        self.assertEqual(self.client.get('/en/').status_code, 404)

    def test_language_switch_has_real_targets_in_both_directions(self):
        english = self.client.get('/projects/sample/?media_page=2')
        self.assertContains(english, 'name="next" value="/it/projects/sample/?media_page=2"')
        italian = self.client.post('/i18n/setlang/', {
            'language':'it', 'next':'/it/projects/sample/?media_page=2#gallery',
        })
        self.assertEqual(italian.status_code, 302)
        self.assertEqual(italian.url, '/it/projects/sample/?media_page=2#gallery')
        self.assertEqual(italian.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'it')
        page = self.client.get('/it/projects/sample/?media_page=2')
        self.assertContains(page, 'name="next" value="/projects/sample/?media_page=2"')
        english = self.client.post('/i18n/setlang/', {
            'language':'en', 'next':'/projects/sample/?media_page=2#gallery',
        })
        self.assertEqual(english.url, '/projects/sample/?media_page=2#gallery')
        self.assertEqual(english.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'en')

    def test_switch_requires_csrf_and_rejects_external_redirects(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/i18n/setlang/', {'language':'it','next':'/it/'}).status_code, 403)
        response = self.client.post('/i18n/setlang/', {'language':'it','next':'https://example.com/untrusted'})
        self.assertEqual(response.url, '/it/')

    def test_navigation_and_donation_links_keep_italian_language(self):
        response = self.client.get('/it/')
        for path in ['/it/projects/', '/it/support/', '/it/support/#bank-details', '/it/?interest=volunteer#newsletter']:
            self.assertContains(response, f'href="{path}"')
        self.assertNotContains(response, 'data-lang="ua"')
        self.assertContains(response, 'lang="it" aria-label="Passa all’italiano" aria-pressed="true"')
        self.assertContains(response, '"closeMenu": "Chiudi il menu"')

    def test_italian_media_pagination_keeps_page_and_translated_labels(self):
        first = self.client.get('/it/')
        self.assertEqual(len(first.context['media_mentions']), 12)
        self.assertContains(first, 'Pagine della rassegna stampa')
        self.assertContains(first, '?media_page=2#media')
        second = self.client.get('/it/?media_page=2')
        self.assertEqual(len(second.context['media_mentions']), 1)
        self.assertContains(second, 'Titolo italiano')
        self.assertNotContains(second, 'English headline')

    def test_italian_gallery_captions_and_event_actions_are_translated(self):
        response = self.client.get('/it/projects/sample/')
        self.assertContains(response, 'data-caption="Didascalia italiana"')
        self.assertContains(response, 'Apri la foto 1 di 1')
        self.assertContains(response, 'Foto successiva')
        event = self.client.get(f'/it/events/{self.event.pk}/')
        self.assertContains(event, 'Acquista i biglietti')
        self.assertContains(event, 'Foto italiana')
        self.assertContains(event, '12 Maggio 2030')

    def test_italian_faq_team_and_support_benefits_are_translated(self):
        home = self.client.get('/it/')
        for expected in ['Domanda italiana?', 'Risposta italiana', 'Ruolo italiano', 'Vantaggio uno', '/anno']:
            self.assertContains(home, expected)
        self.assertNotContains(home, 'English benefit one')

    def test_italian_contact_validation_and_success_redirect(self):
        page = self.client.get('/it/?interest=volunteer')
        self.assertContains(page, '<option value="volunteer" selected>Volontariato</option>')
        self.assertContains(page, 'action="/it/#newsletter"')
        invalid = self.client.post('/it/', {'name':'Contatto', 'email':'invalid', 'interest':'volunteer'})
        self.assertEqual(invalid.status_code, 400)
        self.assertContains(invalid, 'Inserisci un indirizzo email valido.', status_code=400)
        self.assertContains(invalid, 'Questo campo è obbligatorio.', status_code=400)
        self.assertFalse(ContactRequest.objects.exists())
        valid = self.client.post('/it/', {'name':'Contatto', 'email':'contatto@example.com','interest':'volunteer','consent':'on'}, follow=True)
        self.assertEqual(valid.redirect_chain, [('/it/#newsletter',302)])
        self.assertContains(valid, 'Abbiamo ricevuto i tuoi contatti')
        self.assertEqual(ContactRequest.objects.get().name, 'Contatto')

    def test_localization_falls_back_without_mutating_the_original(self):
        with translation.override('it'):
            self.assertEqual(self.project.localized.title, 'Progetto di esempio')
            self.assertEqual(self.project.title, 'Sample project')
            self.project.title_it=''
            self.assertEqual(self.project.localized.title, 'Sample project')
        with translation.override('en'):
            self.assertEqual(self.level.benefits, ['English benefit one','English benefit two'])

    def test_page_text_changes_are_independent_and_immediate(self):
        text = SiteText.objects.get(key='landing.sections.newsletter.t0001')
        text.text_it='Messaggio modificato'; text.save()
        self.assertContains(self.client.get('/it/'), 'Messaggio modificato')
        self.assertContains(self.client.get('/'), 'Stay in touch')
        text.text=''; text.text_it=''; text.save()
        self.assertNotContains(self.client.get('/it/'), 'Messaggio modificato')

    def test_split_headings_and_project_brand_have_contextual_translations(self):
        response=self.client.get('/it/')
        self.assertContains(response, 'Dicono')
        self.assertEqual(SiteText.objects.get(key='landing.sections.media.t0003').text_it, 'di noi')
        self.assertNotContains(response, 'Unbreakable\n            Ucraina')
        self.assertEqual(SiteText.objects.get(key='landing.sections.hero.t0010').text_it, 'Ukraine')

    def test_all_original_cms_phrases_have_italian_defaults(self):
        catalog=italian_catalog()
        for key, entry in _defaults()['texts'].items():
            with self.subTest(key=key):
                self.assertIn(entry['value'], catalog)

    def test_italian_admin_fields_are_available_for_new_and_existing_content(self):
        user=get_user_model().objects.create_superuser('italian-editor','editor@example.com','test-password')
        request=RequestFactory().get('/admin/'); request.user=user
        for Model, field in [(Project,'title_it'),(MediaMention,'headline_it'),(SiteText,'text_it'),(SupportTier,'benefits_lines_it'),(SiteIdentity,'representative_it')]:
            with self.subTest(model=Model.__name__):
                editor=admin.site._registry[Model]
                self.assertIn(field, editor.get_form(request).base_fields)
                self.assertIn('Italiano', [name for name,_ in editor.get_fieldsets(request)])

    def test_seed_preserves_custom_italian_and_skips_unknown_source(self):
        known=SiteText.objects.get(key='landing.header.t0004')
        known.text_it='Progetti personalizzati';known.save()
        unknown=SiteText.objects.create(key='test.new.copy',page='Home',section='Test',label='Test',text='Unmapped new source')
        migration=importlib.import_module('landing.migrations.0010_italian_content')
        migration.seed_italian_content(apps,SimpleNamespace(connection=connection))
        known.refresh_from_db();unknown.refresh_from_db()
        self.assertEqual(known.text_it,'Progetti personalizzati')
        self.assertEqual(unknown.text_it,'')

    def test_partner_credit_uses_localized_project_title(self):
        partner=Partner.objects.create(name='Sample Partner')
        credit=PartnerCredit.objects.create(partner=partner,project=self.project)
        with translation.override('it'):
            self.assertEqual(credit.supported_title,'Progetto di esempio')
            self.assertEqual(credit.get_absolute_url(),'/it/projects/sample/')

from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import (Event, Project, ProjectSupporter, Partner, PartnerCredit,
                     FestivalEdition, BookClubMeeting, EventGalleryImage)


class LandingPagesTests(TestCase):
	def test_home_page_renders_successfully(self):
		response = self.client.get(reverse('homeview'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Next event to be announced')

	def test_public_routes_are_defined(self):
		for name in ('homeview', 'projects', 'about', 'join', 'support'):
			self.assertTrue(reverse(name).startswith('/'))

	def test_dynamic_project_route_is_buildable(self):
		project = Project.objects.create(
			title='Test Project',
			slug='test-project',
			short_description='A test project.',
		)
		self.assertEqual(
			reverse('project-detail', kwargs={'slug': project.slug}),
			'/projects/test-project/',
		)

	def test_project_card_and_detail_show_editorial_fields(self):
		project = Project.objects.create(
			title='Festival Project',
			slug='festival-project',
			short_description='A short card description.',
			date_label='11–12 September 2026',
			location='Linz, Austria',
			goal='Reach 50,000 people.',
			budget='€70,000',
			partners='Ars Electronica, SARAVÁ',
			participants='Svitlana Tereshchenko',
			website_text='A highlighted project note.',
			description='The complete project story.',
			is_featured=True,
		)
		card_response = self.client.get(reverse('homeview'))
		detail_response = self.client.get(reverse('project-detail', kwargs={'slug': project.slug}))
		self.assertContains(card_response, '11–12 September 2026')
		self.assertContains(card_response, 'Linz, Austria')
		for text in ('Reach 50,000 people.', '€70,000', 'Ars Electronica, SARAVÁ', 'A highlighted project note.', 'The complete project story.'):
			self.assertContains(detail_response, text)

	def test_projects_page_groups_projects_and_offers_event_registration(self):
		project_data = (
			('UNBREAKABLE UKRAINE', Project.FLAGSHIP),
			('Ukrainian Culture Festival UCRAINA è UCRAINA', Project.ANNUAL),
			('BOOK CLUB BORISTENE', Project.MONTHLY),
			('Community partnership', Project.COLLABORATION),
		)
		for title, category in project_data:
			Project.objects.create(
				title=title,
				short_description=f'{title} project description.',
				category=category,
			)

		Event.objects.create(
			title='Festival opening',
			date=date(2027, 5, 1),
			location='Milan',
			description='A day of Ukrainian culture.',
			registration_url='https://example.com/register',
		)

		response = self.client.get(reverse('projects'))
		home_response = self.client.get(reverse('homeview'))
		self.assertEqual(response.status_code, 200)
		for title in ('UNBREAKABLE UKRAINE', 'Ukrainian Culture Festival UCRAINA è UCRAINA', 'BOOK CLUB BORISTENE', 'Community partnership'):
			self.assertContains(response, title)
			self.assertContains(home_response, title)
		for tab_title in ('Flagship project', 'Annual project', 'Monthly project', 'Other Projects &amp; Collaborations'):
			self.assertContains(home_response, tab_title)
		self.assertContains(home_response, 'Other Projects &amp; Collaborations')
		self.assertContains(home_response, 'Upcoming Events')
		self.assertNotContains(home_response, 'Upcoming Events</button>')
		self.assertNotContains(home_response, 'Annual festival</button>')
		self.assertNotContains(home_response, 'Book club</button>')
		self.assertContains(response, 'Upcoming events')
		self.assertContains(response, 'Festival opening')
		self.assertContains(response, 'href="https://example.com/register"')
		self.assertContains(response, 'Register now')
		self.assertContains(home_response, 'Festival opening')
		self.assertContains(home_response, 'href="https://example.com/register"')
		self.assertContains(home_response, 'Register now')

	def test_event_registration_action_is_only_shown_when_a_url_exists(self):
		event = Event.objects.create(
			title='Project gathering',
			date=date(2027, 5, 1),
		)
		response = self.client.get(reverse('projects'))
		self.assertContains(response, event.title)
		self.assertNotContains(response, 'Register now')

	def test_project_event_registration_link_appears_on_home_and_detail_pages(self):
		project = Project.objects.create(
			title='Festival Project',
			slug='festival-project',
			short_description='A festival project.',
		)
		Event.objects.create(
			title='Festival event',
			date=date(2027, 5, 1),
			project=project,
			registration_url='https://example.com/festival',
		)

		for url in (
			reverse('homeview'),
			reverse('project-detail', kwargs={'slug': project.slug}),
		):
			response = self.client.get(url)
			self.assertContains(response, 'href="https://example.com/festival"')
			self.assertContains(response, 'Register now')

	def test_ticket_action_uses_ticket_label_and_expired_events_have_no_cta(self):
		Event.objects.create(
			title='Festival tickets',
			date=date(2027, 5, 1),
			registration_type=Event.TICKETS,
			registration_url='https://example.com/tickets',
		)
		Event.objects.create(
			title='Past event with expired ticket link',
			date=date(2000, 5, 1),
			registration_type=Event.TICKETS,
			registration_url='https://example.com/expired-tickets',
		)

		response = self.client.get(reverse('projects'))
		self.assertContains(response, 'Buy tickets')
		self.assertContains(response, 'href="https://example.com/tickets"')
		self.assertNotContains(response, 'href="https://example.com/expired-tickets"')

	def test_project_detail_shows_project_specific_supporters_and_other_project_images(self):
		project = Project.objects.create(
			title='Featured project',
			slug='featured-project',
			short_description='The featured project.',
		)
		other_project = Project.objects.create(
			title='Related project',
			slug='related-project',
			short_description='A related project.',
			image_url='https://example.com/related.jpg',
		)
		ProjectSupporter.objects.create(
			project=project,
			name='Community Patron',
			role=ProjectSupporter.PATRON,
		)
		ProjectSupporter.objects.create(
			project=project,
			name='Cultural Sponsor',
			role=ProjectSupporter.SPONSOR,
			logo_url='https://example.com/sponsor.png',
			website_url='https://example.com/sponsor',
		)

		response = self.client.get(reverse('project-detail', kwargs={'slug': project.slug}))
		self.assertContains(response, 'Patrons &amp; Sponsors')
		self.assertContains(response, 'Community Patron')
		self.assertContains(response, 'Cultural Sponsor')
		self.assertContains(response, 'https://example.com/sponsor.png')
		self.assertContains(response, 'https://example.com/related.jpg')
		self.assertContains(response, other_project.title)
		self.assertContains(response, 'Explore more projects')
		self.assertContains(response, 'Support this project')


class EditorialContentTests(TestCase):
    def test_support_tiers_are_exactly_six_and_have_approved_prices(self):
        from .support import SUPPORT_LEVELS
        self.assertEqual([tier['price'] for tier in SUPPORT_LEVELS],
                         ['', 'From €5', '€50', '€100', '€350', '€500'])
        self.assertEqual([tier['name'] for tier in SUPPORT_LEVELS], [
            'One-time donation', 'Monthly donation', 'Membership — Socio',
            'Gold Membership', 'Patron — Mecenate', 'Grand Patron',
        ])
        for tier in SUPPORT_LEVELS[:2]:
            self.assertFalse(tier['benefits'])
        page = self.client.get(reverse('support'))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, '€500')

    def test_partner_link_targets_supported_project_only_if_mapped(self):
        project = Project.objects.create(title='Project A', slug='project-a',
                                         short_description='A supported project')
        partner = Partner.objects.create(name='Partner A', logo_url='https://example.com/a.png')
        home = self.client.get(reverse('homeview'))
        self.assertContains(home, 'Partner A')
        self.assertNotContains(home, 'Partner A: Project A')
        PartnerCredit.objects.create(partner=partner, project=project)
        home = self.client.get(reverse('homeview'))
        self.assertContains(home, 'See what Partner A supported')
        detail = self.client.get(project.get_absolute_url())
        self.assertContains(detail, 'Partner A')

    def test_event_link_and_report_page(self):
        event = Event.objects.create(title='Book fair', date=date(2027, 5, 1),
                                     description='Cultural event')
        response = self.client.get(reverse('event-detail', kwargs={'pk': event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Photo report')
        self.assertContains(response, 'Photos from this event will be published')
        listing = self.client.get(reverse('homeview'))
        self.assertContains(listing, reverse('event-detail', kwargs={'pk': event.pk}))

    def test_festival_editions_and_monthly_meeting_routes(self):
        annual = Project.objects.create(title='Annual festival', slug='annual-festival',
                                        category=Project.ANNUAL,
                                        short_description='Yearly festival')
        edition = FestivalEdition.objects.create(project=annual, year=2026,
                                                 description='Festival recap')
        month = Project.objects.create(title='Book club', slug='book-club',
                                       category=Project.MONTHLY,
                                       short_description='Our monthly book club')
        meeting = BookClubMeeting.objects.create(project=month, date=date(2026, 9, 12),
                                                 title='Autumn meeting', report='Books discussed')
        for url, text in [(annual.get_absolute_url(), 'Festival editions'),
                          (edition.get_absolute_url(), 'Festival recap'),
                          (month.get_absolute_url(), 'Meeting reports'),
                          (meeting.get_absolute_url(), 'Books discussed')]:
            self.assertContains(self.client.get(url), text)
        self.assertEqual(self.client.get('/projects/not-a-project/editions/2026/').status_code, 404)
        self.assertEqual(self.client.get('/projects/annual-festival/meetings/1/').status_code, 404)

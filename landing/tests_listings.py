from datetime import timedelta
import re

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .forms import ProjectAdminForm
from .models import MediaMention, Project


class ProjectOrderingTests(TestCase):
    def make_project(self, title, **kwargs):
        return Project.objects.create(title=title, short_description=title, **kwargs)

    def test_newest_projects_come_first_regardless_of_legacy_order(self):
        older = self.make_project('Older', display_order=0)
        newer = self.make_project('Newer', display_order=999)
        Project.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))
        self.assertEqual(list(Project.objects.all()), [newer, older])
        self.assertEqual(Project.ordered_for_display(), [newer, older])

    def test_pins_keep_exact_positions_when_new_projects_are_added(self):
        first = self.make_project('First pin', is_pinned=True, pinned_position=1)
        third = self.make_project('Third pin', is_pinned=True, pinned_position=3)
        old = self.make_project('Old')
        recent = self.make_project('Recent')
        self.assertEqual(Project.ordered_for_display(), [first, recent, third, old])
        newest = self.make_project('Newest')
        self.assertEqual(Project.ordered_for_display(), [first, newest, third, recent, old])
        for url in ('/', '/projects/'):
            response = self.client.get(url)
            ids = [int(pk) for pk in re.findall(r'data-project-id="(\d+)"', response.content.decode())]
            self.assertEqual(ids, [first.pk, newest.pk, third.pk, recent.pk, old.pk])

    def test_unpinning_restores_chronological_order(self):
        older = self.make_project('Older pinned', is_pinned=True, pinned_position=1)
        newer = self.make_project('Newer')
        older.is_pinned = False
        older.save(update_fields=['is_pinned'])
        self.assertEqual(Project.ordered_for_display(), [newer, older])

    def test_inactive_pins_do_not_occupy_positions(self):
        self.make_project('Inactive', is_active=False, is_pinned=True, pinned_position=1)
        active = self.make_project('Active pinned', is_pinned=True, pinned_position=1)
        newest = self.make_project('Newest')
        self.assertEqual(Project.ordered_for_display(), [active, newest])

    def test_positions_beyond_list_end_stay_in_order(self):
        end = self.make_project('End pin', is_pinned=True, pinned_position=5)
        later = self.make_project('Later pin', is_pinned=True, pinned_position=9)
        regular = self.make_project('Regular')
        self.assertEqual(Project.ordered_for_display(), [regular, end, later])
        for i in range(8):
            self.make_project('Added '+str(i))
        ordered = Project.ordered_for_display()
        self.assertEqual(ordered[4], end)
        self.assertEqual(ordered[8], later)

    def test_pin_requires_positive_position(self):
        for position in (None, 0):
            project = Project(title='Invalid pin', short_description='Invalid', is_pinned=True, pinned_position=position)
            with self.assertRaises(ValidationError) as error:
                project.full_clean()
            self.assertIn('pinned_position', error.exception.message_dict)

    def test_conflicting_pin_is_rejected_by_form_and_database(self):
        self.make_project('Existing pin', is_pinned=True, pinned_position=2)
        form = ProjectAdminForm(data={
            'title': 'Conflicting pin', 'slug': 'conflicting-pin',
            'category': Project.COLLABORATION, 'short_description': 'Conflict',
            'status': Project.CURRENT, 'is_active': True, 'is_pinned': True,
            'pinned_position': 2, 'display_order': 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('pinned_position', form.errors)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_project('Database conflict', is_pinned=True, pinned_position=2)

    def test_tied_creation_dates_have_deterministic_order(self):
        older = self.make_project('First created')
        newer = self.make_project('Second created')
        Project.objects.all().update(created_at=timezone.now())
        self.assertEqual(Project.ordered_for_display(), [newer, older])


class MediaPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        MediaMention.objects.bulk_create([
            MediaMention(outlet='Test outlet', headline='News '+str(i), display_order=i)
            for i in range(17)
        ])
        MediaMention.objects.create(outlet='Hidden', headline='Hidden news', is_active=False)

    def test_twelve_items_then_five_without_overlap(self):
        first = self.client.get('/')
        second = self.client.get('/?media_page=2')
        first_ids = [int(pk) for pk in re.findall(r'data-media-id="(\d+)"', first.content.decode())]
        second_ids = [int(pk) for pk in re.findall(r'data-media-id="(\d+)"', second.content.decode())]
        self.assertEqual(len(first_ids), 12)
        self.assertEqual(len(second_ids), 5)
        self.assertFalse(set(first_ids) & set(second_ids))
        self.assertEqual(set(first_ids + second_ids), set(MediaMention.objects.filter(is_active=True).values_list('pk', flat=True)))
        self.assertNotContains(first, 'Hidden news')
        self.assertContains(first, '?media_page=2#media')
        self.assertContains(first, '1–12 / 17')
        self.assertContains(second, '13–17 / 17')
        self.assertContains(second, 'aria-current="page" aria-label="Page 2"')

    def test_pagination_preserves_other_query_parameters(self):
        response = self.client.get('/?campaign=test')
        self.assertContains(response, '?campaign=test&amp;media_page=2#media')

    def test_invalid_page_values_do_not_break_home(self):
        for value, expected in [('invalid', 1), ('999', 2)]:
            response = self.client.get('/', {'media_page': value})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['media_page'].number, expected)

    def test_empty_or_single_page_hides_pagination(self):
        MediaMention.objects.all().delete()
        response = self.client.get('/')
        self.assertNotContains(response, 'aria-label="Media pages"')
        MediaMention.objects.create(outlet='One item', headline='One story')
        response = self.client.get('/')
        self.assertContains(response, 'One story')
        self.assertNotContains(response, 'aria-label="Media pages"')

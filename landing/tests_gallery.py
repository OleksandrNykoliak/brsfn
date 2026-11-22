from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Project, ProjectGalleryImage


def photo_file(name):
    output = BytesIO()
    Image.new('RGB', (40, 30), '#fd7715').save(output, format='PNG')
    return SimpleUploadedFile(name, output.getvalue(), content_type='image/png')


class ProjectGalleryTests(TestCase):
    def setUp(self):
        self.media_root = self.enterContext(TemporaryDirectory())
        self.enterContext(self.settings(MEDIA_ROOT=self.media_root))
        self.editor = get_user_model().objects.create_superuser('gallery-editor', 'gallery@example.com', 'test-password')
        self.client.force_login(self.editor)
        self.project = Project.objects.create(
            title='UNBREAKABLE UKRAINE', slug='unbreakable-ukraine',
            category=Project.FLAGSHIP, short_description='Ukrainian heritage',
            description='The full project story.',
        )

    def project_data(self, files):
        return {
            'title': self.project.title, 'slug': self.project.slug,
            'category': self.project.category, 'short_description': self.project.short_description,
            'description': self.project.description, 'status': Project.CURRENT,
            'is_active': 'on', 'display_order': '0', 'gallery_uploads': files,
            'gallery_images-TOTAL_FORMS': '0', 'gallery_images-INITIAL_FORMS': '0',
            'gallery_images-MIN_NUM_FORMS': '0', 'gallery_images-MAX_NUM_FORMS': '1000',
            'supporters-TOTAL_FORMS': '0', 'supporters-INITIAL_FORMS': '0',
            'supporters-MIN_NUM_FORMS': '0', 'supporters-MAX_NUM_FORMS': '1000',
        }

    def test_admin_uploads_multiple_photos_and_appends_to_existing_gallery(self):
        original = ProjectGalleryImage.objects.create(project=self.project, image=photo_file('original.png'), display_order=7)
        data = self.project_data([photo_file('one.png'), photo_file('two.png'), photo_file('three.png')])
        data.update({
            'gallery_images-TOTAL_FORMS': '1', 'gallery_images-INITIAL_FORMS': '1',
            'gallery_images-0-id': str(original.pk), 'gallery_images-0-project': str(self.project.pk),
            'gallery_images-0-display_order': '7', 'gallery_images-0-caption': 'Original photo',
        })
        response = self.client.post(reverse('admin:landing_project_change', args=[self.project.pk]), data)
        self.assertEqual(response.status_code, 302)
        photos = list(self.project.gallery_images.all())
        self.assertEqual([photo.display_order for photo in photos], [7, 8, 9, 10])
        self.assertEqual(photos[0].caption, 'Original photo')
        self.assertTrue(all(Path(photo.image.path).is_file() for photo in photos))

    def test_invalid_image_prevents_partial_gallery_upload(self):
        invalid = SimpleUploadedFile('invalid.png', b'not an image', content_type='image/png')
        response = self.client.post(
            reverse('admin:landing_project_change', args=[self.project.pk]),
            self.project_data([photo_file('valid.png'), invalid]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('gallery_uploads', response.context['adminform'].form.errors)
        self.assertEqual(self.project.gallery_images.count(), 0)
        self.assertEqual(list(Path(self.media_root).rglob('*.png')), [])

    def test_gallery_uses_only_its_project_photos_below_the_cover(self):
        second = ProjectGalleryImage.objects.create(project=self.project, image=photo_file('second.png'), caption='Second photo', display_order=20)
        first = ProjectGalleryImage.objects.create(project=self.project, image=photo_file('first.png'), caption='<strong>First photo</strong>', display_order=10)
        other = Project.objects.create(title='Other project', short_description='Other')
        private_photo = ProjectGalleryImage.objects.create(project=other, image=photo_file('other.png'), caption='Other gallery photo')
        response = self.client.get(self.project.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertContains(response, 'data-project-gallery')
        self.assertContains(response, '&lt;strong&gt;First photo&lt;/strong&gt;')
        self.assertNotContains(response, private_photo.image.url)
        self.assertLess(html.index('editorial-project-cover'), html.index('id="gallery"'))
        self.assertLess(html.index('id="gallery"'), html.index('The full project story.'))
        self.assertLess(html.index('href="'+first.image.url+'"'), html.index('href="'+second.image.url+'"'))
        self.assertContains(response, 'src="'+first.image.url+'"', count=2)
        self.assertNotContains(self.client.get(other.get_absolute_url()), 'data-caption="Second photo"')

    def test_bulk_upload_respects_gallery_add_permission(self):
        staff = get_user_model().objects.create_user('project-editor', is_staff=True)
        staff.user_permissions.add(Permission.objects.get(codename='change_project'))
        self.client.force_login(staff)
        response = self.client.post(
            reverse('admin:landing_project_change', args=[self.project.pk]),
            self.project_data([photo_file('restricted.png')]),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.project.gallery_images.count(), 0)

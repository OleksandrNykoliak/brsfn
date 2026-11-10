"""Idempotent page copy seeding. Existing edits are never overwritten."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from landing.models import SiteMedia, SiteLink, SiteText, SiteIdentity


class Command(BaseCommand):
    help = 'Create missing editable page texts/images/links from the original templates; never overwrite edits.'

    def handle(self, *args, **options):
        file = Path(__file__).resolve().parents[2] / 'cms_defaults.json'
        with file.open(encoding='utf-8') as handle:
            defaults = json.load(handle)
        created = {}
        for category, model in [('texts', SiteText), ('media', SiteMedia), ('links', SiteLink)]:
            n = 0
            for key, data in defaults[category].items():
                base = {
                    'page': data['page'], 'section': data['section'],
                    'label': data['label'][:180],
                }
                if category == 'texts':base['text'] = data['value']
                elif category == 'media':base['fallback'] = data['value']
                else:base['url'] = data['value']
                _, was_created = model.objects.get_or_create(key=key, defaults=base)
                n += int(was_created)
            created[category] = n
        SiteIdentity.objects.get_or_create(pk=1)
        self.stdout.write(self.style.SUCCESS('Added missing content only: ' + str(created)))

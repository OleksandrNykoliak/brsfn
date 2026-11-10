"""Add-only CMS migration: does not alter or remove any original models."""
import json
from pathlib import Path

from django.db import migrations, models


def seed_site_content(apps, schema_editor):
    Text = apps.get_model('landing', 'SiteText')
    Media = apps.get_model('landing', 'SiteMedia')
    Link = apps.get_model('landing', 'SiteLink')
    Identity = apps.get_model('landing', 'SiteIdentity')
    Tier = apps.get_model('landing', 'SupportTier')
    file = Path(__file__).resolve().parents[1] / 'cms_defaults.json'
    with file.open(encoding='utf8') as handle:
        defaults = json.load(handle)
    for entry in defaults['texts'].items():
        key, data = entry
        Text.objects.using(schema_editor.connection.alias).get_or_create(
            key=key, defaults={
                'page':data['page'], 'section':data['section'],
                'label':data['label'][:180], 'text':data['value'],
            })
    for key, data in defaults['media'].items():
        Media.objects.using(schema_editor.connection.alias).get_or_create(
            key=key, defaults={
                'page':data['page'], 'section':data['section'],
                'label':data['label'][:180], 'fallback':data['value'],
            })
    for key, data in defaults['links'].items():
        Link.objects.using(schema_editor.connection.alias).get_or_create(
            key=key, defaults={
                'page':data['page'], 'section':data['section'],
                'label':data['label'][:180], 'url':data['value'],
            })
    Identity.objects.using(schema_editor.connection.alias).get_or_create(pk=1)
    tiers = [
        ('One-time donation', '', '', '', 'donation', []),
        ('Monthly donation', 'From €5', '/month', 'Choose comfortable to you amount from 5€ and up', 'donation', []),
        ('Membership — Socio', '€50', '/year', '', 'membership', [
            'Your name featured on our YouTube channel',
            'Possibility of reservation on front-row seating at our events',
            'Priority booking for our events',
            'Three exclusive Zoom meetings per year with members of the Association’s Board and a special guest',
        ]),
        ('Gold Membership', '€100', '/year', '', 'membership', [
            'Personal invitations to our events',
            'Your name featured on our YouTube channel',
            'Reserved front-row seating at our events',
            'Priority booking for our events',
            'Three exclusive Zoom meetings per year with members of the Association’s Board and a special guest',
            'Participation in two dinners per year with the Boristene team and its guest of honour',
        ]),
        ('Patron — Mecenate', '€350', '/year', 'All benefits of the preceding levels, plus', 'patron', [
            'Exclusive events for Patrons and Grand Patrons, including private dinners at the Association founder’s home with special guests, and curated tours of Milan and across Italy exploring Ukrainian traces and their stories',
        ]),
        ('Grand Patron', '€500', '/year', 'All benefits of the preceding levels, plus', 'patron', [
            'The opportunity to contribute to the creation of our events and take an active role as a host or moderator',
        ]),
    ]
    if not Tier.objects.using(schema_editor.connection.alias).exists():
        for n, (name, price, period, subtitle, kind, benefits) in enumerate(tiers, start=1):
            Tier.objects.using(schema_editor.connection.alias).create(
                name=name, price=price, period=period, subtitle=subtitle,
                kind=kind, benefits_lines='\n'.join(benefits), display_order=n * 10,
            )

class Migration(migrations.Migration):
    dependencies = [('landing', '0006_editorial_content_and_credits')]
    operations = [
        migrations.CreateModel(
            name='SiteText',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('key', models.CharField(max_length=220, unique=True)),
                ('page', models.CharField(max_length=90, db_index=True)),
                ('section', models.CharField(max_length=120, db_index=True)),
                ('label', models.CharField(max_length=180)),
                ('text', models.TextField(blank=True, help_text='Plain text. HTML is escaped for safety. Empty text hides the phrase.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ('page', 'section', 'key'), 'verbose_name':'Page text','verbose_name_plural':'Page texts'},
        ),
        migrations.CreateModel(
            name='SiteMedia',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('key', models.CharField(max_length=220, unique=True)),
                ('page', models.CharField(max_length=90, db_index=True)),
                ('section', models.CharField(max_length=120)),
                ('label', models.CharField(max_length=180)),
                ('fallback', models.TextField(help_text='Original static path, or original absolute image URL.')),
                ('image', models.ImageField(upload_to='cms/', blank=True)),
                ('external_url', models.URLField(blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ('page', 'section', 'key'), 'verbose_name':'Page image','verbose_name_plural':'Page images'},
        ),
        migrations.CreateModel(
            name='SiteLink',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('key', models.CharField(max_length=220, unique=True)),
                ('page', models.CharField(max_length=90, db_index=True)),
                ('section', models.CharField(max_length=120)),
                ('label', models.CharField(max_length=180)),
                ('url', models.CharField(max_length=1200)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ('page', 'section', 'key'), 'verbose_name':'Page link','verbose_name_plural':'Page links'},
        ),
        migrations.CreateModel(
            name='SiteIdentity',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('legal_name', models.CharField(default='BORISTENE ETS', max_length=180)),
                ('beneficiary', models.CharField(default='BORISTENE associazione ETS', max_length=180)),
                ('tax_code', models.CharField(default='97971770157', max_length=40)),
                ('legal_form', models.CharField(default='Associazione riconosciuta / Ente del Terzo Settore (ETS), non-profit', max_length=300)),
                ('representative', models.CharField(default='Svetlana Terechtchenko, President', max_length=180)),
                ('registered_address', models.CharField(default='Via Ugo Tarchetti 1, 20121 Milano (MI), Italy', max_length=250)),
                ('short_address', models.CharField(default='Via Ugo Tarchetti 1, 20121 Milano, Italy', max_length=250)),
                ('email', models.EmailField(default='associazione@boristenemilano.com', max_length=254)),
                ('phone', models.CharField(default='+39 331 272 0262', max_length=45)),
                ('iban', models.CharField(default='IT58B0503401727000000003792', max_length=70)),
                ('swift', models.CharField(default='BAPPIT21633', max_length=30)),
                ('bank_name', models.CharField(default='Banco BPM · Milan, Italy', max_length=180)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name':'Association and banking details','verbose_name_plural':'Association and banking details'},
        ),
        migrations.CreateModel(
            name='SupportTier',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=130)),
                ('price', models.CharField(max_length=60, blank=True)),
                ('period', models.CharField(max_length=45, blank=True)),
                ('subtitle', models.TextField(blank=True)),
                ('kind', models.CharField(max_length=20, choices=[('donation', 'Donation'), ('membership', 'Membership'), ('patron', 'Patron')], default='donation')),
                ('benefits_lines', models.TextField(blank=True, help_text='One benefit per line. The layout keeps its original appearance.')),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ('display_order', 'id'), 'verbose_name':'Donation / membership level','verbose_name_plural':'Donation / membership levels'},
        ),
        migrations.RunPython(seed_site_content, reverse_code=migrations.RunPython.noop),
    ]

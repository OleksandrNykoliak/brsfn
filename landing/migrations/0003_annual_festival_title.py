from django.db import migrations


def rename_annual_festival(apps, schema_editor):
    Project = apps.get_model('landing', 'Project')
    Project.objects.filter(slug='ukraine-is-ukraine-festival').update(
        title='Ukrainian Culture Festival UCRAINA è UCRAINA',
    )


def restore_annual_festival_title(apps, schema_editor):
    Project = apps.get_model('landing', 'Project')
    Project.objects.filter(slug='ukraine-is-ukraine-festival').update(
        title='UCRAINA è UCRAINA',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0002_project_categories_event_registration'),
    ]

    operations = [
        migrations.RunPython(
            rename_annual_festival,
            restore_annual_festival_title,
        ),
    ]

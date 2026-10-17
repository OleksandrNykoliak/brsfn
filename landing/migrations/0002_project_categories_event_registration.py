from django.db import migrations, models


def categorize_existing_projects(apps, schema_editor):
    Project = apps.get_model('landing', 'Project')
    Project.objects.filter(slug='unbreakable-ukraine').update(
        title='UNBREAKABLE UKRAINE',
        category='flagship',
    )
    Project.objects.filter(slug='ukraine-is-ukraine-festival').update(
        title='UCRAINA è UCRAINA',
        category='annual',
    )


def restore_existing_projects(apps, schema_editor):
    Project = apps.get_model('landing', 'Project')
    Project.objects.filter(slug='unbreakable-ukraine').update(
        title='Unbreakable Ukraine',
        category='collaboration',
    )
    Project.objects.filter(slug='ukraine-is-ukraine-festival').update(
        title='Ukraine Is Ukraine — Ukrainian Culture Festival in Milan',
        category='collaboration',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='category',
            field=models.CharField(
                choices=[
                    ('flagship', 'Flagship project'),
                    ('annual', 'Annual project'),
                    ('monthly', 'Monthly project'),
                    ('collaboration', 'Other projects and collaborations'),
                ],
                default='collaboration',
                help_text='Determines which section of the projects page displays this project.',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='registration_url',
            field=models.URLField(
                blank=True,
                help_text='Optional link to event registration or ticket sales.',
            ),
        ),
        migrations.RunPython(
            categorize_existing_projects,
            restore_existing_projects,
        ),
    ]

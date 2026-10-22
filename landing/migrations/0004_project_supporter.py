from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0003_annual_festival_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectSupporter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180)),
                ('role', models.CharField(choices=[('patron', 'Patron'), ('sponsor', 'Sponsor')], max_length=20)),
                ('logo_url', models.URLField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='projects/supporters/')),
                ('website_url', models.URLField(blank=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supporters', to='landing.project')),
            ],
            options={
                'ordering': ['display_order', 'name'],
            },
        ),
    ]

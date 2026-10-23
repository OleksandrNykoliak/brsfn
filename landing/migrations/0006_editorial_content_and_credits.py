from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('landing', '0005_event_registration_type_alter_event_registration_url')]

    operations = [
        migrations.CreateModel(name='EventGalleryImage', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('image', models.ImageField(upload_to='events/gallery/')),
            ('caption', models.CharField(blank=True, max_length=180)),
            ('display_order', models.PositiveIntegerField(default=0)),
            ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='landing.event')),
        ], options={'ordering': ['display_order', 'id']}),
        migrations.CreateModel(name='FestivalEdition', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('year', models.PositiveIntegerField()),
            ('title', models.CharField(blank=True, max_length=180)),
            ('description', models.TextField(blank=True)),
            ('location', models.CharField(blank=True, max_length=180)),
            ('cover', models.ImageField(blank=True, upload_to='festivals/editions/')),
            ('display_order', models.PositiveIntegerField(default=0)),
            ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='festival_editions', to='landing.project')),
        ], options={'ordering': ['-year', 'display_order']}),
        migrations.CreateModel(name='FestivalEditionPhoto', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('image', models.ImageField(upload_to='festivals/photos/')),
            ('caption', models.CharField(blank=True, max_length=180)),
            ('display_order', models.PositiveIntegerField(default=0)),
            ('edition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='landing.festivaledition')),
        ], options={'ordering': ['display_order', 'id']}),
        migrations.CreateModel(name='BookClubMeeting', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=180)),
            ('date', models.DateField()),
            ('report', models.TextField(blank=True)),
            ('materials_url', models.URLField(blank=True)),
            ('cover', models.ImageField(blank=True, upload_to='bookclub/meetings/')),
            ('display_order', models.PositiveIntegerField(default=0)),
            ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_club_meetings', to='landing.project')),
        ], options={'ordering': ['-date', 'display_order']}),
        migrations.CreateModel(name='BookClubMeetingPhoto', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('image', models.ImageField(upload_to='bookclub/photos/')),
            ('caption', models.CharField(blank=True, max_length=180)),
            ('display_order', models.PositiveIntegerField(default=0)),
            ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='landing.bookclubmeeting')),
        ], options={'ordering': ['display_order', 'id']}),
        migrations.CreateModel(name='PartnerCredit', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('display_order', models.PositiveIntegerField(default=0)),
            ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credits', to='landing.partner')),
            ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='partner_credits', to='landing.project')),
            ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='partner_credits', to='landing.event')),
        ], options={'ordering': ['display_order', 'id']}),
        migrations.AddConstraint(model_name='festivaledition', constraint=models.UniqueConstraint(fields=('project','year'), name='unique_festival_edition_per_year')),
    ]

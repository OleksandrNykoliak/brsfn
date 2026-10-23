from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Project(models.Model):
    CURRENT = 'current'
    PAST = 'past'

    FLAGSHIP = 'flagship'
    ANNUAL = 'annual'
    MONTHLY = 'monthly'
    COLLABORATION = 'collaboration'

    CATEGORY_CHOICES = [
        (FLAGSHIP, 'Flagship project'),
        (ANNUAL, 'Annual project'),
        (MONTHLY, 'Monthly project'),
        (COLLABORATION, 'Other projects and collaborations'),
    ]

    STATUS_CHOICES = [
        (CURRENT, 'Current'),
        (PAST, 'Past'),
    ]

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=COLLABORATION,
        help_text='Determines which section of the projects page displays this project.',
    )

    short_description = models.TextField(
        verbose_name='Card description',
        help_text='Short text shown on the project card.',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Full description',
        help_text='The main text shown after visitors open “More details”.',
    )

    date_label = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Date',
        help_text='Free text supports date ranges and notes.',
    )
    year = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=180, blank=True)

    goal = models.TextField(
        blank=True,
        help_text='Shown in the project facts on the full page.',
    )
    budget = models.CharField(
        max_length=180,
        blank=True,
        help_text='For example: “fundraising target — €70,000”.',
    )
    partners = models.TextField(
        blank=True,
        help_text='Separate names with commas.',
    )
    participants = models.TextField(
        blank=True,
        help_text='Separate names with commas.',
    )
    outcome = models.TextField(
        blank=True,
        help_text='Optional result, award, or next milestone.',
    )
    website_text = models.TextField(
        blank=True,
        verbose_name='Website text',
        help_text='A highlighted editorial note displayed on the full project page.',
    )

    image_url = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='projects/',
        blank=True,
        null=True,
    )

    registration_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=CURRENT,
    )

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class ProjectGalleryImage(models.Model):
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='gallery_images',
    )
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=180, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.caption or self.project.title


class ProjectSupporter(models.Model):
    PATRON = 'patron'
    SPONSOR = 'sponsor'

    ROLE_CHOICES = [
        (PATRON, 'Patron'),
        (SPONSOR, 'Sponsor'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='supporters',
    )
    name = models.CharField(max_length=180)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    logo_url = models.URLField(blank=True)
    logo = models.ImageField(
        upload_to='projects/supporters/',
        blank=True,
        null=True,
    )
    website_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f'{self.name} — {self.get_role_display()}'


class Partner(models.Model):
    name = models.CharField(max_length=180)
    logo_url = models.URLField(blank=True)
    logo = models.ImageField(
        upload_to='partners/',
        blank=True,
        null=True,
    )
    website_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Event(models.Model):
    REGISTRATION = 'registration'
    TICKETS = 'tickets'

    REGISTRATION_TYPE_CHOICES = [
        (REGISTRATION, 'Registration'),
        (TICKETS, 'Ticket sales'),
    ]

    title = models.CharField(max_length=180)
    date = models.DateField(null=True, blank=True)
    date_label = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    registration_type = models.CharField(
        max_length=12,
        choices=REGISTRATION_TYPE_CHOICES,
        default=REGISTRATION,
        verbose_name='Call to action',
        help_text='Choose whether visitors should register or buy tickets.',
    )
    registration_url = models.URLField(
        blank=True,
        verbose_name='Registration / ticket link',
        help_text='Optional link. A matching button appears on the website when provided.',
    )
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True,
    )

    project = models.ForeignKey(
        'Project',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='events',
    )

    is_confirmed = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['date', 'display_order']

    def __str__(self):
        return self.title

    @property
    def registration_action_label(self):
        if self.registration_type == self.TICKETS:
            return 'Buy tickets'
        return 'Register now'

    @property
    def accepts_registration(self):
        return self.date is None or self.date >= timezone.localdate()


class Achievement(models.Model):
    number = models.CharField(max_length=40)
    label = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f'{self.number} - {self.label}'


class MediaMention(models.Model):
    ARTICLE = 'article'
    INTERVIEW = 'interview'
    PHOTO = 'photo'
    VIDEO = 'video'
    STORY = 'story'

    TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (INTERVIEW, 'Interview'),
        (PHOTO, 'Photo'),
        (VIDEO, 'Video'),
        (STORY, 'Story'),
    ]

    outlet = models.CharField(
        max_length=180,
        verbose_name='Media outlet',
        help_text='For example: Ukrinform, Rai News, Corriere della Sera.',
    )

    headline = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Headline',
        help_text='Article or interview title.',
    )

    excerpt = models.TextField(
        blank=True,
        verbose_name='Short description',
        help_text='Short summary shown on the media card.',
    )

    media_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=ARTICLE,
        verbose_name='Type',
    )

    published_at = models.DateField(
        null=True,
        blank=True,
        verbose_name='Publication date',
    )

    image_url = models.URLField(
        blank=True,
        verbose_name='External image URL',
    )

    image = models.ImageField(
        upload_to='media/',
        blank=True,
        null=True,
        verbose_name='Uploaded image',
    )

    article_url = models.URLField(
        blank=True,
        verbose_name='Article URL',
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name='Featured',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Show on website',
    )

    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Display order',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            'display_order',
            '-published_at',
            '-created_at',
        ]
        verbose_name = 'Media mention'
        verbose_name_plural = 'Media mentions'

    def __str__(self):
        if self.headline:
            return f'{self.outlet} — {self.headline}'
        return self.outlet


class TeamMember(models.Model):
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=160)
    bio = models.TextField(blank=True)

    photo_url = models.URLField(blank=True)
    photo = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True,
    )

    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('about', 'About Boristene'),
        ('events', 'Events & Activities'),
        ('join', 'Getting Involved'),
        ('donations', 'Donations & Tax Benefits'),
        ('project', 'Projects'),
    ]

    question = models.CharField(max_length=240)
    answer = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='about',
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'display_order']

    def __str__(self):
        return self.question


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('event', 'Event'),
        ('project', 'Project'),
        ('publication', 'Publication'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=180)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)

    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPES,
        default='event',
    )

    image_url = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='activities/',
        blank=True,
        null=True,
    )

    link = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date', 'display_order']

    def __str__(self):
        return self.title
    
    

class EventGalleryImage(models.Model):
    """Photo report for a particular event, including past events."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='events/gallery/')
    caption = models.CharField(max_length=180, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.caption or self.event.title


class FestivalEdition(models.Model):
    """An edition of an annual project (normally UCRAINA è UCRAINA)."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='festival_editions')
    year = models.PositiveIntegerField()
    title = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=180, blank=True)
    cover = models.ImageField(upload_to='festivals/editions/', blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-year', 'display_order']
        constraints = [models.UniqueConstraint(fields=['project', 'year'], name='unique_festival_edition_per_year')]

    def get_absolute_url(self):
        return reverse('festival-edition', kwargs={'slug': self.project.slug, 'year': self.year})

    def __str__(self):
        return f'{self.project.title} — {self.year}'


class FestivalEditionPhoto(models.Model):
    edition = models.ForeignKey(FestivalEdition, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='festivals/photos/')
    caption = models.CharField(max_length=180, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.caption or str(self.edition)


class BookClubMeeting(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='book_club_meetings')
    title = models.CharField(max_length=180)
    date = models.DateField()
    report = models.TextField(blank=True)
    materials_url = models.URLField(blank=True)
    cover = models.ImageField(upload_to='bookclub/meetings/', blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date', 'display_order']

    def get_absolute_url(self):
        return reverse('book-club-meeting', kwargs={'slug': self.project.slug, 'pk': self.pk})

    def __str__(self):
        return f'{self.title} — {self.date}'


class BookClubMeetingPhoto(models.Model):
    meeting = models.ForeignKey(BookClubMeeting, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='bookclub/photos/')
    caption = models.CharField(max_length=180, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.caption or self.meeting.title


class PartnerCredit(models.Model):
    """Verified link between an existing partner logo and a supported event/project.

    No implicit sponsorship association is inferred from a partner's presence.
    """
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='credits')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='partner_credits', blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='partner_credits', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def clean(self):
        from django.core.exceptions import ValidationError
        if bool(self.project_id) == bool(self.event_id):
            raise ValidationError('Choose either a supported project or a supported event, not both or neither.')

    @property
    def supported_title(self):
        return self.project.title if self.project_id else self.event.title

    def get_absolute_url(self):
        if self.project_id:
            return self.project.get_absolute_url()
        return reverse('event-detail', kwargs={'pk': self.event_id})

    def __str__(self):
        return f'{self.partner.name}: {self.supported_title}'

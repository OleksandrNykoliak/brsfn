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


# ------------------------------ Website CMS -------------------------------
# These models are additive: existing Project/Event/Partner records are kept.
class SiteText(models.Model):
    """A visible text fragment from a particular template, editable without deployment."""
    key = models.CharField(max_length=220, unique=True)
    page = models.CharField(max_length=90, db_index=True)
    section = models.CharField(max_length=120, db_index=True)
    label = models.CharField(max_length=180)
    text = models.TextField(blank=True, help_text='Plain text. HTML is escaped for safety. Empty text hides the phrase.')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('page', 'section', 'key')
        verbose_name = 'Page text'
        verbose_name_plural = 'Page texts'

    def __str__(self):
        return f'{self.page} / {self.section}: {self.label[:65]}'


class SiteMedia(models.Model):
    """Replace a static or remote image without touching the template."""
    key = models.CharField(max_length=220, unique=True)
    page = models.CharField(max_length=90, db_index=True)
    section = models.CharField(max_length=120)
    label = models.CharField(max_length=180)
    fallback = models.TextField(help_text='Original static path, or original absolute image URL.')
    image = models.ImageField(upload_to='cms/', blank=True)
    external_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('page', 'section', 'key')
        verbose_name = 'Page image'
        verbose_name_plural = 'Page images'

    def __str__(self):
        return f'{self.page}: {self.label[:70]}'


class SiteLink(models.Model):
    """Editable external, email and telephone links in page templates."""
    key = models.CharField(max_length=220, unique=True)
    page = models.CharField(max_length=90, db_index=True)
    section = models.CharField(max_length=120)
    label = models.CharField(max_length=180)
    url = models.CharField(max_length=1200)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('page', 'section', 'key')
        verbose_name = 'Page link'
        verbose_name_plural = 'Page links'

    def clean(self):
        from django.core.exceptions import ValidationError
        from urllib.parse import urlsplit
        url = (self.url or '').strip()
        parts = urlsplit(url)
        if not url or (parts.scheme not in ('http', 'https', 'mailto', 'tel') and not (url.startswith('/') and not url.startswith('//')) and not url.startswith('#')):
            raise ValidationError({'url': 'Use an http(s), mailto:, tel:, /path or #anchor URL.'})
        if parts.scheme in ('http','https') and not parts.netloc:
            raise ValidationError({'url': 'Enter a valid HTTP(S) URL.'})
        super().clean()

    def __str__(self):
        return f'{self.page} / {self.section}: {self.label[:65]}'


class SiteIdentity(models.Model):
    """Single source of truth for bank transfer and association details."""
    legal_name = models.CharField(max_length=180, default='BORISTENE ETS')
    beneficiary = models.CharField(max_length=180, default='BORISTENE associazione ETS')
    tax_code = models.CharField(max_length=40, default='97971770157')
    legal_form = models.CharField(max_length=300, default='Associazione riconosciuta / Ente del Terzo Settore (ETS), non-profit')
    representative = models.CharField(max_length=180, default='Svetlana Terechtchenko, President')
    registered_address = models.CharField(max_length=250, default='Via Ugo Tarchetti 1, 20121 Milano (MI), Italy')
    short_address = models.CharField(max_length=250, default='Via Ugo Tarchetti 1, 20121 Milano, Italy')
    email = models.EmailField(default='associazione@boristenemilano.com')
    phone = models.CharField(max_length=45, default='+39 331 272 0262')
    iban = models.CharField(max_length=70, default='IT58B0503401727000000003792')
    swift = models.CharField(max_length=30, default='BAPPIT21633')
    bank_name = models.CharField(max_length=180, default='Banco BPM · Milan, Italy')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Association and banking details'
        verbose_name_plural = 'Association and banking details'

    def save(self, *args, **kwargs):
        self.pk = 1
        self.iban = ''.join(self.iban.split()).upper()
        self.swift = ''.join(self.swift.split()).upper()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return None

    def __str__(self):
        return 'BORISTENE — official details and bank transfers'


class SupportTier(models.Model):
    KIND_CHOICES = [('donation', 'Donation'), ('membership', 'Membership'), ('patron', 'Patron')]
    name = models.CharField(max_length=130)
    price = models.CharField(max_length=60, blank=True)
    period = models.CharField(max_length=45, blank=True)
    subtitle = models.TextField(blank=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='donation')
    benefits_lines = models.TextField(blank=True, help_text='One benefit per line. The layout keeps its original appearance.')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('display_order', 'id')
        verbose_name = 'Donation / membership level'
        verbose_name_plural = 'Donation / membership levels'

    @property
    def benefits(self):
        return [line.strip() for line in self.benefits_lines.splitlines() if line.strip()]

    def __str__(self):
        return self.name

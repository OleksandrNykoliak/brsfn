from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Project(models.Model):
    CURRENT = 'current'
    PAST = 'past'

    STATUS_CHOICES = [
        (CURRENT, 'Current'),
        (PAST, 'Past'),
    ]

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)

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
    title = models.CharField(max_length=180)
    date = models.DateField(null=True, blank=True)
    date_label = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
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
    
    

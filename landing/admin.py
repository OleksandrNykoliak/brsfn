from django.contrib import admin

from .models import (FAQ, Achievement, Activity, Event, MediaMention, Partner,
                     Project, ProjectGalleryImage, ProjectSupporter, TeamMember,
                     EventGalleryImage, FestivalEdition, FestivalEditionPhoto,
                     BookClubMeeting, BookClubMeetingPhoto, PartnerCredit)

admin.site.siteheader = 'BORISTENE'
admin.site.site_title = 'BORISTENE'
admin.site.index_title = 'Website content'


class StudioAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/admin_studio.css',)}


class ProjectGalleryImageInline(admin.TabularInline):
    model = ProjectGalleryImage
    extra = 1
    fields = ('image', 'caption', 'display_order')


class ProjectSupporterInline(admin.TabularInline):
    model = ProjectSupporter
    extra = 1
    fields = ('name', 'role', 'logo', 'logo_url', 'website_url', 'display_order')


class EventGalleryInline(admin.TabularInline):
    model = EventGalleryImage
    extra = 1

class FestivalEditionPhotoInline(admin.TabularInline):
    model = FestivalEditionPhoto
    extra = 1

class BookClubMeetingPhotoInline(admin.TabularInline):
    model = BookClubMeetingPhoto
    extra = 1

class PartnerCreditInline(admin.TabularInline):
    model = PartnerCredit
    extra = 1
    fields = ('project', 'event', 'display_order')

@admin.register(FestivalEdition)
class FestivalEditionAdmin(StudioAdmin):
    list_display = ('project', 'year', 'title', 'display_order')
    list_filter = ('project', 'year')
    inlines = (FestivalEditionPhotoInline,)

@admin.register(BookClubMeeting)
class BookClubMeetingAdmin(StudioAdmin):
    list_display = ('title', 'date', 'project', 'display_order')
    list_filter = ('project', 'date')
    inlines = (BookClubMeetingPhotoInline,)

@admin.register(Project)
class ProjectAdmin(StudioAdmin):
    inlines = (ProjectGalleryImageInline, ProjectSupporterInline)
    list_display = (
        'title',
        'category',
        'status',
        'year',
        'is_featured',
        'display_order',
    )
    list_filter = (
        'category',
        'status',
        'is_featured',
    )
    search_fields = (
        'title',
        'short_description',
        'description',
        'location',
    )
    list_editable = (
        'category',
        'status',
        'is_featured',
        'display_order',
    )
    ordering = (
        'display_order',
        '-created_at',
    )
    prepopulated_fields = {
        'slug': ('title',),
    }
    fieldsets = (
        (
            'Card on the website',
            {
                'fields': (
                    'title',
                    'slug',
                    'category',
                    'short_description',
                    'image',
                    'image_url',
                    'status',
                    'is_featured',
                    'display_order',
                )
            },
        ),
        (
            'Project facts',
            {
                'fields': (
                    'date_label',
                    'location',
                    'year',
                    'goal',
                    'budget',
                    'partners',
                    'participants',
                    'outcome',
                )
            },
        ),
        (
            'Full project page',
            {
                'fields': (
                    'description',
                    'website_text',
                    'registration_url',
                )
            },
        ),
    )


@admin.register(Event)
class EventAdmin(StudioAdmin):
    inlines = (EventGalleryInline,)
    list_display = (
        'title',
        'date',
        'location',
        'registration_type',
        'is_confirmed',
        'project',
    )
    list_filter = (
        'is_confirmed',
        'date',
        'registration_type',
    )
    search_fields = (
        'title',
        'location',
        'description',
    )
    date_hierarchy = 'date'
    ordering = (
        'date',
        'display_order',
    )
    fieldsets = (
        (
            'Event details',
            {
                'fields': (
                    'title',
                    'date',
                    'date_label',
                    'location',
                    'description',
                    'image',
                    'project',
                )
            },
        ),
        (
            'Registration',
            {
                'fields': ('registration_type', 'registration_url'),
            },
        ),
        (
            'Website display',
            {
                'fields': ('is_confirmed', 'display_order'),
            },
        ),
    )


@admin.register(Partner)
class PartnerAdmin(StudioAdmin):
    inlines = (PartnerCreditInline,)
    list_display = (
        'name',
        'website_url',
        'display_order',
    )
    search_fields = (
        'name',
        'website_url',
    )
    ordering = (
        'display_order',
        'name',
    )


@admin.register(Achievement)
class AchievementAdmin(StudioAdmin):
    list_display = (
        'number',
        'label',
        'display_order',
    )
    search_fields = (
        'number',
        'label',
        'note',
    )


@admin.register(MediaMention)
class MediaMentionAdmin(StudioAdmin):
    list_display = (
        'outlet',
        'headline',
        'media_type',
        'published_at',
        'is_featured',
        'is_active',
        'display_order',
    )
    list_filter = (
        'media_type',
        'is_featured',
        'is_active',
        'published_at',
    )
    search_fields = (
        'outlet',
        'headline',
        'excerpt',
        'article_url',
    )
    list_editable = (
        'is_featured',
        'is_active',
        'display_order',
    )
    ordering = (
        'display_order',
        '-published_at',
    )
    date_hierarchy = 'published_at'
    fieldsets = (
        (
            'Publication',
            {
                'fields': (
                    'outlet',
                    'headline',
                    'excerpt',
                    'media_type',
                    'published_at',
                    'article_url',
                )
            },
        ),
        (
            'Image',
            {
                'fields': (
                    'image',
                    'image_url',
                )
            },
        ),
        (
            'Website display',
            {
                'fields': (
                    'is_featured',
                    'is_active',
                    'display_order',
                )
            },
        ),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(StudioAdmin):
    list_display = (
        'name',
        'role',
        'display_order',
    )
    search_fields = (
        'name',
        'role',
        'bio',
    )
    ordering = (
        'display_order',
        'name',
    )


@admin.register(FAQ)
class FAQAdmin(StudioAdmin):
    list_display = (
        'question',
        'category',
        'display_order',
    )
    list_filter = (
        'category',
    )
    search_fields = (
        'question',
        'answer',
    )
    ordering = (
        'category',
        'display_order',
    )


@admin.register(Activity)
class ActivityAdmin(StudioAdmin):
    list_display = (
        'title',
        'activity_type',
        'date',
        'link',
        'display_order',
    )
    list_filter = (
        'activity_type',
        'date',
    )
    search_fields = (
        'title',
        'description',
        'link',
    )
    ordering = (
        '-date',
        'display_order',
    )

# Content studio: every existing data entity is still managed above; this
# section adds page copy/media/links, official banking info and support tiers.
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import (SiteText, SiteMedia, SiteLink, SiteIdentity, SupportTier)


class ContentStudioAdmin(admin.ModelAdmin):
    list_per_page = 50
    save_on_top = True
    class Media:
        css = {'all': ('css/admin_studio.css',)}


@admin.register(SiteText)
class SiteTextAdmin(ContentStudioAdmin):
    list_display = ('label', 'page', 'section', 'preview', 'updated_at')
    list_display_links = ('label',)
    list_filter = ('page', 'section')
    search_fields = ('text', 'label', 'page', 'section', 'key')
    readonly_fields = ('key', 'page', 'section', 'label', 'updated_at')
    fields = ('page', 'section', 'label', 'text', 'key', 'updated_at')
    ordering = ('page', 'section', 'key')

    def has_add_permission(self, request):
        # New keys must be linked to a template; use sync_site_content after editing templates.
        return False

    @admin.display(description='Displayed text')
    def preview(self, obj):
        return (obj.text[:96] + '…') if len(obj.text) > 96 else obj.text


@admin.register(SiteMedia)
class SiteMediaAdmin(ContentStudioAdmin):
    list_display = ('label', 'page', 'section', 'preview')
    list_filter = ('page', 'section')
    search_fields = ('key', 'label', 'page', 'fallback')
    readonly_fields = ('key', 'page', 'section', 'label', 'fallback', 'preview')
    fields = ('page', 'section', 'label', 'image', 'external_url', 'preview', 'fallback', 'key')

    def has_add_permission(self, request):
        return False

    @admin.display(description='Image preview')
    def preview(self, obj):
        from django.templatetags.static import static
        if obj.image:
            src = obj.image.url
        elif obj.external_url:
            src = obj.external_url
        elif obj.fallback.startswith('http'):
            src = obj.fallback
        else:
            src = static(obj.fallback)
        return format_html('<img src="{}" alt="" style="max-height:90px;max-width:230px;object-fit:contain;border-radius:6px">', src)


@admin.register(SiteLink)
class SiteLinkAdmin(ContentStudioAdmin):
    list_display = ('label', 'page', 'section', 'url')
    list_filter = ('page', 'section')
    search_fields = ('key', 'label', 'url', 'page')
    readonly_fields = ('key', 'page', 'section', 'label')
    fields = ('page', 'section', 'label', 'url', 'key')

    def has_add_permission(self, request):
        return False


@admin.register(SiteIdentity)
class SiteIdentityAdmin(ContentStudioAdmin):
    list_display = ('legal_name', 'beneficiary', 'tax_code', 'bank_name', 'updated_at')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Association', {'fields': ('legal_name', 'legal_form', 'representative', 'registered_address', 'short_address', 'tax_code')}),
        ('Contact', {'fields': ('email', 'phone')}),
        ('Bank transfers', {'fields': ('beneficiary', 'bank_name', 'iban', 'swift')}),
        ('Change history', {'fields': ('updated_at',)}),
    )

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteIdentity.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SupportTier)
class SupportTierAdmin(ContentStudioAdmin):
    list_display = ('name', 'price', 'period', 'kind', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    list_filter = ('kind', 'is_active')
    search_fields = ('name', 'subtitle', 'benefits_lines')
    ordering = ('display_order', 'id')
    fieldsets = (
        ('Display on site', {'fields': ('name', 'kind', 'price', 'period', 'subtitle')}),
        ('Membership benefits', {'fields': ('benefits_lines',)}),
        ('Order / visibility', {'fields': ('display_order', 'is_active')}),
    )


# Stand-alone editors for images and other nested entities, in addition to the
# inlines on Project, Event, Partner, Festival and Book Club pages.
@admin.register(ProjectGalleryImage)
class ProjectGalleryImageAdmin(ContentStudioAdmin):
    list_display = ('project', 'caption', 'display_order')
    list_filter = ('project',)
    search_fields = ('caption', 'project__title')

@admin.register(EventGalleryImage)
class EventGalleryImageAdmin(ContentStudioAdmin):
    list_display = ('event', 'caption', 'display_order')
    list_filter = ('event',)
    search_fields = ('caption', 'event__title')

@admin.register(FestivalEditionPhoto)
class FestivalEditionPhotoAdmin(ContentStudioAdmin):
    list_display = ('edition', 'caption', 'display_order')
    list_filter = ('edition__project',)
    search_fields = ('caption', 'edition__title', 'edition__project__title')

@admin.register(BookClubMeetingPhoto)
class BookClubMeetingPhotoAdmin(ContentStudioAdmin):
    list_display = ('meeting', 'caption', 'display_order')
    search_fields = ('caption', 'meeting__title')

@admin.register(ProjectSupporter)
class ProjectSupporterAdmin(ContentStudioAdmin):
    list_display = ('name', 'project', 'role', 'display_order')
    list_filter = ('role', 'project')
    search_fields = ('name', 'project__title')

@admin.register(PartnerCredit)
class PartnerCreditAdmin(ContentStudioAdmin):
    list_display = ('partner', 'project', 'event', 'display_order')
    list_filter = ('partner',)
    search_fields = ('partner__name', 'project__title', 'event__title')


admin.site.site_header = 'BORISTENE · Content Studio'
admin.site.site_title = 'BORISTENE CMS'
admin.site.index_title = 'Website content'
admin.site.index_template = 'admin/cms_dashboard.html'

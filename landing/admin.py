from django.contrib import admin

from .models import (FAQ, Achievement, Activity, Event, MediaMention, Partner,
                     Project, TeamMember)

admin.site.site_header = 'BORISTENE'
admin.site.site_title = 'BORISTENE'
admin.site.index_title = 'Website content'


class StudioAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/admin.css',)}


@admin.register(Project)
class ProjectAdmin(StudioAdmin):
    list_display = (
        'title',
        'status',
        'year',
        'is_featured',
        'display_order',
    )
    list_filter = (
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
    list_display = (
        'title',
        'date',
        'location',
        'is_confirmed',
        'project',
    )
    list_filter = (
        'is_confirmed',
        'date',
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


@admin.register(Partner)
class PartnerAdmin(StudioAdmin):
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
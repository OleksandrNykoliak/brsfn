from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import (FAQ, Achievement, Activity, Event, MediaMention, Partner,
                     Project, TeamMember, FestivalEdition, BookClubMeeting, ProjectSupporter)
from .support import SUPPORT_LEVELS


def homeview(request):
    today = timezone.localdate()
    context = {
        'flagship_projects': Project.objects.filter(is_active=True, category=Project.FLAGSHIP),
        'annual_projects': Project.objects.filter(is_active=True, category=Project.ANNUAL),
        'monthly_projects': Project.objects.filter(is_active=True, category=Project.MONTHLY),
        'collaboration_projects': Project.objects.filter(
            is_active=True,
            category=Project.COLLABORATION,
        ),
        'upcoming_events': Event.objects.filter(
            Q(date__gte=today) | Q(date__isnull=True),
        ).order_by(F('date').asc(nulls_last=True), 'display_order').prefetch_related('gallery_images'),
        'past_events': Event.objects.filter(date__lt=today).order_by('-date', 'display_order').prefetch_related('gallery_images'),
        'achievements': Achievement.objects.all(),
        'media_mentions': MediaMention.objects.filter(is_active=True),
        'partners': Partner.objects.all(),
        'credited_partners': Partner.objects.filter(credits__isnull=False).distinct().prefetch_related('credits__project', 'credits__event'),
        'other_partners': Partner.objects.filter(credits__isnull=True),
        'project_supporters': ProjectSupporter.objects.filter(project__is_active=True).select_related('project'),
        'support_levels': SUPPORT_LEVELS,
        'team_members': TeamMember.objects.all(),
        'faqs': FAQ.objects.all(),
        'activities': Activity.objects.all().order_by('-date', '-id')[:6],
    }
    return render(request, 'homepage.html', context)

def projects_list(request):
    today = timezone.localdate()
    projects = Project.objects.filter(is_active=True)
    return render(request, 'landing/projects.html', {
        'flagship_projects': projects.filter(category=Project.FLAGSHIP),
        'annual_projects': projects.filter(category=Project.ANNUAL),
        'monthly_projects': projects.filter(category=Project.MONTHLY),
        'collaboration_projects': projects.filter(category=Project.COLLABORATION),
        'upcoming_events': Event.objects.filter(
            Q(date__gte=today) | Q(date__isnull=True),
        ).order_by(F('date').asc(nulls_last=True), 'display_order').prefetch_related('gallery_images'),
    })

def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related('gallery_images', 'events__gallery_images', 'supporters', 'festival_editions__photos', 'book_club_meetings__photos', 'partner_credits__partner'),
        slug=slug,
        is_active=True,
    )
    other_projects = Project.objects.filter(is_active=True).exclude(pk=project.pk)[:3]
    return render(request, 'landing/project_detail.html', {
        'project': project,
        'other_projects': other_projects,
    })

def about_page(request):
    return render(request, 'landing/about.html', {'team_members': TeamMember.objects.all()})

def join_page(request):
    return render(request, 'landing/join.html', {'partners': Partner.objects.all()})
def support_page(request):
    return render(request, 'landing/support.html', {'support_levels': SUPPORT_LEVELS})


def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('project').prefetch_related('gallery_images', 'partner_credits__partner'), pk=pk)
    return render(request, 'landing/event_detail.html', {'event': event})


def festival_edition_detail(request, slug, year):
    project = get_object_or_404(Project, slug=slug, category=Project.ANNUAL, is_active=True)
    edition = get_object_or_404(FestivalEdition.objects.prefetch_related('photos'), project=project, year=year)
    return render(request, 'landing/festival_edition.html', {'project': project, 'edition': edition})


def book_club_meeting_detail(request, slug, pk):
    project = get_object_or_404(Project, slug=slug, category=Project.MONTHLY, is_active=True)
    meeting = get_object_or_404(BookClubMeeting.objects.prefetch_related('photos'), project=project, pk=pk)
    return render(request, 'landing/book_club_meeting.html', {'project': project, 'meeting': meeting})

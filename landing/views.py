from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import (FAQ, Achievement, Activity, Event, MediaMention, Partner,
                     Project, TeamMember)


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
        ).order_by(F('date').asc(nulls_last=True), 'display_order'),
        'past_events': Event.objects.filter(date__lt=today).order_by('-date', 'display_order'),
        'achievements': Achievement.objects.all(),
        'media_mentions': MediaMention.objects.filter(is_active=True),
        'partners': Partner.objects.all(),
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
        ).order_by(F('date').asc(nulls_last=True), 'display_order'),
    })

def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related('gallery_images', 'events', 'supporters'),
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
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.db.models import Q
from .models import Activity, Achievement, Event, FAQ, MediaMention, Partner, Project, TeamMember
from django.template.exceptions import TemplateDoesNotExist
from django.http import Http404

def homeview(request):
    today = timezone.localdate()
    context = {
        'projects': Project.objects.filter(status=Project.CURRENT),
        'past_projects': Project.objects.filter(status=Project.PAST),
        'upcoming_events': Event.objects.filter(Q(date__gte=today) | Q(date__isnull=True)).order_by('date', 'display_order'),
        'past_events': Event.objects.filter(date__lt=today).order_by('-date', 'display_order'),
        'achievements': Achievement.objects.all(),
        'media_mentions': MediaMention.objects.all(),
        'partners': Partner.objects.all(),
        'team_members': TeamMember.objects.all(),
        'faqs': FAQ.objects.all(),
        'activities': Activity.objects.all().order_by('-date', '-id')[:6],
    }
    return render(request, 'homepage.html', context)


def unbreakable_project(request):
    return render(request, 'landing/project_unbreakable.html')


def projects_list(request):
    return render(request, 'landing/projects.html', {'projects': Project.objects.all()})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'landing/project_detail.html', {'project': project})


def about_page(request):
    return render(request, 'landing/about.html', {'team_members': TeamMember.objects.all()})


def join_page(request):
    return render(request, 'landing/join.html', {'partners': Partner.objects.all()})

def project_detail(request, project_name):
    try:
        return render(request, f'{project_name}.html')
    except TemplateDoesNotExist:
        raise Http404("Проєкт не знайдено")
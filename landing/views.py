from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .forms import ContactRequestForm

from .models import (FAQ, Activity, Event, MediaMention, Partner,
                     Project, TeamMember, FestivalEdition, BookClubMeeting, ProjectSupporter)
from .models import ContactRequest, SupportTier


@require_http_methods(['GET', 'HEAD', 'POST'])
def homeview(request):
    if request.method == 'POST':
        contact_form = ContactRequestForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(
                request, _('Thank you. We have received your details and will be in touch.'),
                extra_tags='contact-request',
            )
            return redirect(reverse('homeview') + '#newsletter')
    else:
        interest = request.GET.get('interest', ContactRequest.Interest.UPDATES)
        if interest not in ContactRequest.Interest.values:
            interest = ContactRequest.Interest.UPDATES
        contact_form = ContactRequestForm(initial={'interest': interest})

    media_page = Paginator(
        MediaMention.objects.filter(is_active=True).order_by('display_order', '-published_at', '-created_at', '-pk'),
        12,
    ).get_page(request.GET.get('media_page'))
    context = {
        'contact_form': contact_form,
        'projects': Project.ordered_for_display(),
        'media_mentions': media_page,
        'media_page': media_page,
        'media_page_range': media_page.paginator.get_elided_page_range(media_page.number, on_each_side=1, on_ends=1),
        'partners': Partner.objects.all(),
        'credited_partners': Partner.objects.filter(credits__isnull=False).distinct().prefetch_related('credits__project', 'credits__event'),
        'other_partners': Partner.objects.filter(credits__isnull=True),
        'project_supporters': ProjectSupporter.objects.filter(project__is_active=True).select_related('project'),
        'support_levels': SupportTier.objects.filter(is_active=True),
        'team_members': TeamMember.objects.all(),
        'faqs': FAQ.objects.all(),
        'activities': Activity.objects.all().order_by('-date', '-id')[:6],
    }
    return render(request, 'homepage.html', context, status=400 if contact_form.errors else 200)

def projects_list(request):
    return render(request, 'landing/projects.html', {
        'projects': Project.ordered_for_display(),
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
    return render(request, 'landing/support.html', {'support_levels': SupportTier.objects.filter(is_active=True)})


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

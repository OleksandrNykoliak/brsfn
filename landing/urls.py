from django.urls import path

from .views import (about_page, homeview, join_page, project_detail,
                    projects_list, support_page, event_detail, festival_edition_detail,
                    book_club_meeting_detail)

urlpatterns = [
    path('', homeview, name='homeview'),
    path('projects/', projects_list, name='projects'),
    path('projects/<slug:slug>/', project_detail, name='project-detail'),
    path('projects/<slug:slug>/editions/<int:year>/', festival_edition_detail, name='festival-edition'),
    path('projects/<slug:slug>/meetings/<int:pk>/', book_club_meeting_detail, name='book-club-meeting'),
    path('events/<int:pk>/', event_detail, name='event-detail'),
    path('support/', support_page, name='support'),
    path('about/', about_page, name='about'),
    path('join/', join_page, name='join'),
]





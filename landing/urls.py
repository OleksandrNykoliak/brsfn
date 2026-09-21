from django.urls import path

from .views import (about_page, homeview, join_page, project_detail,
                    projects_list)

urlpatterns = [
    path('', homeview, name='homeview'),
    path('projects/', projects_list, name='projects'),
    path('projects/<slug:slug>/', project_detail, name='project-detail'),
    path('about/', about_page, name='about'),
    path('join/', join_page, name='join'),
]





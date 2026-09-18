from django.urls import path
from .views import about_page, homeview, join_page, project_detail, projects_list, unbreakable_project
from . import views

urlpatterns = [
    path('', homeview, name='homeview'),
    path('projects/', projects_list, name='projects'),
    path('projects/unbreakable-ukraine/', unbreakable_project, name='project-unbreakable'),
    path('unbreakable-ukraine/', unbreakable_project, name='unbreakable-ukraine'),
    path('projects/<slug:slug>/', project_detail, name='project-detail'),
    path('about/', about_page, name='about'),
    path('join/', join_page, name='join'),

    path('<slug:project_name>/', views.project_detail, name='project_detail'),
]

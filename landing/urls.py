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




# .hero2-left > .eyebrow,
# .hero2-left > .hero2-title,
# .hero2-left > .hero2-tagline,
# .hero2-left > .hero2-divider,
# .hero2-left > .hero2-ctas-wrap {
#   position: relative;
#   z-index: 2;
# }

# @media (max-width: 959px) {
#   .hero2-mapline {
#     top: -2rem;
#     right: -15rem;
#     width: 700px;
#     opacity: .4;
#   }
# }

# @media (max-width: 640px) {
#   .hero2-mapline {
#     top: 0;
#     right: -18rem;
#     width: 620px;
#     opacity: .25;
#   }
# }*/
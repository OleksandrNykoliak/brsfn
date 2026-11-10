from django import template
from django.db.models import Count
from landing.models import SiteText

register = template.Library()

@register.simple_tag
def cms_page_stats():
    return list(SiteText.objects.values('page').annotate(total=Count('id')).order_by('page'))

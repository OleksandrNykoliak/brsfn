"""Request-scoped CMS template tags. Original text/assets remain usable before migrations."""
import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from django import template
from django.conf import settings
from django.db.utils import DatabaseError
from django.templatetags.static import static

from landing.models import SiteIdentity, SiteLink, SiteMedia, SiteText

register = template.Library()

@lru_cache(maxsize=1)
def _defaults():
    path = Path(__file__).resolve().parent.parent / 'cms_defaults.json'
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)


def _records(context, kind):
    # No cross-request content caching: every save is immediately visible.
    request = context.get('request')
    if request is not None:
        store = getattr(request, '_boristene_cms_cache', None)
        if store is None:
            store = {}
            request._boristene_cms_cache = store
    else:
        store = context.render_context.setdefault(_RENDER_KEY, {})
    if kind not in store:
        model = {'texts': SiteText, 'media': SiteMedia, 'links': SiteLink, 'identity': SiteIdentity}[kind]
        try:
            if kind == 'identity':
                store[kind] = model.objects.filter(pk=1).first()
            else:
                store[kind] = {entry.key: entry for entry in model.objects.all()}
        except DatabaseError:
            # Before running migrate, pages still render with original material.
            store[kind] = None if kind == 'identity' else {}
    return store[kind]

_RENDER_KEY = object()


def _safe_link(url):
    if not url or any(ch in url for ch in ('\n', '\r', '\x00')):
        return False
    if url.startswith('//'):
        return False
    scheme = urlsplit(url).scheme.lower()
    return scheme in ('https', 'http', 'mailto', 'tel') or url.startswith(('/', '#'))


@register.simple_tag(takes_context=True)
def cms_text(context, key):
    item = _records(context, 'texts').get(key)
    if item is not None:
        return item.text
    return _defaults()['texts'].get(key, {}).get('value', '')


@register.simple_tag(takes_context=True)
def cms_image(context, key):
    item = _records(context, 'media').get(key)
    fallback = _defaults()['media'].get(key, {}).get('value', '')
    if item is not None:
        if item.image:
            try:
                return item.image.url
            except (ValueError, OSError):
                pass
        if item.external_url and _safe_link(item.external_url):
            return item.external_url
        fallback = item.fallback or fallback
    if fallback.startswith(('https://', 'http://')):
        return fallback
    return static(fallback) if fallback else ''


@register.simple_tag(takes_context=True)
def cms_link(context, key):
    fallback = _defaults()['links'].get(key, {}).get('value', '#')
    item = _records(context, 'links').get(key)
    value = item.url if item else fallback
    # Keep mailto URLs with their own subject editable while respecting the
    # central association email if the original recipient was not customised.
    original_mailbox = 'mailto:associazione@boristenemilano.com'
    if value.startswith(original_mailbox):
        identity = _records(context, 'identity')
        email = identity.email if identity else 'associazione@boristenemilano.com'
        value = 'mailto:' + email + value[len(original_mailbox):]
    return value if _safe_link(value) else fallback


@register.simple_tag(takes_context=True)
def cms_identity(context, key):
    obj = _records(context, 'identity')
    defaults = {
        'legal_name': 'BORISTENE ETS',
        'beneficiary': 'BORISTENE associazione ETS',
        'tax_code': '97971770157',
        'legal_form': 'Associazione riconosciuta / Ente del Terzo Settore (ETS), non-profit',
        'representative': 'Svetlana Terechtchenko, President',
        'registered_address': 'Via Ugo Tarchetti 1, 20121 Milano (MI), Italy',
        'short_address': 'Via Ugo Tarchetti 1, 20121 Milano, Italy',
        'email': 'associazione@boristenemilano.com',
        'phone': '+39 331 272 0262',
        'iban': 'IT58B0503401727000000003792',
        'swift': 'BAPPIT21633',
        'bank_name': 'Banco BPM · Milan, Italy',
    }
    if key == 'iban_display':
        value = obj.iban if obj else defaults['iban']
        # Group like the association's published account number, preserve past spacing.
        if len(value) == 27 and value.startswith('IT'):
            return f'{value[:4]} {value[4]} {value[5:10]} {value[10:15]} {value[15:23]} {value[23:]}'
        return value
    if key == 'iban_compact':
        return obj.iban if obj else defaults['iban']
    if key == 'email_href':
        return 'mailto:' + (obj.email if obj else defaults['email'])
    if key == 'phone_href':
        return 'tel:' + ''.join(c for c in (obj.phone if obj else defaults['phone']) if c.isdigit() or c == '+')
    if key not in defaults:
        return ''
    return getattr(obj, key) if obj else defaults[key]

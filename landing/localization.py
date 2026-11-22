"""Italian defaults for site copy and translated labels used by browser controls."""
import json
from functools import lru_cache
from pathlib import Path

from django.utils.translation import gettext as _


@lru_cache(maxsize=1)
def italian_catalog():
    with (Path(__file__).parent / 'italian_catalog.json').open(encoding='utf-8') as handle:
        return json.load(handle)


def client_messages():
    return {
        'openMenu': _('Open menu'), 'closeMenu': _('Close menu'),
        'partnerPage': _('Go to partner page'), 'projectPage': _('Go to project page'),
        'copy': _('Copy'), 'copied': _('Copied'), 'failed': _('Failed'),
        'copySuccess': _('Copied to clipboard.'),
        'copyFailure': _('Copy failed. Please select and copy the displayed text manually.'),
        'monthlyContribution': _('Monthly contribution'), 'oneTimeContribution': _('One-time contribution'),
        'supportMonthly': _('Support monthly'), 'supportOnce': _('Support once'),
    }

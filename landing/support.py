"""Editorial support tiers — prices and benefits approved in the brief.

These are informational tiers, not a payment integration. Do not imply that a
click has created a subscription or taken a payment.
"""
SUPPORT_LEVELS = [
    {
        'name': 'One-time donation', 'price': '', 'period': '',
        'subtitle': '', 'benefits': [], 'kind': 'donation',
    },
    {
        'name': 'Monthly donation', 'price': 'From €5', 'period': '/month',
        'subtitle': 'Choose comfortable to you amount from 5€ and up',
        'benefits': [], 'kind': 'donation',
    },
    {
        'name': 'Membership — Socio', 'price': '€50', 'period': '/year',
        'subtitle': '', 'kind': 'membership',
        'benefits': [
            'Your name featured on our YouTube channel',
            'Possibility of reservation on front-row seating at our events',
            'Priority booking for our events',
            'Three exclusive Zoom meetings per year with members of the Association’s Board and a special guest',
        ],
    },
    {
        'name': 'Gold Membership', 'price': '€100', 'period': '/year',
        'subtitle': '', 'kind': 'membership',
        'benefits': [
            'Personal invitations to our events',
            'Your name featured on our YouTube channel',
            'Reserved front-row seating at our events',
            'Priority booking for our events',
            'Three exclusive Zoom meetings per year with members of the Association’s Board and a special guest',
            'Participation in two dinners per year with the Boristene team and its guest of honour',
        ],
    },
    {
        'name': 'Patron — Mecenate', 'price': '€350', 'period': '/year',
        'subtitle': 'All benefits of the preceding levels, plus', 'kind': 'patron',
        'benefits': [
            'Exclusive events for Patrons and Grand Patrons, including private dinners at the Association founder’s home with special guests, and curated tours of Milan and across Italy exploring Ukrainian traces and their stories',
        ],
    },
    {
        'name': 'Grand Patron', 'price': '€500', 'period': '/year',
        'subtitle': 'All benefits of the preceding levels, plus', 'kind': 'patron',
        'benefits': [
            'The opportunity to contribute to the creation of our events and take an active role as a host or moderator',
        ],
    },
]

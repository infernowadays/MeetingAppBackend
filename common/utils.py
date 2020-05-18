from django.db.models import Q

from events.models import Request
from .models import *


def not_requested_events(queryset, user):
    ids = queryset.values_list('id', flat=True)
    requested_events = Request.objects.filter(event__in=ids, from_user=user).values_list('event', flat=True)

    return ~Q(id__in=requested_events)


def not_requested_tickets(queryset, user):
    ids = queryset.values_list('id', flat=True)

    return Q()


def filter_by_user_roles(list_roles, user):
    q = Q()
    if list_roles:
        for role in list_roles:
            if role == 'creator':
                q = q | Q(creator=user)
            elif role == 'member':
                q = q | Q(members=user)

    else:
        q = Q(~Q(creator=user) & ~Q(members=user))

    return q


def filter_by_categories(list_categories):
    if list_categories:
        categories = Category.objects.filter(name__in=list_categories).values_list('id', flat=True)
        return Q(categories__in=categories)
    else:
        return Q()

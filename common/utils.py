from django.db.models import Q

from events.models import Request, EventCategories
from tickets.models import TicketCategories
from token_auth.models import UserProfileCategories
from .models import *


def requested_events(user):
    requested_events = Request.objects.filter(from_user=user).values_list('event', flat=True)

    return Q(id__in=requested_events)


def ended_events(queryset, user):
    return Q(ended=True) & (Q(creator=user) | Q(members=user))


def not_ended_events(queryset, user):
    return Q(ended=False) & (Q(creator=user) | Q(members=user))


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


def set_event_categories(categories, instance):
    EventCategories.objects.filter(event=instance.id).delete()
    for string_category in categories:
        category = SubCategory.objects.filter(name=string_category.get('name'))
        category = category.get()
        EventCategories.objects.create(event=instance, category=category)


def set_ticket_categories(categories, instance):
    TicketCategories.objects.filter(ticket=instance.id).delete()
    for string_category in categories:
        category = SubCategory.objects.filter(name=string_category.get('name'))
        category = category.get()
        TicketCategories.objects.create(ticket=instance, category=category)


def set_user_profile_categories(categories, instance):
    UserProfileCategories.objects.filter(user_profile=instance.id).delete()
    for string_category in categories:
        category = SubCategory.objects.filter(name=string_category.get('name'))
        category = category.get()
        UserProfileCategories.objects.create(user_profile=instance, category=category)


def set_geo_point(geo_point, validated_data):
    geo_point.latitude = validated_data.get('geo_point').get('latitude')
    geo_point.longitude = validated_data.get('geo_point').get('longitude')
    geo_point.address = validated_data.get('geo_point').get('address')
    geo_point.save()

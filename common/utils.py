from datetime import date

import geopy.distance
from django.db.models import Q

from events.models import Event
from events.models import Request, EventCategories
from tickets.models import TicketCategories
from token_auth.models import UserProfileCategories, UserProfile
from .models import *


def not_answered_requests(user):
    not_answered_requests_ids = Request.objects.filter(from_user=user, decision="NO_ANSWER").values_list('event',
                                                                                                         flat=True)
    return Q(id__in=not_answered_requests_ids)


def not_requested_events(user):
    not_requested_events_ids = Request.objects.filter(from_user=user).values_list('event', flat=True)

    return ~Q(id__in=not_requested_events_ids)


def ended_events():
    return Q(ended=True)


def not_requested_tickets(queryset, user):
    ids = queryset.values_list('id', flat=True)

    return Q()


def taking_part(user):
    return Q(creator=user) | Q(members=user)


def not_taking_part(user):
    return ~Q(creator=user) & ~Q(members=user)


def filter_by_text(text):
    if text:
        return Q(description__icontains=text)
    else:
        return Q()


def filter_by_categories(list_categories):
    if list_categories:
        categories = SubCategory.objects.filter(name__in=list_categories).values_list('id', flat=True)
        return Q(categories__in=categories)
    else:
        return Q()


def filter_by_sex(sex_list):
    if sex_list:
        user_profiles_ids = UserProfile.objects.filter(sex__in=map(lambda x: x.upper(), sex_list)).values_list('id',
                                                                                                               flat=True)
        return Q(creator_id__in=user_profiles_ids)
    else:
        return Q()


def filter_by_geo(latitude, longitude, distance):
    if latitude and longitude and distance:
        events_ids = list([])
        for event in Event.objects.all():
            user = (float(latitude), float(longitude))
            place = (event.geo_point.latitude, event.geo_point.longitude)

            if geopy.distance.geodesic(user, place).km <= float(distance):
                events_ids.append(event.id)

        return Q(id__in=events_ids)

    else:
        return Q()


def filter_by_age(from_age, to_age):
    if from_age and to_age:
        user_profiles_ids = list([])
        for user_profile in UserProfile.objects.all():
            if user_profile.date_of_birth and int(from_age) < calculate_age(user_profile.date_of_birth) < int(to_age):
                user_profiles_ids.append(user_profile.id)

        return Q(creator_id__in=user_profiles_ids)
    else:
        return Q()


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


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

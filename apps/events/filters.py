import django_filters

from events.models import Event


class EventFilter(django_filters.FilterSet):
    area = django_filters.CharFilter(
        method='filter_by_area',
    )
    city = django_filters.CharFilter(
        method='filter_by_city',
    )
    category = django_filters.CharFilter(
        method='filter_by_category',
    )
    # age_limit = django_filters.NumberFilter(
    #     method='filter_by_age_limit'
    # )

    class Meta:
        model = Event
        fields = {
            'start_at': ['lte', 'gte'],
            'end_at': ['lte', 'gte'],
            'age_limit': ['lte', 'gte'],
        }

    def filter_by_area(self, queryset, name, value):
        return queryset.filter(area__name__icontains=value)

    def filter_by_city(self, queryset, name, value):
        return queryset.filter(area__city__icontains=value)

    def filter_by_category(self, queryset, name, value):
        return queryset.filter(category__name__icontains=value)

    def filter_by_age_limit(self, queryset, name, value):
        value = int(value)
        if name.endswith('gte'):
            return queryset.filter(age_limit__gte=value)
        elif name.endswith('lte'):
            return queryset.filter(age_limit__lte=value)

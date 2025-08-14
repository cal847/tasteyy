import django_filters
from django.db.models import Q
from .models import Recipe

class RecipeFilter(django_filters.FilterSet):
    """Filters for recipes"""

    #cooking time filters
    min_cooking_time = django_filters.NumberFilter(field_name="cooking_time", lookup_expr="gte")
    max_cooking_time = django_filters.NumberFilter(field_name="cooking_time", lookup_expr="lte")

    #category filter
    category = django_filters.CharFilter(field_name="category__name", lookup_expr="iexact")

    #diet filter
    diet = django_filters.CharFilter(field_name="diet__name", lookup_expr="iexact")

    #search
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Recipe
        fields = ["category", "diet", "min_cooking_time", "max_cooking_time", "search"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))

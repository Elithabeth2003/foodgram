from rest_framework.pagination import PageNumberPagination


class PaginatorWithLimit(PageNumberPagination):
    """Пагинатор с атрибутом лимита количества выведенных страниц."""

    page_size_query_param = 'limit'
    page_size = 10

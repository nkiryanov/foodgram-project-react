from rest_framework.pagination import PageNumberPagination


class FoodgramDefaultPagination(PageNumberPagination):
    page_size_query_param = "limit"

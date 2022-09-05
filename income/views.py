from django.shortcuts import render

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import IncomeSerializer
from .models import Income

from incomeexpensesapi.permissions import IsOwner
from incomeexpensesapi.renderers import DefaultRenderer

from datetime import date, timedelta

# Create your views here.

class IncomeList(generics.ListCreateAPIView):
    """
    Basic List/Create enpoint for `GET`/`POST` requests.
    """

    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Income.objects.all()

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

class IncomeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Basic Retrieve/Update/Delete for `GET`/`PUT`/`PATCH`/`DELETE` requests.
    """

    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Income.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

class IncomeAverages(APIView):
    """
    Collects all `Income` records related to current user, calculates average
    for each source of income, and issues a response with a number of records
    for each source and its total.
    """

    pagination_classes = None
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [DefaultRenderer]

    def get_average_for_source(self, qs, source):
        income = qs.filter(
            source=source,
        )
        avg = round(float(sum([i.amount for i in income]) / len(income)), 2)
        return avg

    def get(self, request):

        income_qs = Income.objects.filter(owner=request.user)

        sources = list(set([i.source for i in income_qs]))

        final = {entry:{'amount':self.get_average_for_source(income_qs, entry), 'records': income_qs.filter(
                    source=entry
                ).count()} for entry in sources}

        return Response(final, status=status.HTTP_200_OK)

class YearlyIncome(APIView):
    """
    Collects all `Income` records related to current user, filters them down to
    records within the last 365 days, and calculates total result for each source.
    """

    pagination_classes = None
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [DefaultRenderer]

    def get_total_for_source(self, queryset, source):
        return sum([i.amount for i in queryset.filter(source=source)])

    def get(self, request):

        income_qs = Income.objects.filter(owner=request.user)

        sources = list(set([i.source for i in income_qs]))

        today = date.today()
        year_ago = today - timedelta(days=365)

        income_within_year = income_qs.filter(
            date__lte=today,
            date__gte=year_ago
        )

        final = {entry:self.get_total_for_source(income_within_year, entry) for entry in sources}

        return Response(final, status=status.HTTP_200_OK)

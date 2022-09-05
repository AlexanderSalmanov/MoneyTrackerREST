from django.shortcuts import render

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from incomeexpensesapi.renderers import DefaultRenderer
from incomeexpensesapi.permissions import IsOwner

from .serializers import ExpenseSerializer

from .models import Expense

from datetime import datetime, date, timedelta

# Create your views here.

class ExpenseListAPIView(generics.ListCreateAPIView):
    """
    Endpoint for listing all `Expense` entries or creating new ones based on
    a request type (`GET`/`POST`).
    """

    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated,]
    queryset = Expense.objects.all()

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

class ExpenseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint for viewing single `Expense` entries, and also updating or deleting them.
    (`GET`/`PUT`/`PATCH`/`DELETE`)
    """

    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Expense.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class YearlyExpense(APIView):
    """
    Gets total `amount` spent on each `Expense` category within the last year.
    """

    permission_classes = [permissions.IsAuthenticated, ]
    renderer_classes = [DefaultRenderer, ]

    def get_category_items(self, items, category):
        return items.filter(category=category)

    def calculate_category_total(self, items):
        return sum([int(i.amount) for i in items])

    def get(self, request):

        today = date.today()
        year_ago = today - timedelta(days=365)

        qs = Expense.objects.filter(
            owner=request.user,
            date__gte=year_ago,
            date__lte=today
        )

        categories = list(set([i.category for i in qs]))

        final = {}

        for category in categories:
            items = self.get_category_items(qs, category)
            final[category] = self.calculate_category_total(items)

        return Response({
            'Summary': final
        }, status=status.HTTP_200_OK)


class CategoriesAverage(APIView):
    """
    Gets average money expenses (`amount`) for each `Expense` category.
    """

    permission_classes = [permissions.IsAuthenticated,]
    renderer_classes = [DefaultRenderer,]

    def get_category_average(self, queryset, category):
        qs = queryset.filter(
            category=category
        )

        avg = round(float(sum([i.amount for i in qs]) / len(qs)), 2)
        return avg

    def get(self, request):

        expenses = Expense.objects.filter(owner=request.user)
        categories = list(set([i.category for i in expenses]))

        final = {category:{category:self.get_category_average(expenses, category), 'records': expenses.filter(category=category).count()} for category in categories}

        return Response(final, status=status.HTTP_200_OK)

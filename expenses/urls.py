from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.ExpenseListAPIView.as_view(), name='list-create'),
    path('<int:id>/', views.ExpenseDetailAPIView.as_view(), name='single'),
    path('yearly-stats/', views.YearlyExpense.as_view(), name='yearly-stats'),
    path('category-averages/', views.CategoriesAverage.as_view(), name='category-averages')
]

from django.urls import path

from . import views

app_name = 'income'

urlpatterns = [
    path('', views.IncomeList.as_view(), name='list-create'),
    path('<int:id>/', views.IncomeDetail.as_view(), name='rud'),
    path('source-averages/', views.IncomeAverages.as_view(), name='source-averages'),
    path('yearly-stats/', views.YearlyIncome.as_view(), name='yearly-stats')
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.thesis_list, name='thesis_list'),
    path('add/', views.thesis_create, name='thesis_create'),
    path('<int:pk>/', views.thesis_detail, name='thesis_detail'),
    path('<int:pk>/delete/', views.thesis_delete, name='thesis_delete'),
    path('<int:pk>/report/', views.report_thesis, name='report_thesis'),
]

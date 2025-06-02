from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('create/', views.create_project, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_project, name='edit'),
    path('<int:pk>/delete/', views.delete_project, name='delete'),
    path('<int:project_id>/complete/', views.complete_project, name='complete_project'),
]
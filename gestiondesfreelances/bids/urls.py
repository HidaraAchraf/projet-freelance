from django.urls import path
from . import views

app_name = 'bids'

urlpatterns = [
    path('', views.bid_list, name='list'),
    path('create/<int:project_id>/', views.create_bid, name='create'),
    path('<int:bid_id>/', views.bid_detail, name='detail'),
    path('<int:bid_id>/edit/', views.edit_bid, name='edit'),
    path('<int:bid_id>/withdraw/', views.withdraw_bid, name='withdraw'),
    path('<int:bid_id>/manage/', views.manage_bid, name='manage'),
]
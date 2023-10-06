from django.urls import path
from .views import bot_view

urlpatterns = [
    path('new/', bot_view, name='bot_new'),
    path('<int:id>/', bot_view, name='bot_view'),
    path('', bot_view, name='bot_view'),
]


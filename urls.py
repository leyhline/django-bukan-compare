from django.urls import path

from . import views

urlpatterns = [
    path('', views.TitleList.as_view(), name='titles'),
    path('book/<int:title_id>', views.BookList.as_view(), name='books')
]
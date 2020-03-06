from django.urls import path

from . import views

urlpatterns = [
    path('', views.TitleList.as_view(), name='titles'),
    path('book/<int:pk>', views.TitlesBookList.as_view(), name='books'),
    path('page/<int:pk>', views.BookPagesView.as_view(), name='pages')
]
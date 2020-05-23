from django.urls import path

from . import views

urlpatterns = [
    path('', views.TitleList.as_view(), name='titles'),
    path('book/<int:pk>', views.TitlesBookList.as_view(), name='books'),
    path('pages/<int:pk>', views.BookPagesView.as_view(), name='pages'),
    path('page/<int:pk>', views.PageView.as_view(), name='page'),
    #path('match/<int:src_page_id>/<int:dst_page_id>', views.matching_image, name='match')
]
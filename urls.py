from django.urls import path

from . import views

urlpatterns = [
    path('', views.BookList.as_view(), name='books'),
    path('book/<int:pk>', views.BookPagesView.as_view(), name='pages'),
    path('page/<int:pk>', views.PageView.as_view(), name='page'),
    path('pagepair/<int:pk>', views.pagepair_json, name="pagepair"),
    path('bookpairs/<int:pk>', views.BookPairsView.as_view(), name='bookpairs'),
    path('bookpairs/<int:main>/<int:book1>/<int:book2>/<int:page>/<str:lr>', views.PagePairView.as_view(), name='pagepair')
]
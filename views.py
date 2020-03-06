from django.db.models import Count
from django.views import generic

from .models import Title, Book


class TitleList(generic.ListView):
    template_name = 'compare/titles.html'
    model = Title

    def get_queryset(self):
        return self.model.objects.annotate(nr_books=Count('book')).order_by('-nr_books')


class BookList(generic.ListView):
    template_name = 'compare/books.html'
    model = Book
    
    def get_queryset(self):
        return self.model.objects.filter(title_id=self.kwargs['title_id'])

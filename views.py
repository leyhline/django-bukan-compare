from django.db.models import Count
from django.views import generic

from .models import Title, Book


class TitleList(generic.ListView):
    template_name = 'compare/titles.html'
    model = Title
    queryset = Title.objects.annotate(nr_books=Count('book')).order_by('-nr_books')


class TitlesBookList(generic.DetailView):
    template_name = 'compare/books.html'
    model = Title


class BookPagesView(generic.DetailView):
    template_name = 'compare/pages.html'
    model = Book

    def get_context_data(self, **kwargs):
        book = super().get_object()
        context = super().get_context_data(**kwargs)
        template = "{book_id}/{book_id}_{page:0>5}_{lr}.jpg"
        images = []
        for page_nr in range(1, book.nr_scans+1):
            if book.pages_per_scan == 2:
                images.append(template.format(book_id=book.id, page=page_nr, lr=2))
                images.append(template.format(book_id=book.id, page=page_nr, lr=1))
            else:
                images.append(template.format(book_id=book.id, page=page_nr, lr=0))
        context['images'] = images
        return context    

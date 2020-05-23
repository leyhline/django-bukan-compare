from django.db.models import Count, Q
from django.views import generic
from django.http import FileResponse
from django.contrib.staticfiles import finders

from .models import Book, Page, Pagepair


THUMB_TEMPLATE = "thumb/{book_id}/{filename}"
IMAGE_TEMPLATE = "image/{book_id}/{filename}"
THRESHOLD_NR_KEYPOINTS = 20


class BookList(generic.ListView):
    template_name = 'compare/books.html'
    model = Book


class BookPagesView(generic.DetailView):
    template_name = 'compare/pages.html'
    model = Book

    def get_context_data(self, **kwargs):
        book = super().get_object()
        context = super().get_context_data(**kwargs)
        pages = book.page_set.all()
        context['pages'] = [(page, THUMB_TEMPLATE.format(
            book_id=book.id, filename=page.filename)) for page in pages]
        return context


class PageView(generic.DetailView):
    template_name = 'compare/page.html'
    model = Page

    def get_context_data(self, **kwargs):
        page = super().get_object()
        context = super().get_context_data(**kwargs)
        context['matches'] = Pagepair.objects.filter(Q(first_page=page) | Q(second_page=page)).filter(nr_matches__gt=0)
        context['url'] = IMAGE_TEMPLATE.format(
            book_id=page.book_id, filename=page.filename)
        book_pages = Page.objects.filter(book=page.book)
        try:
            context['previous'] = book_pages.get(id=page.id-1)
        except Page.DoesNotExist:
            context['previous'] = None
        try:
            context['next'] = book_pages.get(id=page.id+1)
        except Page.DoesNotExist:
            context['next'] = None
        return context

from django.db.models import Q
from django.views import generic
from django.http import JsonResponse

from .models import Book, Page, Pagepair


THUMB_TEMPLATE = "compare/thumb/{book_id}/{filename}"
IMAGE_TEMPLATE = "compare/image/{book_id}/{filename}"
THRESHOLD_NR_KEYPOINTS = 30


class BookList(generic.ListView):
    template_name = 'compare/books.html'
    queryset = Book.objects.order_by('-id')


class BookPagesView(generic.DetailView):
    template_name = 'compare/pages.html'
    model = Book

    def get_context_data(self, **kwargs):
        book = super().get_object()
        context = super().get_context_data(**kwargs)
        pages = book.page_set.order_by('page', '-lr')
        context['pages'] = [
            (page, THUMB_TEMPLATE.format(book_id=book.id, filename=page.filename))
            for page in pages]
        return context


class PageView(generic.DetailView):
    template_name = 'compare/page.html'
    model = Page

    def get_context_data(self, **kwargs):
        page = super().get_object()
        context = super().get_context_data(**kwargs)
        context['matches'] = Pagepair.objects.filter(Q(first_page=page) | Q(second_page=page)).filter(nr_matches__gt=THRESHOLD_NR_KEYPOINTS).order_by('-nr_matches')
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


def pagepair_json(request, pk):
    pp = Pagepair.objects.get(pk=pk)
    return JsonResponse({
        'first': pp.first_page.filename,
        'second': pp.second_page.filename,
        'homography': [pp.h11, pp.h12, pp.h13, pp.h21, pp.h22, pp.h23, pp.h31, pp.h32, pp.h33],
        'firstbook': pp.first_page.book_id,
        'secondbook': pp.second_page.book_id,
        'firstpage': pp.first_page.page,
        'secondpage': pp.second_page.page
    })

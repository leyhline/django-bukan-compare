from operator import itemgetter
from django.db.models import Q, Count
from django.views.generic import TemplateView, DetailView, ListView
from django.http import JsonResponse

from .models import Book, Page, Pagepair


THUMB_TEMPLATE = "compare/thumb/{book_id}/{filename}"
IMAGE_TEMPLATE = "compare/image/{book_id}/{filename}"
THRESHOLD_NR_KEYPOINTS = 30
THRESHOLD_NR_PAGES = 6


class BookList(ListView):
    template_name = 'compare/books.html'
    queryset = Book.objects.order_by('-id')


class BookPagesView(DetailView):
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


class BookPairsView(DetailView):
    template_name = 'compare/bookpairs.html'
    model = Book

    def get_context_data(self, **kwargs):
        book = super().get_object()
        context = super().get_context_data(**kwargs)
        bookpairs12 = (Pagepair.objects
            .filter(Q(first_page__book=book))
            .filter(nr_matches__gt=THRESHOLD_NR_KEYPOINTS)
            .values('second_page__book')
            .annotate(nr_pages=Count('id'))
            .filter(nr_pages__gt=THRESHOLD_NR_PAGES))
        bookpairs21 = (Pagepair.objects
            .filter(second_page__book=book)
            .filter(nr_matches__gt=THRESHOLD_NR_KEYPOINTS)
            .values('first_page__book')
            .annotate(nr_pages=Count('id'))
            .filter(nr_pages__gt=THRESHOLD_NR_PAGES))
        bookpairs = (
            [(1, Book.objects.get(pk=book.id), Book.objects.get(pk=obj['second_page__book']), obj['nr_pages']) for obj in bookpairs12] + 
            [(2, Book.objects.get(pk=obj['first_page__book']), Book.objects.get(pk=book.id), obj['nr_pages']) for obj in bookpairs21])
        bookpairs.sort(key=itemgetter(3), reverse=True)
        context['bookpairs'] = bookpairs
        return context


class PageView(DetailView):
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


class PagePairView(TemplateView):
    template_name = "compare/pagepair.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book1 = Book.objects.get(pk=context['book1'])
        book2 = Book.objects.get(pk=context['book2'])
        if context['main'] == 1:
            page1 = Page.objects.get(book=book1, page=context['page'], lr=context['lr'].encode())
            pp = Pagepair.objects.filter(first_page=page1, second_page__book_id=book2).order_by('-nr_matches')[0]
            page2 = pp.second_page
            page = page1
        elif context['main'] == 2:
            page2 = Page.objects.get(book=book2, page=context['page'], lr=context['lr'].encode())
            pp = Pagepair.objects.filter(second_page=page2, first_page__book_id=book1).order_by('-nr_matches')[0]
            page1 = pp.first_page
            page = page2
        book_pages = Page.objects.filter(book=page.book)
        try:
            context['previous'] = book_pages.get(id=page.id-1)
        except Page.DoesNotExist:
            context['previous'] = None
        try:
            context['next'] = book_pages.get(id=page.id+1)
        except Page.DoesNotExist:
            context['next'] = None
        url1 = IMAGE_TEMPLATE.format(book_id=book1.id, filename=page1.filename)
        url2 = IMAGE_TEMPLATE.format(book_id=book2.id, filename=page2.filename)
        context['book1'] = book1
        context['book2'] = book2
        context['book1page'] = page1
        context['book2page'] = page2
        context['book1pageurl'] = url1
        context['book2pageurl'] = url2
        homography = [pp.h11, pp.h12, pp.h13, pp.h21, pp.h22, pp.h23, pp.h31, pp.h32, pp.h33]
        if any(x is None for x in homography):
            context['homography'] = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        else:
            context['homography'] = homography
        return context

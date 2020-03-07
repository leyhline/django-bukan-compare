from django.db.models import Count
from django.views import generic

from .models import Title, Book, Page


PAGE_FILENAME_TEMPLATE = "{book_id}/{book_id}_{page:0>5}_{lr}.jpg"


class TitleList(generic.ListView):
    template_name = 'compare/titles.html'
    model = Title
    queryset = Title.objects.annotate(nr_books=Count('book')).order_by('-nr_books')


class TitlesBookList(generic.DetailView):
    template_name = 'compare/books.html'
    model = Title


def get_filename_page_tuple(pages, book_id, page_nr, lr):
    filename = PAGE_FILENAME_TEMPLATE.format(book_id=book_id, page=page_nr, lr=lr)
    try:
        page = pages.get(page=page_nr, lr=lr)
    except Page.DoesNotExist:
         page = None
    return (filename, page)


class BookPagesView(generic.DetailView):
    template_name = 'compare/pages.html'
    model = Book

    def get_context_data(self, **kwargs):
        book = super().get_object()
        context = super().get_context_data(**kwargs)
        pages = book.page_set.all()
        images = []
        for page_nr in range(1, book.nr_scans+1):
            if book.pages_per_scan == 2:
                images.append(get_filename_page_tuple(pages, book.id, page_nr, 2))
                images.append(get_filename_page_tuple(pages, book.id, page_nr, 1))
            else:
                images.append(get_filename_page_tuple(pages, book.id, page_nr, 0))
        context['images'] = images
        return context


class PageView(generic.DetailView):
    template_name = 'compare/page.html'
    model = Page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = super().get_object()
        src_to_dst = (page.keypoint_set
            .values_list('match_src__dst_keypoint__page')
            .distinct()
            .exclude(match_src__dst_keypoint__page=None)
            .annotate(count=Count('match_src')))
        dst_to_src = (page.keypoint_set
            .values_list('match_dst__src_keypoint__page')
            .distinct()
            .exclude(match_dst__src_keypoint__page=None)
            .annotate(count=Count('match_dst')))
        union = src_to_dst.union(dst_to_src).order_by('-count')
        context['matching'] = union
        context['filename'] = PAGE_FILENAME_TEMPLATE.format(book_id=page.book_id, page=page.page, lr=page.lr)
        return context

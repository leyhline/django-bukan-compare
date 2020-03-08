from django.db.models import Count
from django.views import generic
from django.http import FileResponse
from django.contrib.staticfiles import finders

from .models import Title, Book, Page, Match

import io
import cv2 as cv
import numpy as np


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


def get_keypoints(src_page: Page, dst_page: Page):
    src_dst_matches = Match.objects.filter(src_keypoint__page=src_page).filter(dst_keypoint__page=dst_page)
    dst_src_matches = Match.objects.filter(src_keypoint__page=dst_page).filter(dst_keypoint__page=src_page)
    src_dst_count = src_dst_matches.count()
    dst_src_count = dst_src_matches.count()
    assert (src_dst_count == 0) or (dst_src_count == 0)
    assert (src_dst_count > 0) or (dst_src_count > 0)
    if src_dst_count != 0:
        return src_dst_matches.values_list('src_keypoint__x', 'src_keypoint__y', 'dst_keypoint__x', 'dst_keypoint__y')
    else:
        return dst_src_matches.values_list('dst_keypoint__x', 'dst_keypoint__y', 'src_keypoint__x', 'src_keypoint__y')


def matching_image(response, src_page_id, dst_page_id):
    src_page = Page.objects.get(pk=src_page_id)
    dst_page = Page.objects.get(pk=dst_page_id)
    dst_filename = PAGE_FILENAME_TEMPLATE.format(book_id=dst_page.book_id, page=dst_page.page, lr=dst_page.lr)
    dst_path = finders.find('images/' + dst_filename)
    dst_image = cv.imread(dst_path, cv.IMREAD_GRAYSCALE)
    keypoints = np.array(get_keypoints(src_page, dst_page))
    homography, _ = cv.findHomography(keypoints[:,2:], keypoints[:,:2], 0)
    height, width = dst_image.shape
    dst_image_warped = cv.warpPerspective(dst_image, homography, (width, height))
    enc_result, dst_image_warped_jpg = cv.imencode(".jpg", dst_image_warped, [cv.IMWRITE_JPEG_QUALITY, 80, cv.IMWRITE_JPEG_OPTIMIZE, True])
    assert enc_result
    r = FileResponse(io.BytesIO(dst_image_warped_jpg))
    r['Content-Disposition'] = f'inline; filename="{dst_filename}"'
    r['Content-Type'] = 'image/jpeg'
    r['Content-Length'] = len(dst_image_warped_jpg)
    return r

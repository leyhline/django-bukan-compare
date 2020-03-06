from django.db import models


class Title(models.Model):
    kanji = models.CharField(max_length=50, unique=True)
    hiragana = models.CharField(max_length=50)
    romanji = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.kanji} ({self.romanji})"


class Book(models.Model):
    ASPECT_CHOICES = [
        ('LA', 'Landscape'),
        ('PO', 'Portrait')
    ]

    id = models.PositiveIntegerField(primary_key=True)
    released = models.CharField(max_length=6)
    classification = models.CharField(max_length=50)
    title = models.ForeignKey(Title, on_delete=models.PROTECT)
    original_id = models.CharField(max_length=20)
    published = models.CharField(max_length=10)
    published_ad = models.CharField(max_length=10)
    nr_books = models.PositiveIntegerField(null=True, blank=True)
    pages_per_scan = models.PositiveSmallIntegerField()
    aspect = models.CharField(max_length=2, choices=ASPECT_CHOICES)
    nr_scans = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}/{self.original_id} ({self.nr_scans} scans)"


class Page(models.Model):
    LR_CHOICES = [
        (0, 'whole'),
        (1, 'right'),
        (2, 'left')
    ]

    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    page = models.PositiveIntegerField()
    lr = models.PositiveSmallIntegerField(choices=LR_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['book', 'page', 'lr'], name='unique_page')
        ]


class Keypoint(models.Model):
    page = models.ForeignKey(Page, on_delete=models.PROTECT)
    feature = models.PositiveIntegerField()
    x = models.FloatField()
    y = models.FloatField()
    size = models.FloatField()
    angle = models.FloatField()
    response = models.FloatField()
    octave = models.PositiveSmallIntegerField()
    class_id = models.PositiveSmallIntegerField()
    descriptor = models.BinaryField(max_length=61)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['page', 'feature'], name='unique_keypoint')
        ]


class Match(models.Model):
    src_keypoint = models.ForeignKey(Keypoint, on_delete=models.PROTECT, related_name='match_src')
    dst_keypoint = models.ForeignKey(Keypoint, on_delete=models.PROTECT, related_name='match_dst')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['src_keypoint', 'dst_keypoint'], name='unique_match')
        ]

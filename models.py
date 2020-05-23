from django.db import models


class Title(models.Model):
    kanji = models.CharField(unique=True, max_length=50)
    hiragana = models.CharField(max_length=50)
    romanji = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'title'

    def __str__(self):
        return f"{self.kanji} ({self.romanji})"    


class Book(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    released = models.DateField()
    title = models.ForeignKey(Title, models.PROTECT)
    original_id = models.CharField(max_length=20)
    era_name = models.CharField(max_length=2)
    era_year = models.PositiveIntegerField(blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    estimate = models.IntegerField(blank=True, null=True)
    nr_books = models.PositiveIntegerField(blank=True, null=True)
    pages_per_scan = models.PositiveIntegerField()
    aspect = models.BinaryField(max_length=1)
    nr_scans = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'book'

    def __str__(self):
        return f"{self.id}/{self.original_id} ({self.nr_scans} scans)"


class Page(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    book = models.ForeignKey(Book, models.PROTECT)
    page = models.PositiveIntegerField()
    lr = models.BinaryField(max_length=1)
    filename = models.CharField(max_length=21, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'page'
        constraints = [
            models.UniqueConstraint(fields=['book', 'page', 'lr'], name='unique_page')
        ]


class Feature(models.Model):
    id = models.BigIntegerField(primary_key=True)
    page = models.ForeignKey(Page, models.PROTECT)
    feature_nr = models.PositiveIntegerField()
    x = models.FloatField()
    y = models.FloatField()
    size = models.FloatField()
    angle = models.FloatField()
    response = models.FloatField()
    octave = models.PositiveIntegerField()
    class_id = models.PositiveIntegerField()
    descriptor = models.BinaryField(max_length=61)

    class Meta:
        managed = False
        db_table = 'feature'
        constraints = [
            models.UniqueConstraint(fields=['page', 'feature'], name='unique_feature')
        ]


class Match(models.Model):
    id = models.BigIntegerField(primary_key=True)
    src_feature = models.ForeignKey(Feature, models.PROTECT, related_name='src_match')
    dst_feature = models.ForeignKey(Feature, models.PROTECT, related_name='dst_match')

    class Meta:
        managed = False
        db_table = 'dmatch'
        constraints = [
            models.UniqueConstraint(fields=['src_feature', 'dst_feature'], name='unique_match')
        ]


class Pagepair(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_page = models.ForeignKey(Page, models.PROTECT, related_name='first_pagepair')
    second_page = models.ForeignKey(Page, models.PROTECT, related_name='second_pagepair')
    nr_matches = models.PositiveIntegerField()
    h11 = models.FloatField(blank=True, null=True)
    h12 = models.FloatField(blank=True, null=True)
    h13 = models.FloatField(blank=True, null=True)
    h21 = models.FloatField(blank=True, null=True)
    h22 = models.FloatField(blank=True, null=True)
    h23 = models.FloatField(blank=True, null=True)
    h31 = models.FloatField(blank=True, null=True)
    h32 = models.FloatField(blank=True, null=True)
    h33 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pagepair'
        constraints = [
            models.UniqueConstraint(fields=['first_page', 'second_page'], name='unique_pagepair')
        ]

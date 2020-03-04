# Generated by Django 3.0.3 on 2020-02-29 01:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('released', models.CharField(max_length=6)),
                ('classification', models.CharField(max_length=50)),
                ('original_id', models.CharField(max_length=20)),
                ('published', models.CharField(max_length=10)),
                ('published_ad', models.CharField(max_length=10)),
                ('nr_books', models.PositiveIntegerField(blank=True, null=True)),
                ('pages_per_scan', models.PositiveSmallIntegerField()),
                ('aspect', models.CharField(choices=[('LA', 'Landscape'), ('PO', 'Portrait')], max_length=2)),
                ('nr_scans', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Keypoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature', models.PositiveIntegerField()),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('size', models.FloatField()),
                ('angle', models.FloatField()),
                ('response', models.FloatField()),
                ('octave', models.PositiveSmallIntegerField()),
                ('class_id', models.PositiveSmallIntegerField()),
                ('descriptor', models.BinaryField(max_length=61)),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kanji', models.CharField(max_length=50, unique=True)),
                ('hiragana', models.CharField(max_length=50)),
                ('romanji', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.PositiveIntegerField()),
                ('lr', models.PositiveSmallIntegerField(choices=[(0, 'whole'), (1, 'right'), (2, 'left')])),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='compare.Book')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dst_keypoint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='match_dst', to='compare.Keypoint')),
                ('src_keypoint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='match_src', to='compare.Keypoint')),
            ],
        ),
        migrations.AddField(
            model_name='keypoint',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='compare.Page'),
        ),
        migrations.AddField(
            model_name='book',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='compare.Title'),
        ),
        migrations.AddConstraint(
            model_name='page',
            constraint=models.UniqueConstraint(fields=('book', 'page', 'lr'), name='unique_page'),
        ),
        migrations.AddConstraint(
            model_name='match',
            constraint=models.UniqueConstraint(fields=('src_keypoint', 'dst_keypoint'), name='unique_match'),
        ),
        migrations.AddConstraint(
            model_name='keypoint',
            constraint=models.UniqueConstraint(fields=('page', 'feature'), name='unique_keypoint'),
        ),
    ]
